import openwakeword
from openwakeword.model import Model
import numpy as np
import argparse
import pyaudio
import asyncio
from gql import gql
from common.graphql_utils import connect_graphql
from gql.client import ReconnectingAsyncClientSession, AsyncClientSession
from gql.transport.exceptions import TransportQueryError, TransportError

color_change = gql("""
mutation SetColor {
    setLedBreathing(input: {
      name: "wake-up"
      hue: 0
      saturation: 1.0
      initialValue: 0.3
      timeToPeak: 1000
      peak: 1.0
      duration: 1000
    })
}
""")

async def change_color(session: ReconnectingAsyncClientSession | AsyncClientSession):
  print('Changing color')
  try:
    await session.execute(color_change, operation_name="SetColor")
  except TransportError | TransportQueryError as e:
    logger.error("Error in StartToStretch mutation", e, exc_info=True)


parser = argparse.ArgumentParser()
parser.add_argument('--model', default='alexa')
parser.add_argument('--framework', default='tflite')
parser.add_argument('--device', required=False)
parser.add_argument('--min-score', default=0.5, type=float)

args = parser.parse_args()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280
audio = pyaudio.PyAudio()

device_count = audio.get_device_count()

print('Have', device_count, 'devices')

for i in range(0, device_count):
  info = audio.get_device_info_by_index(i)
  print(info)

device_index = args.device
model = args.model
min_score = args.min_score
framework = args.framework

if device_index == None:
  quit()

print('Opening', device_index, 'mic')

mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=False, input_device_index=int(device_index), frames_per_buffer=CHUNK)

owwModel = Model(wakeword_models = [model], inference_framework=framework)

print('Model initialized')

async def main():
    session = await connect_graphql()
    
    while True:
        inc_audio = mic_stream.read(CHUNK, exception_on_overflow=False)
        audio = np.frombuffer(inc_audio, dtype=np.int16)

        owwModel.predict(audio)

        for mdl in owwModel.prediction_buffer.keys():
            scores = owwModel.prediction_buffer[mdl]
            current_score = scores[-1]

            print("%0.3f" % current_score)

            if current_score >= float(args.min_score):
              await change_color(session)

asyncio.run(main())
