import json
from python_graphql_client import GraphqlClient
from random import SystemRandom

mutation = """
mutation SetColor($hue: Float!, $saturation: Float!, $value: Float!, $duration: Int!) {
    setLedStatic(input: {
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

print("Chose '" + choice['name'] + "'!")

variables = choice
variables['duration'] = duration

res = client.execute(mutation, variables=variables)

if "errors" in res or res['data']['setLedStatic'] != "SUCCESS":
    print('Err! ' + str(res))
    exit(1)

print('Sent tea choice for ' + str(duration) + ' milliseconds!')
