import asyncio
import logging
import time

from common.graphql_utils import connect_graphql, subscribe_server
from gql import gql

from common.logger_utils import setup_logger
from gql.client import ReconnectingAsyncClientSession, AsyncClientSession

setup_logger()
logger = logging.getLogger("ruscue")
logger.setLevel(logging.DEBUG)

gql_operations = gql("""
mutation StartToStretch {
  setLedBreathing(
    input: {
      name: "stretchy-startStretch"
      hue: 0
      saturation: 1.0
      initialValue: 0.0
      timeToPeak: 1000
      peak: 0.7
    }
  )
}

subscription OnButtonChange {
  buttonChange {
    button
  }
}
""")

EFFECTIVE_SCHEDULE = [(8, 12), (13.5, 18)]
STRETCH_INTERVAL_MINUTES = 45

last_stretch_time = time.time()
is_stretch_time = False


async def event_handler(_session, _event):
    global last_stretch_time, is_stretch_time

    if is_stretch_time:
        logger.info("Received stretch acknowledge, delaying 5 minutes for next stretch timer")
        last_stretch_time = time.time() + (5 * 60)
        is_stretch_time = False
    else:
        last_stretch_time = time.time()
        logger.info("An event received, stretch timer reset")

async def run_timer(session: ReconnectingAsyncClientSession | AsyncClientSession):
    global last_stretch_time, is_stretch_time

    while True:
        if is_stretch_time:
            await asyncio.sleep(1)
            pass

        minutes_since_last_stretch = (time.time() - last_stretch_time) / 60

        if minutes_since_last_stretch >= STRETCH_INTERVAL_MINUTES:
            logger.info("Time to stretch!")

            await session.execute(gql_operations, operation_name="StartToStretch")
            last_stretch_time = time.time()
            is_stretch_time = True

        await asyncio.sleep(1)


async def main():
    session = await connect_graphql()
    logger.info("Connected to server")

    asyncio.create_task(run_timer(session))

    await subscribe_server(session, gql_operations,operation_name="OnButtonChange", event_handler=event_handler)

asyncio.run(main())
