## RustyController plugins

Little scripts that use the [RustyController](https://github.com/LegendL3n/RustyController) API to create amazing effects.

The [run-all.sh](run-all.sh) script runs all plugins that are not ad-hoc.

Such as [Weathery](#weathery), which is one-off plugin, intended to be run at a certain hour.

The way it detects one as ad-hoc is by having a `.ad-hoc` on its directory. 

### Rustea

Has a list of colors, each corresponding to a tea, and chooses a random one, allowing me to decide which one to take in the morning :9.

### Weathery

Queries [IPMA](https://www.ipma.pt/opencms/pt/index.html) for the next day's weather, and sets the color accordingly.

### Brewertender

Counts down the time of a tea.

#### How to use

Press the `Move` button twice, then one of the 4 main buttons to select the tea.

It then will "brew" the tea, and at the end rumble to notify it has been brewed.

Press the `Move` button again to stop it. 

In any step you can press the `Move` button to cancel the process.

### Ruscue

Press `Start` and `Select` buttons simultaneously to set led and rumble off.

### Stretchy

Every 45 minutes sets the Led to indicate it's time to stretch.

Any button click will reset the timer, and to set the Led off use Ruscue.
