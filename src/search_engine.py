"""
Travel Search Engine with RAG
RUBRIC: Search Engine Implementation (13 marks total)
- TravelSearchEngine initialized correctly (4 marks)
- search_by_text performs similarity search (3 marks)
- synthesize_response generates grounded answers (4 marks)
- Governance checks integrated (2 marks)

TASK: Implement RAG search engine with governance integration
"""
import mlflow
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from src.config import Config
from governance.governance_gate import GovernanceGate
from src.vector_store import get_vector_store


class TravelSearchEngine:
    """RAG-powered search engine for travel queries"""

    def __init__(self):
        """
        Initialize search engine components

        Initializes:
        1. Governance gate
        2. Azure Chat OpenAI (LLM)
        3. Azure OpenAI Embeddings
        4. Vector store using get_vector_store
        """
        # Initialize governance gate
        self.governance_gate = GovernanceGate()

        # Initialize Azure Chat OpenAI LLM
        self.llm = AzureChatOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            deployment_name=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=1
        )

        # Initialize Azure OpenAI Embeddings
        self.embeddings = AzureOpenAIEmbeddings(
            api_key=Config.AZURE_OPENAI_API_KEY,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            azure_deployment=Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            api_version=Config.AZURE_OPENAI_API_VERSION,
        )

        # Initialize Vector Store using get_vector_store function
        self.vector_store = get_vector_store(self.embeddings)

    def search_by_text(self, query_text: str, k: int = 5):
        """
        Search for travel information using a text query

        This method:
        1. Sets MLflow experiment
        2. Starts MLflow run
        3. Validates input with governance gate
        4. Performs similarity search on vector store
        5. Logs metrics to MLflow
        6. Returns results and query
        """

        # Set MLflow experiment name from Config
        mlflow.set_experiment(Config.MLFLOW_EXPERIMENT_NAME)

        with mlflow.start_run(run_name="search_travel_info"):
            print(f"DEBUG: Text Query: {query_text}")

            # Validate input using governance gate
            gov_check = self.governance_gate.validate_input(query_text)

            if not gov_check['passed']:
                # Log governance failure event
                mlflow.log_event("GovernanceCheckFailed", {"violations": gov_check['violations']})
                return [], "Query blocked by security checks."

            # Log parameters to MLflow
            mlflow.log_param("k", k)
            mlflow.log_param("query_text", query_text)

            # Perform similarity search on vector store
            docs = self.vector_store.similarity_search(query_text, k=k)

            # Log metric for number of results
            mlflow.log_metric("results_count", len(docs))

            return docs, query_text

    def synthesize_response(self, docs, user_query):
        """
        Generate a conversational response based on retrieved documents

        This method:
        1. Starts MLflow run
        2. Builds context from retrieved documents
        3. Creates a prompt for the LLM
        4. Generates response using LLM
        5. Validates output with governance gate
        6. Logs response to MLflow
        7. Returns final response
        """

        mlflow.set_experiment(Config.MLFLOW_EXPERIMENT_NAME)

        with mlflow.start_run(run_name="synthesize_response"):
            # Handle case when no documents found
            if not docs:
                return "I couldn't find relevant information to answer your question. Please try rephrasing or contact our support team."

            # Build context from documents
            context = "\n".join([
                f"- {doc.page_content} (Source: {doc.metadata.get('source', 'Unknown')})"
                for doc in docs
            ])

            # Create prompt for LLM
            prompt = f"""
            You are a helpful travel assistant for Wanderlust Travels, an online travel agency.
            Use the following information from our knowledge base to answer the customer's question.

            Knowledge Base Information:
            {context}

            Customer Question: "{user_query}"

            Please provide a clear, helpful, and accurate answer based on the information above.
            If the information is not sufficient, let the customer know and provide general guidance.
            """

            # Generate response using LLM
            response = self.llm.invoke(prompt).content

            # Validate output using governance gate
            gov_check = self.governance_gate.validate_output(response)

            if not gov_check['passed']:
                return "I generated a response but it didn't pass safety checks. Please rephrase your question."

            # Log response to MLflow as text file
            mlflow.log_text(response, "final_response.txt")

            return response