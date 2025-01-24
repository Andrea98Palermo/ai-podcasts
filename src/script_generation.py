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

        return filtered_general_results + filtered_news_results

class ScriptGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

    def generate(self, topic: str, search_results: List[Dict]) -> str:
        """
        Generates a podcast script from the Tavily search results using LangChain.
        Ensures the final script is at least 2,500 words.
        Args:
            topic (str): The topic for the podcast
            search_results (list): A list of dictionaries with titles and contents
        Returns:
            str: The generated podcast script
        """
        combined_texts = [
            f"Title: {result['title']}\nContent: {result['content']}\nSource: {result['source']}"
            for result in search_results
        ]
        
        vectorstore = FAISS.from_texts(
            combined_texts,
            OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        )
        
        chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(
                model="gpt-4",
                openai_api_key=self.openai_api_key
            ),
            retriever=vectorstore.as_retriever()
        )
        
        chat_history = []
        
        query = f"Generate a the first part of a detailed podcast script about {topic}. The script must be a monologue and as long as possible and it must only contain the monologue text, without any additional information (e.g. music, pauses, etc.). Important: It must not contain any conclusion at the end, as the script will be expanded later. NEVER use terms like 'lastly', 'in conclusion', 'finally' or similar ones."
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
                f"Only answer with the expansion to add at the end of the script, not the entire script. It must be a meaningful expansion that starts from where the current script ends."
                f"Important: Don't repeat the same information already present in the current script."
                f"Important: Don't add any conclusion at the end, as the script will be expanded later. NEVER use terms like 'lastly', 'in conclusion', 'finally' or similar ones."
            )
            input_data = {
                "question": query,
                "chat_history": []
            }
            result = chain.invoke(input_data)
            
            new_content = result["answer"]
            podcast_script += f"\n\n{new_content}"

        conclusion_llm = ChatOpenAI(
            model="gpt-4",
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
            f"An explanation of the fact that listeners can vote for the topics for future podcasts by buying and burning the AIPODCAST token, "
            f"An invitation to a final goodbye to the listeners."
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
