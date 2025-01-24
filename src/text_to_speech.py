from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

class AudioGenerator:
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))

    def generate(self, script: str) -> bytes:
        """
        Generates audio from script and returns the audio bytes
        Args:
            script (str): The podcast script to convert to audio
        Returns:
            bytes: The generated audio as bytes
        """
        audio = self.client.generate(
            text=script,
            voice="Brian",
            model="eleven_flash_v2_5"
        )
        return audio
