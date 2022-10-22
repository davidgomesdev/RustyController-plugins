# 3 hours
DURATION = 3 * 60 * 60


def create_effect(hue, saturation=1.0, value=0.3):
    return f"""
    mutation SetTemperatureColor {{
      setLedStatic(input: {{
        hue: {hue},
        saturation: {saturation},
        value: {value},
        duration: {DURATION}
      }})
    }}
    """


EFFECT_BY_TEMP = {
    "NO_INFO": create_effect(hue=300, value=0.03),
    "LIGHT_RAIN": create_effect(hue=194, saturation=0.84, value=0.19),
    "RAIN": create_effect(hue=197, value=0.05),
    "HEAVY_RAIN": create_effect(hue=235, value=0.05),
    "CLOUDY": create_effect(hue=195, saturation=0.067, value=0.23),
    "THUNDER": create_effect(hue=237, saturation=0.81, value=0.23),
    "SNOW": create_effect(hue=0.0, saturation=0.0, value=0.68),
    "SUNNY": create_effect(hue=26),
}
