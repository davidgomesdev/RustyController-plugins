import asyncio
import json
import time
from asyncio import CancelledError
from enum import Enum
from typing import Any

import pytimeparse
from common.graphql_utils import subscribe_server, connect_graphql
from common.logger_utils import setup_logger
from gql import gql


class BrewModeState(Enum):
    INACTIVE = 1,
    SELECTING = 2,
    CONFIGURING = 3,
    BREWING = 4,
    BREWED = 5,
    CANCELLING = 6


logger = setup_logger("brewertender")

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

mutation TeaSelected($name: String!, $hue: Int!, $saturation: Float!, $value: Float!) {
    setLedBreathing(input: {
        name: $name,
        hue: $hue,
        saturation: $saturation,
        initialValue: 0.0,
        peak: $value,
        timeToPeak: 300
    })
}

mutation BrewFinished($timeout: Int!) {
    setLedBreathing(input: {
        hue: 0,
        saturation: 1.0,
        initialValue: 0.0,
        timeToPeak: 3000,
        peak: 0.3,
        duration: $timeout
    })
    setRumbleStatic(input: {
        strength: 1.0,
        duration: $timeout
    })
}

mutation WaitingForSelection {
    setLedBreathing(input: {
        hue: 0,
        saturation: 0.0,
        initialValue: 0.6,
        timeToPeak: 300,
        peak: 0.8
    })
}

mutation ChangedConfiguration($duration: Int!) {
    setRumbleBlink(input: {
        strength: 0.35,
        interval: 250,
        duration: $duration
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

START_SELECTION_TIMEOUT_SECS = 3
START_BREW_TIMEOUT_SECS = 10
CANCEL_TIMEOUT_SECS = 3
ACKNOWLEDGE_BREW_TIMEOUT_SECS = 10

HIGHEST_SECOND_PRESS_TIMEOUT = max(CANCEL_TIMEOUT_SECS, START_SELECTION_TIMEOUT_SECS)

last_move_press = time.time() - HIGHEST_SECOND_PRESS_TIMEOUT
brew_mode_state = BrewModeState.INACTIVE

chosen_tea: Any = None
chosen_timing_index = 0

brew_task = None
finished_brew_at = 0

with open('config.json', 'r') as teasFile:
    tea_config = json.load(teasFile)


async def brew_tea(session, tea, brew_time):
    global brew_task, brew_mode_state, finished_brew_at

    color = tea['color']
    brew_time_secs = pytimeparse.parse(brew_time)

    try:
        await session.execute(gql_operations, operation_name="BrewTea",
                              variable_values={
                                  "name": f'{tea["name"]}-{brew_time}',
                                  "hue": color['hue'],
                                  "saturation": color['saturation'],
                                  "value": color['value'],
                                  "duration": brew_time_secs * 1_000,
                              })
        await asyncio.sleep(brew_time_secs)
    except CancelledError:
        logger.info("Brew task cancelled.")
        return

    logger.info("Finished brew for '" + tea['name'] + "' tea")
    await session.execute(gql_operations, operation_name="BrewFinished",
                          variable_values={
                              "timeout": ACKNOWLEDGE_BREW_TIMEOUT_SECS * 1_000
                          })
    brew_mode_state = BrewModeState.BREWED
    brew_task = None
    finished_brew_at = time.time()


async def handle_key_press(session, button, state):
    global last_move_press, brew_mode_state, brew_task, chosen_tea, chosen_timing_index, finished_brew_at

    now = time.time()
    secs_since_selection_press = now - last_move_press

    if state == 'RELEASED':
        return

    if button == 'START':
        if brew_mode_state is BrewModeState.CONFIGURING:
            timings = chosen_tea['timings']
            brew_time = timings[chosen_timing_index % len(timings)]

            logger.info("Starting brew task of '" + chosen_tea['name'] + "' for '" + brew_time + "'")
            brew_task = asyncio.create_task(brew_tea(session, chosen_tea, brew_time))
            brew_mode_state = BrewModeState.BREWING

        return

    if button == 'SELECT':
        if brew_mode_state is BrewModeState.CONFIGURING:
            logger.info("Changing to next timing")
            chosen_timing_index += 1

            await session.execute(gql_operations, operation_name="ChangedConfiguration",
                                  variable_values={
                                      "duration": 250 * (chosen_timing_index % len(chosen_tea['timings']) + 1)
                                  })

        return

    if button == 'MOVE':
        last_move_press = now

        if brew_mode_state is BrewModeState.CANCELLING and \
                secs_since_selection_press > CANCEL_TIMEOUT_SECS:
            logger.debug("Got press after cancel time out, handling as normal")
            brew_mode_state = BrewModeState.BREWING
            return

        if brew_mode_state is BrewModeState.SELECTING and \
                secs_since_selection_press > START_BREW_TIMEOUT_SECS:
            logger.debug("Selection timed out, handling as new")
            brew_mode_state = BrewModeState.INACTIVE

        if brew_mode_state is BrewModeState.BREWED:
            secs_since_brew = time.time() - finished_brew_at

            if secs_since_brew <= ACKNOWLEDGE_BREW_TIMEOUT_SECS:
                await session.execute(gql_operations, operation_name="CancelledStep")

                logger.info("Stopped brew finish")
                brew_mode_state = BrewModeState.INACTIVE
                last_move_press = now - HIGHEST_SECOND_PRESS_TIMEOUT
                return

            logger.debug("Got move press after the brew timed out, handling as a normal press...")
            brew_mode_state = BrewModeState.INACTIVE

        if brew_mode_state is BrewModeState.SELECTING or brew_mode_state is BrewModeState.CONFIGURING:
            await session.execute(gql_operations, operation_name="CancelledStep")

            logger.info("Cancelled selection/configuration phase")
            brew_mode_state = BrewModeState.INACTIVE
            last_move_press = now - HIGHEST_SECOND_PRESS_TIMEOUT
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
            last_move_press = now - HIGHEST_SECOND_PRESS_TIMEOUT
            return

        is_selection_second_press = secs_since_selection_press <= START_SELECTION_TIMEOUT_SECS

        if not is_selection_second_press:
            return

        brew_mode_state = BrewModeState.SELECTING

        await session.execute(gql_operations, operation_name="WaitingForSelection")
        logger.info("Waiting for selection...")

    if brew_mode_state is BrewModeState.SELECTING and \
            button in ['CIRCLE', 'CROSS', 'TRIANGLE', 'SQUARE']:
        chosen_tea = tea_config.get(button.lower())

        if chosen_tea is None:
            logger.warning("Button selected '" + button + "' has no timings config.")

            await session.execute(gql_operations, operation_name="SelectionNotFound")

            brew_mode_state = BrewModeState.INACTIVE
            return

        logger.info("Tea '" + chosen_tea['name'] + "' selected")

        color = chosen_tea['color']

        await session.execute(gql_operations, operation_name="TeaSelected",
                              variable_values={
                                  "name": chosen_tea['name'],
                                  "hue": color['hue'],
                                  "saturation": color['saturation'],
                                  "value": color['value']
                              })

        brew_mode_state = BrewModeState.CONFIGURING
        chosen_timing_index = chosen_tea.get('common', 0)

        logger.debug("Entered configuration phase")


async def event_handler(session, event):
    event = event['buttonChange']
    await handle_key_press(session, event['button'], event['state'])


async def main():
    session = await connect_graphql()
    logger.info("Connected to server")
    await subscribe_server(session, gql_operations, operation_name="onButtonChange", event_handler=event_handler)


asyncio.run(main())
