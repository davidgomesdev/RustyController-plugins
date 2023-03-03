import asyncio
import logging
import os
import time

from common.graphql_utils import connect_graphql, subscribe_server
from gql import gql

from common.logger_utils import setup_logger
from gql.client import ReconnectingAsyncClientSession, AsyncClientSession
from gql.transport.exceptions import TransportQueryError, TransportError

setup_logger()
logger = logging.getLogger("ruscue")
logger.setLevel(logging.DEBUG)

# Used to test schedule in seconds instead of minutes with a lower value
is_dev_mode = os.environ.get("IS_DEV_MODE", "false").lower() == 'true'

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

mutation StretchFinished {
    setLedOff
}

subscription OnButtonChange {
  buttonChange {
    button
  }
}
""")

EFFECTIVE_SCHEDULE = [(9, 12), (14, 18)]
STRETCH_INTERVAL_MINUTES = 5 if is_dev_mode else 45

last_stretch_time = time.time()
is_stretch_time = False


async def event_handler(session, _event):
    global last_stretch_time, is_stretch_time

    if is_stretch_time:
        logger.info("Received stretch acknowledge, delaying 5 minutes for next stretch timer")

        last_stretch_time = time.time() + (5 * (1 if is_dev_mode else 60))
        is_stretch_time = False

        try:
            await session.execute(gql_operations, operation_name="StretchFinished")
        except TransportError | TransportQueryError as e:
            logger.error("Error in StartToStretch mutation", e, exc_info=True)
    else:
        # Avoids resetting the 5 minutes delay
        if last_stretch_time < time.time():
            last_stretch_time = time.time()
            logger.info("An event received, stretch timer reset")

async def run_timer(session: ReconnectingAsyncClientSession | AsyncClientSession):
    global last_stretch_time, is_stretch_time

    while True:
        is_in_schedule = False

        for time_range in EFFECTIVE_SCHEDULE:
            if time_range[0] <= time.localtime().tm_hour <= time_range[1]:
                is_in_schedule = True
                break

        if not is_in_schedule:
            logger.debug("Not on schedule, sleeping for 15min")
            await asyncio.sleep(15 * 60)
            pass

        minutes_since_last_stretch = (time.time() - last_stretch_time) / (1 if is_dev_mode else 60)

        if not is_stretch_time and minutes_since_last_stretch >= STRETCH_INTERVAL_MINUTES:
            logger.info("Time to stretch!")

            try:
                await session.execute(gql_operations, operation_name="StartToStretch")
            except TransportError | TransportQueryError as e:
                logger.error("Error in StartToStretch mutation", e, exc_info=True)
            last_stretch_time = time.time()
            is_stretch_time = True

        await asyncio.sleep(1)

async def main():
    if is_dev_mode:
        logger.warning("Running in Dev Mode")

    session = await connect_graphql()
    logger.info("Connected to server")

    asyncio.create_task(run_timer(session))

    await subscribe_server(session, gql_operations,operation_name="OnButtonChange", event_handler=event_handler)

asyncio.run(main())
