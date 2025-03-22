# 3 hours
DURATION = 3 * 60 * 60 * 1000


def create_effect(name, hue, saturation=1.0, value=1.0):
    return {
        'name': name,
        'mutation': f"""
            mutation SetTemperatureColor {{
              setLedStatic(input: {{
                name: "weathery-{name}",
                hue: {hue},
                saturation: {saturation},
                value: {value},
                duration: {DURATION}
              }})
            }}"""
    }


EFFECT_BY_TEMP = {
    "NO_INFO": create_effect(name="NoInfo", hue=300, value=1.0),
    "RAIN": create_effect(name="Rain", hue=220, saturation=1.0, value=0.8),
    "LIGHT_RAIN": create_effect(name="Light Rain", hue=210, saturation=0.7, value=1.0),
    "A_BIT_CLOUDY": create_effect(name="ABitCloudy", hue=50, saturation=0.8, value=1.0),
    "CLOUDY": create_effect(name="Cloudy", hue=200, saturation=0.1, value=1.0),
    "SNOW": create_effect(name="Snow", hue=150, saturation=0.65, value=1.0),
    "HEAVY_RAIN": create_effect(name="HeavyRain", hue=240, value=1.0),
    "THUNDER": create_effect(name="Thunder", hue=260, saturation=0.81, value=1.0),
    "SUNNY": create_effect(name="Sunny", hue=35, value=1.0)
}
