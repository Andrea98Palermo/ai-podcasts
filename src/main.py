import os
# Use absolute import since we're running this file directly
from podcast_generator import generate_podcast_content

# In your backend route/handler
topic = "quantum computing"  # Get this from the request
podcast_content = generate_podcast_content(topic)


script = podcast_content.script
audio_bytes = podcast_content.audio_bytes
cover_image_url = podcast_content.cover_image_url
tweet = podcast_content.tweet
# Access the generated content
# Print the generated content
print("\nGenerated Script:\n")
print(script)
print("\nCover Image URL:\n")
print(cover_image_url)
print("\nTweet:\n") 
print(tweet)

# Save the audio file

audio_dir = "generated_audio"
os.makedirs(audio_dir, exist_ok=True)
audio_path = os.path.join(audio_dir, f"{topic}.wav")
with open(audio_path, "wb") as f:
    f.write(b"".join(audio_bytes))
print(f"\nAudio saved to: {audio_path}")
