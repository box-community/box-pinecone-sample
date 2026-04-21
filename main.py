"""main.py"""

from box_integration.box_integration import get_files_in_folder, get_file_text_content
from pinecone_integration.pinecone_client import get_pinecone_index, store_metadata_in_pinecone
import config
import logging
from box_integration.box_client import get_client
import traceback

log_level = getattr(logging, getattr(config, "LOG_LEVEL", "INFO").upper(), logging.ERROR)
logging.basicConfig(level=log_level)
logging.getLogger("box-pinecone-integration")

def main():
    """
    Main function to process files from a Box folder, extract text and metadata, and store them in a Pinecone index.
    """
    # Initialize Box client
    logging.info("Initializing Box client")
    box_client = get_client()

    # Get Box User ID for namespacing
    logging.info("Getting Box user ID")
    box_user = box_client.user().get()
    
    # Initialize Pinecone client
    pinecone_index = get_pinecone_index()
    
    # Define the Box folder ID containing the files
    logging.info("Defining Box folder ID")
    folder_id = config.BOX_FOLDER_ID
    
    # Get all files in the specified folder (including subfolders)
    logging.info("Getting all files in the specified folder tree")
    files = get_files_in_folder(box_client, folder_id)
    if not files:
        logging.warning(
            "No supported files found under folder %s. The script only indexes "
            "certain extensions in that folder tree, or the tree may contain only "
            "subfolders with no matching documents. Adjust BOX_FOLDER_ID or add files.",
            folder_id,
        )
        return

    # Process each file
    ok = 0
    for file in files:
        try:
            logging.info(f"Processing file: {file.name}")
            # Extract text content from the file representation
            text_content = get_file_text_content(box_client, file)
            
            # Extract metadata from the file object
            metadata = {
                "file_name": file.name,
                "file_id": file.id,
                "created_at": file.created_at,
                "modified_at": file.modified_at,
                "size": file.size,
                "box_user_id": box_user.id
            }
            
            # Combine text content with metadata for vectorization
            combined_text = text_content + " " + " ".join(f"{key}: {value}" for key, value in metadata.items())
            logging.debug(f"Text: {combined_text}")
            # Store the vectorized representation and metadata in Pinecone
            logging.info(f"Storing metadata in Pinecone for file: {file.name}")
            store_metadata_in_pinecone(pinecone_index, file.id, {"text": combined_text, **metadata}, box_user.id)
            
            logging.info(f"Processed and stored metadata for file: {file.name}")
            ok += 1

        except Exception as e:
            logging.error(f"Failed to process file {file.name}: {e}")
            logging.error(traceback.format_exc())

    logging.info(
        "Finished: successfully stored vectors for %d of %d file(s).",
        ok,
        len(files),
    )

if __name__ == "__main__":
    main()
