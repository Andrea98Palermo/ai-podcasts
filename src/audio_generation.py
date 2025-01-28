from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from pydub import AudioSegment
import io
import os
# Load environment variables from .env file
load_dotenv()

class AudioGenerator:
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        self.intro_path = os.getenv('INTRO_AUDIO_PATH', 'assets/intro.mp3')
        self.outro_path = os.getenv('OUTRO_AUDIO_PATH', 'assets/intro.mp3')

    def _generate_voice(self, script: str) -> AudioSegment:
        """
        Generates the voice audio from the script by splitting into chunks and combining
        Args:
            script (str): The text to convert to speech
        Returns:
            AudioSegment: The generated voice audio
        """
        # Split script into chunks of max 10000 chars, ending at periods
        chunks = []
        current_chunk = ""
        
        for sentence in script.split('.'):
            sentence = sentence.strip() + '.'
            if len(current_chunk) + len(sentence) <= 2000:
                current_chunk += sentence + ' '
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ' '
        if current_chunk:
            chunks.append(current_chunk.strip())

        # Generate audio for each chunk and combine with pauses
        combined_audio = None
        pause = AudioSegment.silent(duration=500)  # 500ms pause between chunks
        
        for chunk in chunks:
            voice_audio_bytes = self.client.generate(
                text=chunk,
                voice="Brian", 
                model="eleven_multilingual_v2"
            )
            chunk_audio = AudioSegment.from_file(io.BytesIO(b"".join(voice_audio_bytes)), format="mp3")
            
            if combined_audio is None:
                combined_audio = chunk_audio
            else:
                combined_audio += pause + chunk_audio

        return combined_audio
    
    def _add_intro(self, voice_segment: AudioSegment, fade_duration: int = 3000) -> AudioSegment:
        """
        Adds intro music with fade out to the voice segment
        Args:
            voice_segment (AudioSegment): The voice audio
            fade_duration (int): Duration of the fade in milliseconds
        Returns:
            AudioSegment: Combined intro and voice audio
        """
        intro_segment = AudioSegment.from_file(self.intro_path)
        
        # Apply fades
        intro_segment = intro_segment.fade_out(fade_duration)
        
        # Split voice and combine with intro
        voice_overlap = voice_segment[:fade_duration]
        voice_remaining = voice_segment[fade_duration:]
        
        combined = intro_segment.overlay(voice_overlap, position=len(intro_segment)-fade_duration)
        return combined + voice_remaining
    
    def _add_outro(self, audio_segment: AudioSegment, fade_duration: int = 3000) -> AudioSegment:
        """
        Adds outro music with fade in to the audio segment
        Args:
            audio_segment (AudioSegment): The current audio
            fade_duration (int): Duration of the fade in milliseconds
        Returns:
            AudioSegment: Final audio with outro
        """
        outro_segment = AudioSegment.from_file(self.outro_path)
        outro_segment = outro_segment.fade_in(fade_duration)
        
        # Position outro to start before audio ends
        outro_position = len(audio_segment) - fade_duration
        
        # Create final segment with enough length for both
        total_length = max(len(audio_segment), outro_position + len(outro_segment))
        final_audio = audio_segment
        
        # Extend with silence if needed
        if total_length > len(audio_segment):
            silence = AudioSegment.silent(duration=total_length - len(audio_segment))
            final_audio = final_audio + silence
        
        return final_audio.overlay(outro_segment, position=outro_position)
    
    def generate(self, script: str) -> bytes:
        """
        Generates complete audio with intro and outro
        Args:
            script (str): The podcast script to convert to audio
        Returns:
            bytes: The final audio as bytes
        """
        # Generate and combine all audio elements
        voice_segment = self._generate_voice(script)
        with_intro = self._add_intro(voice_segment)
        final_audio = self._add_outro(with_intro)
        
        # Export to bytes
        buffer = io.BytesIO()
        final_audio.export(buffer, format="mp3")
        return buffer.getvalue()

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    script = """

Good day, crypto enthusiasts everywhere, and welcome to another episode of the Cryptoverse. In today's episode, we're delving deep into the world of meme coins and exploring one that has recently made waves over the crypto market: the Official Trump MemeCoin, also known as TRUMP. 

This unique token entered the world stage thanks to President-elect Donald Trump, who launched this memecoin merely three days before returning to the White House. The Official Trump MemeCoin, launched on the Solana network on January 17, 2025, quickly sparked fascination amongst traders, crypto speculators, and millions of supporters across the globe.

While memecoins are a type of cryptocurrency similar to bitcoin, their value is primarily derived not from inherent utility, but from the level of community interest and engagement, making them an intriguing blend of digital currency and social phenomenon. And when it comes to interest and engagement, few figures draw as much as the former US president, Donald Trump.

While there have been other Trump-themed coins, like the FreedomCoin, which used to be known as TrumpCoin, the Official Trump MemeCoin is the latest and endorsed token tied directly to Trump, bringing an unprecented market attention to it.

The launch of TRUMP MemeCoin was a historic event, marking the first time that a serving president has entered the crypto market in such a capacity. The potential of merging politics with decentralized finance was too intriguing for the markets to ignore.

The entrance of the Official Trump MemeCoin into the market wasn't serene; it came with a bang. So magnificent was its entry that it broke into the crypto top 20 by market capitalization. Within days of its launch, the valuation of the coin hit an eye-watering $14 billion, signalling the immense enthusiasm investors have for this token.

Critics have also not been quiet. Some have accused Trump of profiting from his presidency by launching the coin. The Trump administration was, however, known for its pro-crypto stance, associating his launch with an overall supportive environment for cryptocurrency development and trading. 

This pro-crypto approach even extended to proposed looser market regulations which, in the eyes of many, could signal a strong future for the TRUMP MemeCoin. It's since become the subject of intense debate and speculation, not just in the political sphere, but also amongst crypto market analysis and investors.

Now as the dust settles on its explosive entry, TRUMP MemeCoin has attracted even more attention thanks to certain high-profile developments. Amongst these was the launch of a rival cryptocurrency by Melania Trump, causing a dip in the original TRUMP MemeCoin's value, a thrilling twist that has made the story of this new token all the more engrossing.

This has all culminated in a climate of heightened anticipation amongst the cryptocurrency community. The crypto market is now braced for what's next. What direction will TRUMP MemeCoin take in this tumultuous environment? Will there be further bombshells in the offing and how will this impact the value of this controversial coin? With the inauguration underway, these questions are more poignant and relevant than ever. 

As we continue to dissect the story of TRUMP MemeCoin, other aspects we would be looking at includes how to discern fake Trump tokens from the genuine ones as well as the future prospects of the TRUMP MemeCoin... Stay tuned as we unwrap these layers in the following segments.

In the next segment of our podcast, we are going to delve further into the unique geopolitical and social circumstances that may have influenced the explosive rise of TRUMP MemeCoin, as well as the role of blockchain technology and meme culture in reshaping our understanding of currency and value in the modern world.

As each day passes and market conditions develop, the reality of a serving president launching a memecoin is setting in. This raises critical questions about how politics and decentralized finance could further intertwine in the future. Was this just a unique event or could this pave the way for other political figures to embrace the crypto space? We'll explore these angles and discuss how this emergent trend could shape the financial landscape of the future.  

Dalio once famously said, "Cash is trash". Could politics be the next frontier in the world of crypto, pushing its integration into mainstream society even further? The inception of TRUMP MemeCoin certainly throws this topic back into the spotlight and warrants deeper scrutiny. Let's then delve into what this could mean, not just for the world of finance, but for the democratic process and the societal norms that underpin it. 

Moreover, as we consider these fascinating developments, we also need to better understand the technical side of the TRUMP MemeCoin. Why was the Solana network chosen for the launch of this memecoin? How has this influenced its performance and cross-compatibility with other tokens, networks, and digital wallets? And what are the larger implications for the ongoing competition between differing blockchain technologies?

Apart from exploring these intriguing questions, we shall also delve into TRUMP MemeCoin's economic dynamics. Despite its popularity, some investors are doubtful about memecoin's wild valuations. They perceive them as bubbles that could burst anytime, pulling down billions of investments with them. We will take a closer look at this differing perspective and examine the actual economic fundamentals driving the value of TRUMP MemeCoin, providing listeners with a detailed analysis and insights.

Lastly, we cannot overlook the immense public interest that has arisen from the launch of the TRUMP MemeCoin, shaping it into both a symbol of decentralized finance and a socio-political phenomenon. Let's explore how this new token is perceived in different corners of the globe, dissecting its impact across various cultures and age groups. Join us as we unravel this unique blend of finance and fandom in our next segment. 

These are just a few of the fascinating angles we will be exploring in our forthcoming segments. The story of the TRUMP MemeCoin is far from over and is sure to keep us on the edge of our seats for months, if not years, to come. So, be sure to stay tuned as we dive further into these uncharted waters, uncovering the ongoing story of the TRUMP MemeCoin.

As we navigate the terrain of TRUMP MemeCoin's journey, we will also delve into the strategies and marketing efforts that have been integral to its explosive growth. We all know that when it comes to visibility, Donald Trump is no stranger to the limelight. How much did the Trump brand factor into the monumental attention on his memecoin? Has the celebrity effect played a role in the coin's unicorn-like escalation? And can we attribute the coin's success to the strength of Trump's online fanbase, or are there other upper-level market dynamics at play that we need to understand?

Right along with that, it will be essential to get a grasp on the regulatory implications around TRUMP MemeCoin. Many global jurisdictions are still wrestling with how to classify and regulate cryptocurrencies, and now we've introduced the variable of political figures and governments launching their unique tokens. What does this mean for developing legislation and what may future regulation look like? The legality, transparency, and ethical implications of such scenarios will be given a thorough examination to bring more clarity to this contentious issue.

Moreover, we'll be exploring implications not just confined to the world of finance. The launch of a political memecoin has cultural significance, involving not just potential economic impact, but extending to societal norms, community engagements, and even the boundaries of freedom of speech. We will examine how these aspects are influenced and reshaped by such fascinating events, and what it means for the evolution of societal values in a digitized world.

Beyond that, the influence of geopolitics and international relations on the trajectory of TRUMP MemeCoin cannot be overlooked either. As we dive deeper into the token's journey, we will investigate the role geopolitical tensions and alliances might play in the price and reputation of the coin. Could political sentiments bolster or depress its performance, and will it be a tool in the arsenal of political discourse? These are important contexts to consider as we delve into the course TRUMP MemeCoin charts on the global stage.

As we unravel the narrative of the TRUMP MemeCoin, we will also be casting an analytical gaze towards competing memecoins. Melania Trump's personal memecoin, for instance, could possibly alter the dynamics in play. Could we foresee a competition, or perhaps even a collaboration, between these tokens? Understanding the interrelationships between various memecoins strategies, and how they might mutually impact each other’s future prospects, will be another avenue we plan on exploring.

In the backdrop of all these developments, the technology that enabled this saga, blockchain, also deserves our close scrutiny. How have advancements in this space fostered the growth of memes coins? Are there foreseeable innovations on the horizon that could dramatically influence the landscape these tokens operate within?

As we progress through this intricate storyline of TRUMP MemeCoin, we will keep a keen eye on other emerging trends and developments in the crypto space. Although TRUMP MemeCoin has been the focus of attention these past few weeks, the rapidly evolving world of cryptocurrencies is teeming with potential surprises, and we'll ensure we keep you updated on any significant shifts that occur. 

Join us as we deep dive into these exciting aspects in the compelling journey of TRUMP MemeCoin and beyond. As we chart this fascinating course, we promise to unravel every twist and turn and bring you all the interesting insights shaping this remarkable story. Be sure to stick around as we continue navigating these captivating developments together.

We also recognize the importance of understanding the psychology behind investors and digital natives in this memecoin phenomenon. The concept of memecoins presenting an element of rebel investment strategy, taking a jibe at traditional financial systems, has given them distinctive cultural capital. Interestingly, the same wave of decentralized finance ideology has also seen a tangible shift in sentiment among people towards asset ownership and opportunities to voice their support or opposition to various matters. So, in our upcoming segments, we'll explore these shifting narratives and the underlying socio-cultural shifts that make this era of memecoins so captivating.

Furthermore, as TRUMP MemeCoin enters the arenas of both politics and finance, we must consider the implications for public trust. In an age where trust in both financial institutions and political bodies is at a nadir, could the fusion of the two in the form of a memecoin swing public sentiment in any significant way? Also, are there challenges that arise from a sitting president issuing a cryptocurrency? We'll be delving into these complex questions, uncovering the ways this could influence popular perceptions of both cryptocurrency and politics.

Given the buzz around TRUMP MemeCoin, it is also vital to assess the role of media, both traditional and social, in its rise. How have different media outlets and platforms played into the narrative? What has been the reaction on social media? Have there been any substantial influencers or online communities that have significantly swayed the public narrative about this memecoin? And, in the age of instant information, how are the public and market speculators reacting to these media narratives? We'll pay keen attention to these factors in our analysis.

Moreover, we can't ignore the potential impact of the TRUMP MemeCoin on the concept of fundraising for political campaigns. With an established link between crowdfunding and cryptocurrencies, could the ICO approach be employed for political campaign financing? Or can candidates leverage their unique tokens as a means of galvanizing support? Understanding these speculative possibilities would indeed open a pandora's box regarding the many subversions that TRUMP MemeCoin could prompt in our political system.

As a consequence of all these variables, we'll be sure to review the safeguards and risks involved in investing in memecoins like the TRUMP MemeCoin. We'll explore the protective measures that investors can adopt, and the potential pitfalls that they should be mindful of in dealing with such trending coins.

And, while we decipher these remarkable trends in TRUMP MemeCoin's trajectory, we shall also contemplate the future role of governments in the crypto space. Could centralized governments around the world adapt to these changes and accommodate the rising influence of crypto in their administrative and financial frameworks? How might a potential government's own cryptocurrency influence national and global economies? 

Plus, as we dissect the various aspects of this unprecedented event, we'll be analyzing the role of technology and aiming to decipher what the future holds in the realm of crypto security, regulations, scalability, utility, and market volatility. We will also probe into innovations such as NFTs and DeFi, and how they interact with memecoins like the TRUMP MemeCoin, exploring the enthralling renewal of value perception they signify. 

We'll also endeavor to look into the possibility of copycat political memecoins that this event could inspire. Could we see other political leaders or entities following suit, turning the phenomenon into a full-blown trend? We'll review the political landscape worldwide and attempt to objectively consider who might venture into this uncharted territory next.

As we journey through these multifaceted narratives around the TRUMP MemeCoin, we promise to keep shedding light on the numerous critical conversations culminating around it. Stay with us as we unravel more intriguing aspects of this unconventional junction of politics and finance, and explore the transformations this new chapter in cryptocurrency is penning in our societal norms and traditions.

In our forthcoming segments, we also plan to delve deeper into the macroeconomic implications of prominent political figures like Donald Trump launching their own cryptocurrencies. As we've seen with the rise and success of TRUMP MemeCoin, political presence can have a significant impact on the popularity and valuation of these tokens. We'll dive into exploring how much of this is speculation and how much truly corresponds to the fundamental economic indicators. Moreover, we will seek to understand if the macroeconomic trends prevailing at the time of such launches could influence the market performance of these politico-cryptocurrency hybrids.

On another note, the TRUMP MemeCoin saga gives us ample material to examine the socio-psychological dynamics associated with such initiatives. In our future episodes, we'll divert our focus towards the psychological aspects influencing the decisions of the investors. We'll aim to explore the underlying emotions, beliefs, and bias that could be at play - the 'FOMO' (Fear Of Missing Out), brand loyalty, the appeal of participating in a movement, or perhaps the thrill of getting associated with a controversial figure. 

Understanding these inner workings of the investor’s mind could yield significant insights into the demand dynamics of political memecoins and also the broader investor behavior in the crypto market. We are living in times where irrational exuberance is oftentimes pushing cryptocurrency prices, and such a study could bring valuable insights to both individual investors and market regulators.

In addition, we will focus our lens on the various technological aspects of the TRUMP MemeCoin. From understanding the specifics of its underlying blockchain technology, Solana, to discerning why it was chosen over other popular blockchain platforms, we aim to provide a comprehensive analysis. We will touch upon the technicalities of smart contracts, transaction speed, energy efficiency, and scalability that come with Solana and how they impact the functioning of the TRUMP MemeCoin. 

Beyond this, there's an interesting angle to explore regarding the power dynamics involved in such cases. When renowned public figures like Donald Trump launch their own cryptocurrencies, it gives them not just economic power but also significant control over a technology-enabled monetary system. We'll look into the potential risks this situation could pose in terms of centralization of power, manipulation of value, and in extreme scenarios, potential to sway political or economic outcomes.

As we progress in our exploration of the impact of the TRUMP MemeCoin, or any similar political memecoin, we also aim to discuss the implications these tokens could have on global economic practices. For instance, will these cryptocurrencies have the potential to influence socioeconomic policies, both domestic and foreign? Could they become soft power tools or economic weapons in the geopolitical arena? How might they influence global trade, international relations, or global monetary systems? These are some of the numerous questions we intend to answer as we further unravel the intricacies of the TRUMP MemeCoin.

In our subsequent segments, we also plan to highlight the role of legislation in the sphere of memecoins, with a special focus on political memecoins like the TRUMP MemeCoin. Despite the global expansion of the crypto market, the legal framework around these digital assets remains murky and varies greatly by jurisdiction. But with political entities entering the fray, the exigence for clear rules and regulatory framework becomes even higher. Therefore, we'll explore the existing laws governing cryptocurrencies, the legal challenges they face, and the potential legislative changes that could be on the horizon.

Finally, in the backdrop of the cultural phenomenon that is TRUMP MemeCoin, we can't ignore the role played by the power of digitization and the internet community. In future episodes, we'll explore how these modern aspect of our lives are not just changing the way we perceive and trade value but also altering the sociocultural dimensions of our society. We will be looking into the viral nature of memes, the role of online communities, and the impact of social platforms in propelling the popularity and value of memecoins like TRUMP. So, stay tuned as we unravel this and much more.

In conclusion, the launch of the Official Trump MemeCoin, or TRUMP, is a landmark event in both the worlds of cryptocurrency and politics. This unique fusion has sparked immense interest, debate, and speculation globally. The explosive rise of TRUMP on the back of Donald Trump's popularity, its impactful entry into the crypto market, and the intense debate around its implications illuminates the potential symbiosis between political legacy and decentralized finance. 

Not only has this new-age venture disrupted the crypto sphere, it has also called into question the future trajectory of politics, regulatory frameworks, geopolitical dynamics, financial behavior, socio-cultural movements and the power of internet communities. Whether the TRUMP MemeCoin is seen as an audacious power move, a savvy marketing gimmick, or a genuine investment opportunity, its launch marks an intriguing inception of the politicization of crypto and an interesting arena to navigate for the future. 

As we continue this exploration, remember that TRUMP MemeCoin, as with any other burgeoning trend in the crypto space, calls for conscious investment. Be it individual investors, market speculators, or crypto enthusiasts, one must equip oneself with accurate knowledge, discerning analysis, and intuitive understanding of the market dynamics. 

With that said, don't forget to get involved even more actively with us using the AIPODCAST token. By buying and burning the AIPODCAST token, you can vote for the topics for future podcasts. It's an excellent way to steer the discourse towards the questions you want answered and the narratives you're intrigued by. 

Thank you for joining us in this exploration of the intersection of politics and finance. As the saga of TRUMP MemeCoin continues, we promise to be your guiding compass in this thrilling journey. Until next time, keep exploring, keep learning, and keep asking the right questions. Goodbye, and stay tuned!
"""

    output_dir = "generated_audio"
    os.makedirs(output_dir, exist_ok=True)
    
    # Example script
    test_script = "Welcome to today's episode, where we delve into one of the most enduring and contentious conflicts of our time: the Israeli-Palestinian issue. Thank you for tuning in, and remember, every perspective matters, every question counts, and every voice, including yours, can contribute to building bridges of understanding. Until next time, goodbye and keep on learning!"
    
    # Generate audio
    generator = AudioGenerator()
    audio_bytes = generator.generate(test_script)
    
    # Save to file
    output_path = os.path.join(output_dir, "output_2.mp3")
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    
    print(f"Audio saved to: {output_path}")
