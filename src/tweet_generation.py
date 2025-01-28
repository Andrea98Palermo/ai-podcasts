from langchain_openai.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TweetGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            temperature=0.8
        )

    def generate(self, topic: str) -> str:
        """
        Generates a catchy tweet announcing an upcoming podcast episode about a given topic.
        
        Args:
            topic (str): The topic of the podcast episode
        
        Returns:
            str: A tweet with emojis announcing the podcast episode
        """
        # Craft the prompt for tweet generation
        prompt = f"""Generate a catchy and engaging tweet announcing an upcoming AI podcast episode about {topic}.
        Requirements:
        - Must be exactly one tweet (max 280 characters)
        - Never include emojis
        - Be exciting and attention-grabbing
        - Include the topic: {topic}
        - Mention it's an AI-generated podcast
        - Include #AIpodcast and #AIJoe hashtags and other appropriate hashtags
        
        Only return the tweet text, nothing else."""
        
        # Generate the tweet
        response = self.llm.invoke(prompt)
        tweet = response.content.strip()
        
        # Ensure the tweet is not longer than 280 characters
        if len(tweet) > 280:
            # If too long, generate a shorter version
            prompt += "\nIMPORTANT: The previous response was too long. Please make it shorter (under 280 characters)."
            response = self.llm.invoke(prompt)
            tweet = response.content.strip()
        
        return tweet

if __name__ == "__main__":
    topic = input("Enter the podcast topic to generate a tweet for: ")
    tweet_generator = TweetGenerator()
    tweet = tweet_generator.generate(topic)
    print("\nGenerated Tweet:\n")
    print(tweet)
    print(f"\nCharacter count: {len(tweet)}")
