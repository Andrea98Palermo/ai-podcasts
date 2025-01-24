from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.images.generate(
    model="dall-e-3",
    prompt="a cover image for a podcast about climate change",
    size="1024x1024",
    quality="hd",
    n=1,
)

print(response.data[0].url)