import asyncio
import logging
import time

from common.graphql_utils import connect_graphql, subscribe_server
from gql import gql

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("current.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ruscue")
logger.setLevel(logging.DEBUG)

gql_operations = gql("""
subscription OnButtonChange {
    buttonChange {
        button,
        state
    }
}

mutation SetAllOff {
    setLedOff
    setRumbleOff
}
""")
PRESS_INTERVAL = 3.0

last_start_press = None
last_select_press = None


async def handle_key_press(session, button, state):
    global last_start_press, last_select_press
    now = time.time()

    if state == 'RELEASED':
        if button == 'START':
            last_start_press = None

        if button == 'SELECT':
            last_select_press = None
        return

    if button == 'START':
        last_start_press = now

    if button == 'SELECT':
        last_select_press = now

    if None in [last_start_press, last_select_press]:
        return

    secs_since_both_press = abs(last_start_press - last_select_press)

    if secs_since_both_press <= PRESS_INTERVAL:
        await session.execute(gql_operations, operation_name="SetAllOff")
        logger.info("Rescued the day!")
        last_start_press = None
        last_select_press = None


async def event_handler(session, event):
    event = event['buttonChange']
    await handle_key_press(session, event['button'], event['state'])

async def main():
    session = await connect_graphql()
    logger.info("Connected to server")
    await subscribe_server(session, gql_operations,operation_name="OnButtonChange", event_handler=event_handler)


asyncio.run(main())
