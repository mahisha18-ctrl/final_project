import os
from dotenv import load_dotenv
load_dotenv()
from langchain_community.vectorstores import AzureSearch

def get_vector_store(embedding_function):
    # Read directly from env to avoid Config caching issue
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "travel-kb-index")

    # Validate credentials
    if not endpoint or not key:
        raise ValueError("AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY must be set.")
    
    if not index_name:
        raise ValueError("AZURE_SEARCH_INDEX_NAME must be set.")

    # Initialize AzureSearch vector store
    vector_store = AzureSearch(
        azure_search_endpoint=endpoint,
        azure_search_key=key,
        index_name=index_name,
        embedding_function=embedding_function.embed_query
    )

    print(f"Initialized Azure AI Search (LangChain) for index '{index_name}'")
    return vector_store
