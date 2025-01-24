from tavily import TavilyClient
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def tavily_search(topic):
    """
    Searches Tavily for information on the given topic using the qna_search method.
    Args:
        topic (str): The topic to search for
    Returns:
        list: A list of dictionaries containing titles and contents from search results
    """
    # Instantiate the Tavily client with your API key
    tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
    
    # Execute the search using qna_search with the specified keyword arguments
    search_general_results = tavily_client.search(
        query=topic,
        search_depth="advanced", 
        max_results=50
    )

    search_news_results = tavily_client.search(
        query=topic,
        topic="news",
        days=30,
        search_depth="advanced", 
        max_results=25
    )
    
    # Extract only titles and contents from the results
    filtered_general_results = [
        {"title": result["title"], "content": result["content"], "source": "general"}
        for result in search_general_results["results"]
    ]

    filtered_news_results = [
        {"title": result["title"], "content": result["content"], "source": "news"}
        for result in search_news_results["results"]
    ]

    combined_results = filtered_general_results + filtered_news_results
        
    return combined_results

def generate_podcast_script(topic, search_results):
    """
    Generates a podcast script from the Tavily search results using LangChain.
    Ensures the final script is at least 2,500 words.
    Args:
        topic (str): The topic for the podcast
        search_results (list): A list of dictionaries with titles and contents
    Returns:
        str: The generated podcast script
    """
    # Combine titles and contents for better context
    combined_texts = [
        f"Title: {result['title']}\nContent: {result['content']}\nSource: {result['source']}"
        for result in search_results
    ]
    
    # Create an embedding store from the search results
    vectorstore = FAISS.from_texts(
        combined_texts,
        OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
    )
    
    # Set up the LangChain Conversational Retrieval Chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(
            model="gpt-4o",
            openai_api_key=os.getenv('OPENAI_API_KEY')
        ),
        retriever=vectorstore.as_retriever()
    )
    
    # Initialize the chat history as a list of tuples
    chat_history = []
    
    # Initial query to generate the script
    query = f"Generate a the first part of a detailed podcast script about {topic}. The script must be a monologue and as long as possible and it must only contain the monologue text, without any additional information (e.g. music, pauses, etc.). Important: It must not contain any conclusion at the end, as the script will be expanded later. NEVER use terms like 'lastly', 'in conclusion', 'finally' or similar ones."
    input_data = {
        "question": query,
        "chat_history": []
    }
    
    # Run the chain to generate the initial script
    result = chain.invoke(input_data)
    podcast_script = result["answer"]
    
    # Ensure the script is at least 2,500 words
    while len(podcast_script.split()) < 2300:
        # Add the current question and answer to chat history
        chat_history.append((query, podcast_script))

        print("--------------------------------")
        print("--------------------------------")
        print(f"Current script length: {len(podcast_script.split())} words")
        print(f"Current script: {podcast_script}")
        print("--------------------------------")
        print("--------------------------------")
        # Update the query to expand the script
        query = (
            f"Given the current podcast script about {topic}: {podcast_script} "
            f"Provide an expansion to add at the end of the script. It must be as long as possible."
            f"Only answer with the expansion to add at the end of the script, not the entire script. It must be a meaningful expansion that starts from where the current script ends."
            f"Important: Don't repeat the same information already present in the current script."
            f"Important: Don't add any conclusion at the end, as the script will be expanded later. NEVER use terms like 'lastly', 'in conclusion', 'finally' or similar ones."
        )
        input_data = {
            "question": query,
            "chat_history": [],
            #"chat_history": chat_history
        }
        result = chain.invoke(input_data)
        
        new_content = result["answer"]
        
        # Append new content to the script
        podcast_script += f"\n\n{new_content}"

    # Create a separate ChatOpenAI instance for the conclusion query with a custom temperature
    conclusion_llm = ChatOpenAI(
        model="gpt-4",
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.9  # Set a higher temperature for a more creative conclusion
    )

    # Use the conclusion-specific LLM with a new chain
    conclusion_chain = ConversationalRetrievalChain.from_llm(
        llm=conclusion_llm,
        retriever=vectorstore.as_retriever()  # Use the same retriever as the main chain
    )

    # Define the conclusion query
    query = (
        f"Given the current podcast script about {topic}: {podcast_script} "
        f"Provide a conclusion to the script of at least 200 words. "
        f"It must contain: "
        f"A conclusive summary of the key takeaways of the script, "
        f"A final cheering statement that motivates the listener to learn more about the topic, "
        f"An explanation of the fact that listeners can vote for the topics for future podcasts by buying and burning the AIPODCAST token, "
        f"An invitation to a final goodbye to the listeners."
    )

    # Prepare input data for the conclusion query
    input_data = {
        "question": query,
        "chat_history": []  # No chat history needed for the conclusion query
    }

    # Invoke the conclusion chain
    result = conclusion_chain.invoke(input_data)
    conclusion = result["answer"]

    # Append the conclusion to the podcast script
    podcast_script += f"\n\n{conclusion}"

    
    return podcast_script




if __name__ == "__main__":
    # Get the topic from user input
    topic = input("Enter a topic to generate a podcast script about: ")
    
    # Perform a search using Tavily
    search_results = tavily_search(topic)
    
    if search_results:
        # Generate the podcast script
        podcast_script = generate_podcast_script(topic, search_results)
        print("\nGenerated Podcast Script:\n")
        print(podcast_script)
    else:
        print("No search results found for the given topic.")
