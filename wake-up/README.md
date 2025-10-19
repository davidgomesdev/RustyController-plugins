# Wake up

## Pre-requisites (Linux only)

`sudo apt install python3-pyaudio python3-dev portaudio19-dev`

Add this to `~/.asoundrc`:

```conf
pcm.mic {
    type plug
    slave {
        pcm "hw:1,0"
        rate 48000
    }
}

pcm.resample16k {
    type plug
    slave {
        pcm mic
        rate 16000
    }
}
```
