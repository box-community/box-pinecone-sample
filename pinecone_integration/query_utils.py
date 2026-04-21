import config
from pinecone import Pinecone
import logging

logging.getLogger("pinecone")

def initialize_pinecone_client():
    pinecone = Pinecone(
        api_key=config.PINECONE_API_KEY, 
        source_tag="box_pinecone_integration"
    )
    return pinecone

def query_pinecone(index, query_text, box_user_id, top_k=50):
    """
    Queries the Pinecone index with the given query text and retrieves the top_k results.

    Parameters:
    - index: The Pinecone index to search in.
    - query_text: The text of the query to search for in the index.
    - box_user_id: The namespace identifier for the Box user, used to scope the search.
    - top_k: The number of top results to retrieve from the index (default is 50).

    Returns:
    - A list of query results from the Pinecone index, including the top_k results based on the query text.
    """
    logging.info(f"Querying Pinecone with query: {query_text}")
    # Reranking (e.g. cohere-rerank-3.5) requires separate model entitlements on
    # the Pinecone project; omit by default so search works for all accounts.
    query_results = index.search(
        namespace=box_user_id,
        query={
            "inputs": {"text": query_text},
            "top_k": top_k,
        },
        fields=["chunk_text"],
    )

    return query_results
