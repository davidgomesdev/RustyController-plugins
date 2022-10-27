from python_graphql_client import GraphqlClient
from random import SystemRandom

mutation = """
mutation SetColor($hue: Float!, $saturation: Float!, $value: Float!) {
    setLedStatic(input: {
        hue: $hue,
        saturation: $saturation,
        value: $value,
        # 3 hours
        duration: 10800000
    })
}
"""


def create(name, hue, saturation, value):
    return {
        "name": name,
        "hue": hue,
        "saturation": saturation,
        "value": value,
    }


pool = [
    # Tea Shop
    create("silverNeedles", 308.0, 0.55, 0.5),
    create("milkTea", 197.8, 0.75, 0.3),
    create("chocolatea", 26.3, 0.9, 0.5),
    ## create("earlGrey", 114.0, 1.0, 0.58),
    # Gorreana
    create("white", 0.0, 0.0, 0.3),
    create("blackPekoe", 230.0, 0.9, 0.59),
    # Tea bag
    create("yerbaMate", 0.0, 1.0, 0.3),
]

client = GraphqlClient(endpoint="http://127.0.0.1:8080/graphql")

choice = SystemRandom().choice(pool)

print("Chose '" + choice['name'] + "'!")

res = client.execute(mutation, variables=choice)

if "errors" in res or res['data']['setLedStatic'] != "SUCCESS":
    print('Err! ' + str(res))
    exit(1)

print('Sent tea choice!')
