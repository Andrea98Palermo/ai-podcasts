from typing import List, Dict
from tavily import TavilyClient
from langchain_openai.chat_models import ChatOpenAI
import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_openai.embeddings import OpenAIEmbeddings

# Load environment variables from .env file
load_dotenv()

class ContentSearcher:
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
        # self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=os.getenv('OPENAI_API_KEY'))
        # self.vectorstore = None

    def get_search_queries(self, main_topic: str) -> List[str]:

        general_results = self.client.search(
            query=main_topic,
            search_depth="advanced",
            max_results=30
        )
        news_results = self.client.search(
            query=main_topic,
            topic="news",
            days=30,
            search_depth="advanced",
            max_results=15
        )
        print(f"\nGenerating search topics for: {main_topic}")
        prompt = (
            f"Given the following search results for '{main_topic}':\n"
            f"General: {general_results}\n"
            f"News: {news_results}\n"
            f"Generate a comma separated list of about 10 specific websearch queries related to '{main_topic}' topic that would provide "
            f"comprehensive and interesting content for a podcast. These should cover the most interesting "
            f"aspects of the topic. Do not include '{main_topic}' as it is in the response search queries. "
            f"Make sure to only include the comma separated list of search queries in your response."
        )
        response = self.llm.invoke(prompt)
        topics = [topic.strip() for topic in response.content.split(",")]
        topics = [main_topic] + topics
        print(f"Generated topics: {topics}\n")
        return topics

    def search(self, topics: List[str]) -> Dict[str, List[Dict]]:
        """Perform searches for each topic and combine results."""
        all_results = {"general": [], "news": []}
        #documents = []
        
        for topic in topics:
            print(f"Searching for: {topic}")
            general_results = self.client.search(
                query=topic,
                search_depth="advanced",
                max_results=15
            )
            news_results = self.client.search(
                query=topic,
                topic="news",
                days=30,
                search_depth="advanced",
                max_results=10
            )
            
            # Process results for the dictionary return
            all_results["general"].extend([
                {"title": result["title"], "content": result["content"], "source": "general"}
                for result in general_results["results"]
            ])
            
            all_results["news"].extend([
                {"title": result["title"], "content": result["content"], "source": "news"}
                for result in news_results["results"]
            ])
            
            # Prepare documents for vector store
            # for result in general_results["results"] + news_results["results"]:
            #     documents.append(
            #         f"Title: {result['title']}\n\nContent: {result['content']}"
            #     )
            
            print(f"Found {len(general_results['results'])} general and {len(news_results['results'])} news results")
        
        # # Create vector store from documents
        # print("\nCreating vector store from search results...")
        # self.vectorstore = FAISS.from_texts(
        #     documents,
        #     self.embeddings
        # )
        
        return all_results

class ScriptGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.llm_chain = None
        self.searcher = ContentSearcher()
        
    def extract_concepts(self, topic: str, search_results: Dict[str, List[Dict]]) -> List[Dict]:
        print("\nExtracting key concepts from search results...")
        
        # Combine general and news results into documents
        documents = []
        for result in search_results["general"] + search_results["news"]:
            documents.append(
                f"Title: {result['title']}\n\nSource: {result['source']}\n\nContent: {result['content']}"
            )
            
        # Create vector store from documents
        vectorstore = FAISS.from_texts(
            documents,
            OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        )
        
        self.llm_chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model="gpt-4o", openai_api_key=self.openai_api_key, temperature=0.5),
            retriever=vectorstore.as_retriever(),
        )
        
        prompt = (
            f"""
            Based on the search results and news about {topic}:\n
            Generate a list of around 5 most interesting and important key concepts that should be covered in a podcast episode about {topic}.
            5 is just a suggestion, you can include more or less depending on the topic and the search results. Include the most interesting and important concepts to build a table of contents for the podcast episode.
            Order the concepts to create an engaging flow of information, with the most important and interesting concepts first. 
            Each concept should have a title and a description outlining what should be covered. Focus on both general information and recent news.
            Important: only include a json object containing the concepts titles and descriptions in the following format: 
            {{"concepts": [{{"title": "Concept Title", "description": "Concept Description"}}, ...]}}
            Important: Do not include any other text or comments in your response.
            Important: Property names in the json response object must be enclosed in double quotes.
            """
            #Make sure to incorporate both general knowledge and recent news.
        )
        
        response = self.llm_chain.invoke({"question": prompt, "chat_history": []})
        try:
            concepts = json.loads(response["answer"])
            print("\nExtracted concepts:")
            for i, concept in enumerate(concepts["concepts"]):
                print(f"{i}. {concept['title']}")
            return concepts
        except json.JSONDecodeError as e:
            print(f"Error parsing concepts: {e}")
            print(f"Raw response: {response['answer']}")
            raise
            return []

    def generate_introduction(self, topic: str) -> str:
        print("\nGenerating introduction...")
        
        prompt = (
            f"Generate an engaging introduction for a podcast episode about {topic}. "
            f"The introduction should hook the listener and provide a general overview "
            f"of what will be discussed, without explicitly listing the topics. "
            f"Make it natural and conversational, around 200 words."
            f"Important: The podcast name is 'AI Joe'."
            f"Important: Only include words that can be pronounced by a native English speaker."
        )
        
        response = self.llm_chain.invoke({"question": prompt, "chat_history": []})
        intro = response["answer"]
        print(f"Generated introduction of {len(intro.split())} words")
        return intro

    def expand_concept(self, topic: str, concept: Dict, previous_content: str, total_concepts: int) -> str:
        print(f"\nExpanding concept: {concept['title']}")
        
        
        prompt = (
            f"Your goal is to expand this previously generated podcast script content: {previous_content}\n\n"
            f"Given this concept about {topic}: {concept['title']} - {concept['description']}\n"
            f"Generate a detailed expansion of this concept that flows naturally from the previous content but does not repeat the same information and concepts already covered in the previous content. "
            f"Make it engaging and informative. "
            f"Important: It should be around {round(2100.0/float(total_concepts))} words without repeating the same information and concepts or becoming boring and repetitive. "
            f"Include a smooth transition from the previous content, but don't explicitly announce "
            f"the topic or use phrases like 'now let's talk about' or 'moving on to'."
            f"Important: Only include words that can be pronounced by a native English speaker (e.g. no special characters, no emojis, etc.)."
        )
        
        response = self.llm_chain.invoke({"question": prompt, "chat_history": []})
        content = response["answer"]
        print(f"Generated {len(content.split())} words for this concept")
        return content

    def generate_conclusion(self, topic: str, full_script: str) -> str:
        print("\nGenerating conclusion...")
        
        prompt = (
            f"Generate a conclusion for this podcast episode script about {topic}: {full_script}"
            f"Include: "
            f"1. A summary of key takeaways\n"
            f"2. A motivating statement for listeners to learn more\n"
            f"3. An invitation to future episodes\n"
            f"4. A farewell to listeners\n"
            f"Make it around 200 words and ensure it flows naturally from the script content."
            f"Important: The podcast name is 'AI Joe'."
            f"Important: Only include words that can be pronounced by a native English speaker in the podcast scripts."
        )
        
        response = self.llm_chain.invoke({"question": prompt, "chat_history": []})
        conclusion = response["answer"]
        print(f"Generated conclusion of {len(conclusion.split())} words")
        return conclusion

    def generate(self, topic: str) -> str:
        print(f"\nGenerating podcast script for: {topic}")
        
        search_queries = self.searcher.get_search_queries(topic)
        search_results = self.searcher.search(search_queries)
        # Extract and order key concepts
        concepts = self.extract_concepts(topic, search_results)["concepts"]
        
        # Generate introduction
        print("\nGenerating introduction...")
        script = self.generate_introduction(topic)
        print(f"Introduction length: {len(script.split())} words")

        # Expand concepts one by one until reaching target length
        for i, concept in enumerate(concepts):
            print(f"\nExpanding concept {i}/{len(concepts)}: {concept['title']} - {concept['description']}")
            concept_content = self.expand_concept(topic, concept, script, len(concepts))
            script += f"\n\n{concept_content}"
            
            current_length = len(script.split())
            print(f"Current script length: {current_length} words")
            
            # if current_length >= 2500:
            #     print("Reached target length, stopping concept expansion")
            #     break
        
        # Add conclusion
        print("\nGenerating conclusion...")
        conclusion = self.generate_conclusion(topic, script)
        script += f"\n\n{conclusion}"
        
        final_length = len(script.split())
        print(f"\nFinal script length: {final_length} words")
        return script

if __name__ == "__main__":
    print("Starting podcast script generation")
    topic = input("Enter a topic to generate a podcast script about: ")

    generator = ScriptGenerator()
    podcast_script = generator.generate(topic)
    print("\n" + "="*50)
    print("\nGenerated Podcast Script:\n")
    print(podcast_script)
    print("\n" + "="*50)

