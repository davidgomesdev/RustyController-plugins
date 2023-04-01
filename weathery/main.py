import json
from datetime import datetime, timedelta
from urllib import request

from common.logger_utils import setup_logger
from python_graphql_client import GraphqlClient

from consts import *

logger = setup_logger("weathery")

wanted_date = (datetime.now() + timedelta(days=DAYS_FROM_TODAY))

with request.urlopen(f"{API_URL}/{LOCATION_ID}.json") as raw_data:
    json_data = json.load(raw_data)

date_formatted = wanted_date.strftime("%Y-%m-%dT00:00:00")

temp_info = next(
    row
    for row in json_data if row.get("dataPrev") == date_formatted and row.get("idPeriodo") == 24)

if temp_info is None:
    raise KeyError("Couldn't find temperature info for tomorrow!")

temperature_id = temp_info["idTipoTempo"]
effect = TEMP_ID_TO_HUE[temperature_id]

logger.debug(f"Sending temperature effect '{effect['name']}' for ID '{temperature_id}'")

client = GraphqlClient(endpoint="http://127.0.0.1:8080/graphql")

res = client.execute(effect['mutation'])

if "errors" in res or res['data']['setLedStatic'] != "SUCCESS":
    logger.error('Err! ' + str(res))
    exit(1)

logger.info('Sent temperature effect!')
