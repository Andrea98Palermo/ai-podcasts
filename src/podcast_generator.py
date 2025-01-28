from dataclasses import dataclass
from script_generation import ContentSearcher, ScriptGenerator
from audio_generation import AudioGenerator
from cover_image_generation import CoverImageGenerator
from tweet_generation import TweetGenerator

@dataclass
class PodcastContent:
    """Data class to hold generated podcast content"""
    script: str
    audio_bytes: bytes
    cover_image_url: str
    tweet: str

class PodcastGenerator:
    def __init__(self):
        self.content_searcher = ContentSearcher()
        self.script_generator = ScriptGenerator()
        self.audio_generator = AudioGenerator()
        self.cover_image_generator = CoverImageGenerator()
        self.tweet_generator = TweetGenerator()

    def generate_podcast(self, topic: str) -> PodcastContent:
        """Main function to generate all podcast content"""
        # Search for content
        search_results = self.content_searcher.search(topic)
        
        # Generate script
        script = self.script_generator.generate(topic, search_results)

        print("Generated script:")
        print(script)
        # Generate audio # TODO: change to script
        audio_bytes = self.audio_generator.generate(script)
        
        # Generate cover image
        cover_image_url = self.cover_image_generator.generate(topic)
        
        # Generate tweet
        tweet = self.tweet_generator.generate(topic)
        
        return PodcastContent(
            script=script,
            audio_bytes=audio_bytes,
            cover_image_url=cover_image_url,
            tweet=tweet
        )