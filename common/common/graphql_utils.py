import os
from typing import Any, Callable, Awaitable

import backoff
from gql.client import ReconnectingAsyncClientSession, Client, AsyncClientSession
from gql.transport.exceptions import TransportClosed
from gql.transport.websockets import WebsocketsTransport
from graphql import DocumentNode

retry_connect = backoff.on_exception(
    backoff.expo,
    Exception,
    max_value=20
)

retry_execute = backoff.on_exception(
    backoff.constant,
    Exception,
    max_tries=5,
    interval=0.1,
    giveup=lambda e: not (isinstance(e, TransportClosed)),
)


@backoff.on_exception(backoff.expo,
                      Exception,
                      max_value=5,
                      giveup=lambda e: not (isinstance(e, TransportClosed)))
async def subscribe_server(
        session: ReconnectingAsyncClientSession,
        document: DocumentNode,
        operation_name: str,
        event_handler: Callable[[ReconnectingAsyncClientSession, dict[str, Any]], Awaitable[None]]
):
    async for data in session.subscribe(document, operation_name=operation_name):
        await event_handler(session, data)


async def connect_graphql() -> ReconnectingAsyncClientSession | AsyncClientSession:
    transport = WebsocketsTransport(url='ws://%s/subscriptions' % (os.environ.get("RUSTY_IP_PORT", "127.0.0.1:8080")),
                                    connect_args={"ping_interval": None}
                                    )
    client = Client(
        transport=transport,
        fetch_schema_from_transport=False
    )

    return await client.connect_async(reconnecting=True, retry_connect=retry_connect, retry_execute=retry_execute)
