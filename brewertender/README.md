## Brewertender

### How to configure

Create a `config.json` file with the following structure:

```json
{
  "<button>": {
    "name": "white",
    "timings": [
      60,
      120
    ],
    "color": {
      "hue": 100,
      "saturation": 0.5,
      "value": 0.5
    }
  }
}
```

The button can be one of: `cross`, `square`, `triangle`, `circle`.

The timings array is to allow for a selection of brew times as well.

The name is the name of the tea. (just for label purposes)
