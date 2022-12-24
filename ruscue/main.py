import asyncio
import logging
import os
import time

from gql import gql, Client
from gql.transport.websockets import WebsocketsTransport

logging.basicConfig(level=logging.INFO)
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

    if state != 'PRESSED':
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


async def main():
    transport = WebsocketsTransport(url='ws://%s/subscriptions' % (os.environ.get("RUSTY_IP_PORT", "127.0.0.1:8080")),
                                    connect_args={"ping_interval": None}
                                    )
    client = Client(
        transport=transport,
        fetch_schema_from_transport=False
    )
    session = await client.connect_async(reconnecting=True)

    async for data in session.subscribe(gql_operations, operation_name="OnButtonChange"):
        event = data['buttonChange']
        await handle_key_press(session, event['button'], event['state'])


asyncio.run(main())
