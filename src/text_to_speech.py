from elevenlabs import play, save
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()


client = ElevenLabs(
  api_key=os.getenv('ELEVENLABS_API_KEY'),
)

audio = client.generate(
  text="Thank you for tuning in, and remember, every perspective matters, every question counts, and every voice, including yours, can contribute to building bridges of understanding. Until next time, goodbye and keep on learning!",
  voice="Brian",
  model="eleven_flash_v2_5"
)
save(audio, "./generated_audio/test.wav")
# audio_bytes = b"".join(audio)
# print(audio_bytes)
# with open("./generated_audio/test.wav", "wb") as fp:
#     fp.write(audio_bytes)
