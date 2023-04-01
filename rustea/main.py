import json

import pytimeparse
from common.logger_utils import setup_logger
from python_graphql_client import GraphqlClient
from random import SystemRandom

logger = setup_logger("rustea")

mutation = """
mutation SetColor($name: String!, $hue: Int!, $saturation: Float!, $value: Float!, $duration: Int!) {
    setLedStatic(input: {
        name: $name,
        hue: $hue,
        saturation: $saturation,
        value: $value,
        duration: $duration
    })
}
"""


with open('teas.json', 'r') as teasFile:
    json = json.load(teasFile)

client = GraphqlClient(endpoint="http://127.0.0.1:8080/graphql")

duration = json['duration']
choice = SystemRandom().choice(json['pool'])

logger.info("Chose '" + choice['name'] + "'!")

variables = choice
variables['duration'] = pytimeparse.parse(duration)

res = client.execute(mutation, variables=variables)

if "errors" in res or res['data']['setLedStatic'] != "SUCCESS":
    logger.error('Err! ' + str(res))
    exit(1)

logger.debug(f'Sent tea choice for {duration}!')
