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

# Tea Shop
silverNeedles = {
    "hue": 295.774,
    "saturation": 0.256,
    "value": 0.58
}
milkTea = {
    "hue": 197.88235294117646,
    "saturation": 0.9,
    "value": 0.5
}
chocolatea = {
    "hue": 26.352941176470587,
    "saturation": 0.9,
    "value": 0.5
}
earlGrey = {
    "hue": 114.0,
    "saturation": 1.0,
    "value": 0.58
}

# Gorreana
white = {
    "hue": 0.0,
    "saturation": 0.0,
    "value": 0.68
}
blackPekoe = {
    "hue": 230.0,
    "saturation": 0.9,
    "value": 0.59
}

client = GraphqlClient(endpoint="http://127.0.0.1:8080/graphql")

pool = [silverNeedles, milkTea, chocolatea, earlGrey, white, blackPekoe]

choice = SystemRandom().choice(pool)

print('Random tea chosen!')

res = client.execute(mutation, variables=choice)

if "errors" in res or res['data']['setLedStatic'] != "SUCCESS":
    print('Err! ' + str(res))
    exit(1)

print('Sent tea choice!')

