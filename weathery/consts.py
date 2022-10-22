from effect import EFFECT_BY_TEMP

# Taken from https://www.ipma.pt/bin/file.data/weathertypes.json
TEMP_ID_TO_HUE = {
    # Sem informação / No information
    0: EFFECT_BY_TEMP["NO_INFO"],
    # Céu limpo / Clear sky
    1: EFFECT_BY_TEMP["SUNNY"],
    # Céu pouco nublado / Partly cloudy
    2: EFFECT_BY_TEMP["CLOUDY"],
    # Céu parcialmente nublado / Sunny intervals
    3: EFFECT_BY_TEMP["CLOUDY"],
    # Céu muito nublado ou encoberto / Cloudy
    4: EFFECT_BY_TEMP["CLOUDY"],
    # Céu nublado por nuvens altas / Cloudy (High cloud)
    5: EFFECT_BY_TEMP["CLOUDY"],
    # Chuva/aguaceiros / Showers/rain
    6: EFFECT_BY_TEMP["RAIN"],
    # Chuva/aguaceiros fracos / Light showers/rain
    7: EFFECT_BY_TEMP["LIGHT_RAIN"],
    # Chuva/aguaceiros fortes / Heavy showers/rain
    8: EFFECT_BY_TEMP["HEAVY_RAIN"],
    # Chuva/aguaceiros / Rain/showers
    9: EFFECT_BY_TEMP["RAIN"],
    # Chuva fraca ou chuvisco / Light rain
    10: EFFECT_BY_TEMP["LIGHT_RAIN"],
    # Chuva/aguaceiros fortes / Heavy rain/showers
    11: EFFECT_BY_TEMP["HEAVY_RAIN"],
    # Períodos de chuva / Intermittent rain
    12: EFFECT_BY_TEMP["RAIN"],
    # Períodos de chuva fraca / Intermittent ligth rain
    13: EFFECT_BY_TEMP["LIGHT_RAIN"],
    # Períodos de chuva forte / Intermittent heavy rain
    14: EFFECT_BY_TEMP["HEAVY_RAIN"],
    # Chuvisco / Drizzle
    15: EFFECT_BY_TEMP["LIGHT_RAIN"],
    # Neblina / Mist
    16: EFFECT_BY_TEMP["SNOW"],
    # Nevoeiro ou nuvens baixas / Fog
    17: EFFECT_BY_TEMP["SNOW"],
    # Neve / Snow
    18: EFFECT_BY_TEMP["SNOW"],
    # Trovoada / Thunderstorms
    19: EFFECT_BY_TEMP["THUNDER"],
    # Aguaceiros e possibilidade de trovoada / Showers and thunderstorms
    20: EFFECT_BY_TEMP["THUNDER"],
    # Granizo / Hail
    21: EFFECT_BY_TEMP["SNOW"],
    # Geada / Frost
    22: EFFECT_BY_TEMP["SNOW"],
    # Chuva e possibilidade de trovoada / Heavy rain and thunderstorms
    23: EFFECT_BY_TEMP["THUNDER"],
    # Nebulosidade convectiva / Convective clouds
    24: EFFECT_BY_TEMP["SNOW"],
    # Céu com períodos de muito nublado / Partly cloudy
    25: EFFECT_BY_TEMP["CLOUDY"],
    # Nevoeiro / Fog
    26: EFFECT_BY_TEMP["SNOW"],
    # Céu nublado / Cloudy
    27: EFFECT_BY_TEMP["CLOUDY"],
    # Aguaceiros de neve / Snow showers
    28: EFFECT_BY_TEMP["SNOW"],
    # Chuva e Neve / Rain and snow
    29: EFFECT_BY_TEMP["SNOW"],
    # Chuva e Neve / Rain and snow
    30: EFFECT_BY_TEMP["SNOW"],
}

# Lisbon ID
# Taken from https://api.ipma.pt/public-data/forecast/locations.json
LOCATION_ID = 1110600
API_URL = "https://api.ipma.pt/public-data/forecast/aggregate"
DAYS_FROM_TODAY = 1
