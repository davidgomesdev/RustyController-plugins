# 3 hours
DURATION = 3 * 60 * 60 * 1000


def create_effect(name, hue, saturation=1.0, value=0.2):
    return f"""
    mutation SetTemperatureColor {{
      setLedStatic(input: {{
        name: "weathery-{name}",
        hue: {hue},
        saturation: {saturation},
        value: {value},
        duration: {DURATION}
      }})
    }}
    """


EFFECT_BY_TEMP = {
    "NO_INFO": create_effect(name="NoInfo", hue=300, value=0.03),
    "LIGHT_RAIN": create_effect(name="LightRain", hue=194, saturation=0.84, value=0.04),
    "RAIN": create_effect(name="Rain", hue=220, value=0.04),
    "HEAVY_RAIN": create_effect(name="HeavyRain", hue=240, value=0.04),
    "A_BIT_CLOUDY": create_effect(name="ABitCloudy", hue=35, value=0.05),
    "CLOUDY": create_effect(name="Cloudy", hue=195, saturation=0.067, value=0.07),
    "THUNDER": create_effect(name="Thunder", hue=260, saturation=0.81, value=0.23),
    "SNOW": create_effect(name="Snow", hue=0, saturation=0.0, value=0.68),
    "SUNNY": create_effect(name="Sunny", hue=35, value=0.17),
}
