from typing import List, Dict
from tavily import TavilyClient
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ContentSearcher:
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

    def search(self, topic: str) -> List[Dict]:
        """
        Searches Tavily for information on the given topic using the qna_search method.
        Args:
            topic (str): The topic to search for
        Returns:
            list: A list of dictionaries containing titles and contents from search results
        """
        search_general_results = self.client.search(
            query=topic,
            search_depth="advanced", 
            max_results=50
        )

        search_news_results = self.client.search(
            query=topic,
            topic="news",
            days=30,
            search_depth="advanced", 
            max_results=25
        )
        
        filtered_general_results = [
            {"title": result["title"], "content": result["content"], "source": "general"}
            for result in search_general_results["results"]
        ]

        filtered_news_results = [
            {"title": result["title"], "content": result["content"], "source": "news"}
            for result in search_news_results["results"]
        ]

        return {"general": filtered_general_results, "news": filtered_news_results}

class ScriptGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

    def generate(self, topic: str, search_results: Dict[str, List[Dict]]) -> str:
        """
        Generates a podcast script from the Tavily search results using LangChain.
        Ensures the final script is at least 2,500 words.
        Args:
            topic (str): The topic for the podcast
            search_results (list): A list of dictionaries with titles and contents
        Returns:
            str: The generated podcast script
        """
        general_texts = [
            f"Title: {result['title']}\nContent: {result['content']}\nSource: {result['source']}"
            for result in search_results["general"]
        ]

        news_texts = [
            f"Title: {result['title']}\nContent: {result['content']}\nSource: {result['source']}"
            for result in search_results["news"]
        ]
        
        vectorstore = FAISS.from_texts(
            general_texts + news_texts,
            OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        )
        
        chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(
                model="gpt-4o",
                openai_api_key=self.openai_api_key
            ),
            retriever=vectorstore.as_retriever()
        )
        
        chat_history = []
        
        query = (
            f"Generate the first section of a detailed script for a podcast episode about {topic}. "
            f"These are web search results about {topic}: {general_texts}. "
            f"These are the news of the last 30 days about {topic}: {news_texts}. "
            f"The script must be a monologue and as long as possible and it must only contain the monologue text, "
            f"without any additional information (e.g. music, pauses, etc.). "
            f"Important: It must not contain any conclusion at the end, as the script will be expanded later. "
            f"Important: NEVER use terms like 'lastly', 'in conclusion', 'finally' or similar ones. "
            f"Important: Don't add any transitions, references to upcoming content, or phrases like "
            f"'stay tuned', 'coming up', or 'we'll explore later'. "
            f"This first section should flow naturally into the next without announcing future content. "
            f"Never refer to sections in the script."
        )
        input_data = {
            "question": query,
            "chat_history": []
        }
        
        result = chain.invoke(input_data)
        podcast_script = result["answer"]
        
        while len(podcast_script.split()) < 2300:
            chat_history.append((query, podcast_script))

            print("--------------------------------")
            print(f"Current script length: {len(podcast_script.split())} words")
            print("--------------------------------")

            query = (
                f"Given the current podcast script about {topic}: {podcast_script} "
                f"Provide an expansion to add at the end of the script. It must be as long as possible."
                f"These are web search results about {topic}: {general_texts}. "
                f"These are the news of the last 30 days about {topic}: {news_texts}. "
                f"Only answer with the expansion to add at the end of the script, not the entire script. "
                f"It must be a meaningful expansion that starts from where the current script ends. "
                f"Important: Don't repeat the same information and concepts already present in the current script. "
                f"Important: Don't add any conclusion at the end, as the script will be expanded later. NEVER use terms like 'lastly', 'in conclusion', 'finally' or similar ones."
                f"Important: Don't add any transitions, references to upcoming content, or phrases like 'stay tuned', 'coming up', or 'we'll explore later'. This section should flow naturally into the next without announcing future content. Never refer to sections in the script."
            )
            input_data = {
                "question": query,
                "chat_history": []
            }
            result = chain.invoke(input_data)
            
            new_content = result["answer"]
            podcast_script += f"\n\n{new_content}"

        conclusion_llm = ChatOpenAI(
            model="gpt-4o",
            openai_api_key=self.openai_api_key,
            temperature=0.9
        )

        conclusion_chain = ConversationalRetrievalChain.from_llm(
            llm=conclusion_llm,
            retriever=vectorstore.as_retriever()
        )

        query = (
            f"Given the current podcast script about {topic}: {podcast_script} "
            f"Provide a conclusion to the script of at least 200 words. "
            f"It must contain: "
            f"A conclusive summary of the key takeaways of the script, "
            f"A final cheering statement that motivates the listener to learn more about the topic, "
            f"An invitation to stay tuned for future episodes,"
            f"A final goodbye to the listeners."
        )

        input_data = {
            "question": query,
            "chat_history": []
        }

        result = conclusion_chain.invoke(input_data)
        conclusion = result["answer"]
        podcast_script += f"\n\n{conclusion}"
        
        return podcast_script

if __name__ == "__main__":
    # Get the topic from user input
    topic = input("Enter a topic to generate a podcast script about: ")
    
    # Perform a search using Tavily
    searcher = ContentSearcher()
    search_results = searcher.search(topic)
    
    if search_results:
        # Generate the podcast script
        generator = ScriptGenerator()
        podcast_script = generator.generate(topic, search_results)
        print("\nGenerated Podcast Script:\n")
        print(podcast_script)
    else:
        print("No search results found for the given topic.")
