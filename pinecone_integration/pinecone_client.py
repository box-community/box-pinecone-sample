import config
from pinecone import (
    Pinecone,
    CloudProvider,
    AwsRegion,
    EmbedModel,
    IndexEmbed
)
import logging

log_level = getattr(logging, getattr(config, "LOG_LEVEL", "INFO").upper(), logging.ERROR)
logging.basicConfig(level=log_level)
logging.getLogger("pinecone")

def initialize_pinecone_client():
    """
    Initializes and returns a Pinecone client using the API key from the configuration.

    Returns:
    - A Pinecone client instance.
    """
    logging.info("Initializing Pinecone client")
    pinecone = Pinecone(
        api_key=config.PINECONE_API_KEY, 
        source_tag="box_pinecone_integration"
    )
    logging.info("Pinecone client initialized")
    return pinecone


def get_pinecone_index():
    """
    Retrieves or creates a Pinecone index based on the configuration.

    Returns:
    - A Pinecone index instance.
    """
    pinecone_client = initialize_pinecone_client()
    index_name = config.PINECONE_INDEX or "box-integration-example"
    logging.info(f"Checking if index {index_name} exists")
    try:
        if not pinecone_client.has_index(index_name):
            logging.debug(f"Index {index_name} does not exist, creating it")
            create_index(pinecone_client, index_name)
            logging.debug(f"Index {index_name} created")
        else:
            logging.debug(f"Index {index_name} already exists")
    except Exception as e:
        logging.error(f"Error checking if index {index_name} exists: {e}")
        exit(1)
    return pinecone_client.Index(index_name)


def create_index(client, index_name):
    """
    Creates a Pinecone index with the specified name and configuration.

    Parameters:
    - client: The Pinecone client used to create the index.
    - index_name: The name of the index to create.
    """
    client.create_index_for_model(
        name=index_name,
        cloud=CloudProvider.AWS,
        region=AwsRegion.US_EAST_1,
        embed=IndexEmbed(
            model=EmbedModel.Multilingual_E5_Large,
            field_map={"text": "chunk_text"},
            metric="cosine"
        )
    )


def chunk_text(text, chunk_size=4000, overlap=200):
    """
    Splits the given text into chunks of specified size with overlap.

    Parameters:
    - text: The text to be chunked.
    - chunk_size: The size of each chunk (default is 4000).
    - overlap: The number of overlapping characters between chunks (default is 200).

    Returns:
    - A list of text chunks.
    """
    if not text or len(text) == 0:
        logging.error("No text to chunk")
        return []
    logging.info(f"Chunking text with chunk_size: {chunk_size} and overlap: {overlap}")
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # Overlap adjustment
    logging.debug(f"Chunks: {len(chunks)}")
    return chunks


def store_metadata_in_pinecone(index, file_id, combined_text, box_user_id, upsert_batch_size=96):
    """
    Stores metadata and chunked text in the Pinecone index.

    Parameters:
    - index: The Pinecone index to store the data in.
    - file_id: The ID of the file being processed.
    - combined_text: A dictionary containing the text and metadata to store.
    - box_user_id: The namespace identifier for the Box user.
    - upsert_batch_size: The number of records to upsert in a single batch (default is 96).
    """
    if not index:
        logging.error("Pinecone index not initialized")
        exit(1)

    # Ensure combined_text["text"] is not None
    text_content = combined_text.get("text")
    if text_content is None:
        logging.error(f"No text representation available for file ID: {file_id}")
        return

    # Chunk the text with overlap
    logging.info(f"Chunking text for file ID: {file_id}")
    text_chunks = chunk_text(text_content, chunk_size=2000, overlap=100)
    logging.info(f"Chunked text into {len(text_chunks)} chunks")

    records = []
    for i, chunk in enumerate(text_chunks):
        logging.debug(f"Processing chunk {i}")
        # Integrated index uses field_map {"text": "chunk_text"} (see create_index):
        # Pinecone requires the source field "text" for embedding; "chunk_text" is kept
        # for search and matches query_utils fields=["chunk_text"].
        minimal_metadata = {
            "chunk_id": i,
            "file_id": file_id,
            "file_name": combined_text.get("file_name"),
            "created_at": combined_text.get("created_at"),
            "modified_at": combined_text.get("modified_at"),
            "size": combined_text.get("size", 0),
            "box_user_id": box_user_id,
            "text": chunk,
            "chunk_text": chunk,
        }
        if len(records) < upsert_batch_size:
            logging.debug(f"Adding record {file_id}_chunk_{i} to records list")
            records.append(
                {
                    "_id": f"{file_id}_chunk_{i}", 
                    **minimal_metadata
                }
            )
        else:
            logging.debug(f"Upserting {len(records)} records")
            index.upsert_records(
            namespace=box_user_id,
            records=records,
        )
            records = []

    # Upsert the remaining records
    if records:
        logging.debug(f"Upserting {len(records)} records")
        index.upsert_records(
            namespace=box_user_id,
            records=records,
        )