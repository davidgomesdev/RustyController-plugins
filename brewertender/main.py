import asyncio
import logging
import time
from asyncio import CancelledError
from enum import Enum

from gql import gql, Client
from gql.transport.websockets import WebsocketsTransport
import json
import os


class BrewModeState(Enum):
    INACTIVE = 1,
    INITIATING = 2,
    BREWING = 3,
    BREWED = 4,
    CANCELLING = 5


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("current.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("brewertender")
logger.setLevel(logging.DEBUG)

gql_operations = gql("""
subscription onButtonChange {
    buttonChange {button, state}
}

mutation BrewTea($name: String!, $hue: Int!, $saturation: Float!, $value: Float!, $duration: Int!) {
    setLedBreathing(input: {
        name: $name,
        hue: $hue,
        saturation: $saturation,
        initialValue: 0.0,
        peak: $value,
        timeToPeak: 3000,
        duration: $duration
    })
}

mutation BrewFinished {
    setLedBreathing(input: {
        hue: 0,
        saturation: 1.0,
        initialValue: 0.0,
        timeToPeak: 3000,
        peak: 0.3,
        duration: 10000
    })
    setRumbleStatic(input: {
        strength: 1.0
    })
}

mutation WaitingForSelection {
    setLedBreathing(input: {
        hue: 0,
        saturation: 0.0,
        initialValue: 0.6,
        timeToPeak: 300,
        peak: 0.8,
        duration: 10000
    })
}

mutation SelectionNotFound {
    setLedBlink(input: {
        hue: 0,
        saturation: 1.0,
        value: 0.4,
        interval: 400,
        duration: 1000
    })
}

mutation CancelledStep {
    setLedOff
    setRumbleOff
}
""")
START_SELECTION_TIMEOUT_SECS = 3.0
START_BREW_TIMEOUT_SECS = 10.0
CANCEL_TIMEOUT_SECS = 3.0

last_move_press = time.time()
brew_mode_state = BrewModeState.INACTIVE

brew_task = None

with open('config.json', 'r') as teasFile:
    tea_config = json.load(teasFile)


async def brew_tea(session, chosen_tea):
    global brew_task, brew_mode_state

    color = chosen_tea['color']
    timing_index = chosen_tea.get('common', 0)
    brew_time = chosen_tea['timings'][timing_index]

    try:
        await session.execute(gql_operations, operation_name="BrewTea",
                              variable_values={
                                  "name": chosen_tea['name'],
                                  "hue": color['hue'],
                                  "saturation": color['saturation'],
                                  "value": color['value'],
                                  "duration": brew_time * 1_000,
                              })
        await asyncio.sleep(brew_time)
    except CancelledError:
        logger.info("Brew task cancelled.")
        return

    logger.info("Finished brew")
    await session.execute(gql_operations, operation_name="BrewFinished")
    brew_mode_state = BrewModeState.BREWED
    brew_task = None


async def handle_key_press(session, button, state):
    global last_move_press, brew_mode_state, brew_task

    now = time.time()
    secs_since_selection_press = now - last_move_press

    if state != 'RELEASED':
        return

    if button == 'MOVE':
        last_move_press = now

        if brew_mode_state is BrewModeState.CANCELLING and \
                secs_since_selection_press > CANCEL_TIMEOUT_SECS:
            logger.debug("Got press after cancel time out, handling as normal")
            brew_mode_state = BrewModeState.BREWING
            return

        if brew_mode_state is BrewModeState.INITIATING and \
                secs_since_selection_press > START_BREW_TIMEOUT_SECS:
            logger.debug("Selection timed out, handling as new")
            brew_mode_state = BrewModeState.INACTIVE

        if brew_mode_state is BrewModeState.BREWED:
            await session.execute(gql_operations, operation_name="CancelledStep")

            logger.info("Stopped brew finish")
            brew_mode_state = BrewModeState.INACTIVE
            return

        if brew_mode_state is BrewModeState.INITIATING:
            await session.execute(gql_operations, operation_name="CancelledStep")

            logger.info("Cancelled selection")
            brew_mode_state = BrewModeState.INACTIVE
            return

        if brew_mode_state is BrewModeState.BREWING:
            logger.debug("Got a possible cancel brewing request...")
            brew_mode_state = BrewModeState.CANCELLING
            return

        if brew_mode_state is BrewModeState.CANCELLING:
            await session.execute(gql_operations, operation_name="CancelledStep")

            if brew_task is not None:
                brew_task.cancel()
                brew_task = None

            logger.info("Cancelled brew")
            brew_mode_state = BrewModeState.INACTIVE
            return

        is_selection_second_press = secs_since_selection_press <= START_SELECTION_TIMEOUT_SECS

        if not is_selection_second_press:
            return

        brew_mode_state = BrewModeState.INITIATING

        await session.execute(gql_operations, operation_name="WaitingForSelection")
        logger.info("Waiting for selection...")

    if brew_mode_state is BrewModeState.INITIATING and \
            button in ['CIRCLE', 'CROSS', 'TRIANGLE', 'SQUARE']:
        chosen_tea = tea_config.get(button.lower())

        if chosen_tea is None:
            logger.warning("Button selected '" + button + "' has no timings config.")

            await session.execute(gql_operations, operation_name="SelectionNotFound")

            brew_mode_state = BrewModeState.INACTIVE
            return

        logger.info("Starting brew task")
        brew_task = asyncio.create_task(brew_tea(session, chosen_tea))
        brew_mode_state = BrewModeState.BREWING


async def main():
    transport = WebsocketsTransport(url='ws://%s/subscriptions' % (os.environ.get("RUSTY_IP_PORT", "127.0.0.1:8080")),
                                    connect_args={"ping_interval": None}
                                    )
    client = Client(
        transport=transport,
        fetch_schema_from_transport=False
    )
    session = await client.connect_async(reconnecting=True)

    async for data in session.subscribe(gql_operations, operation_name="onButtonChange"):
        event = data['buttonChange']
        await handle_key_press(session, event['button'], event['state'])


asyncio.run(main())
