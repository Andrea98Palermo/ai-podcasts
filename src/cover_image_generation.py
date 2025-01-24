from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class CoverImageGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def generate(self, topic: str) -> str:
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=f"a cover image for a podcast about {topic}",
            size="1024x1024",
            quality="hd",
            n=1,
        )
        return response.data[0].url