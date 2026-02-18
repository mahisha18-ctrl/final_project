"""
Configuration Management
RUBRIC: Environment Setup & Configuration (8 marks total)
- Azure OpenAI credentials configured correctly (1 mark)
- Azure AI Search credentials set up properly (1 mark)
- config.py implemented with validation (3 marks)
- All required packages installed and imported without errors (3 marks)

TASK: Load all configuration from environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration for Wanderlust Travel Chatbot"""
    
    # ====================
    # Azure OpenAI Configuration
    # ====================
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    
    # ====================
    # Azure AI Search Configuration
    # ====================
    AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
    AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "travel-kb-index")
    
    # ====================
    # Azure Storage (Optional)
    # ====================
    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "travel-documents")
    
    # ====================
    # Azure Content Safety (Optional)
    # ====================
    AZURE_CONTENT_SAFETY_ENDPOINT = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT")
    AZURE_CONTENT_SAFETY_KEY = os.getenv("AZURE_CONTENT_SAFETY_KEY")
    
    # ====================
    # Azure Monitor (Optional)
    # ====================
    APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    # ====================
    # MLflow Configuration
    # ====================
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
    MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "wanderlust-travel-chatbot")
    
    # ====================
    # Ingestion Settings
    # ====================
    INGESTION_LIMIT = int(os.getenv("INGESTION_LIMIT", "0"))