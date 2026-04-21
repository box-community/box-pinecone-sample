<img src="images/box-pinecone.png"
alt= “box-pinecone”
style="margin-left:-10px;"
width=100%;>

# Box and Pinecone Integration Sample

This project demonstrates how to integrate Box and Pinecone via a python script. This coincides with a [blog post](https://medium.com/box-developer-blog/demo-box-pinecone-f03783c412bb) on Medium. Please see that posting for more insructuctions on how to use this solution.

You will need accounts for Box, Pinecone, and OpenAI to appropriate run this demo. You will also need an OAuth Box custom application created in the Box Developer Console.

> [!IMPORTANT]
> Once files leave Box, they are no longer under the protection of Box. It is incumbant upon the developer to ensure proper access rights. In this example, we are using OAuth2 to ensure the user can only access files they have access to, and on the Pinecone side, we are creating a namespace for each user based on their Box user ID, as well as adding their user ID to the metadata. This should ensure only the user can access their vectors.

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/box-community/box-pinecone-sample.git
   ```

   ```bash
   cd box-pinecone-sample

2. Create and activate a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
4. Create config.py file.  

   ```bash
   cp sample_config.py config.py
5. Open the code in an editor of your choice. Update the credentials/Box folder ID with the information you create based on the above linked Medium Post. Save the file.

> [!IMPORTANT]  
> DO NOT input 0 as the folder id. This will attempt to index your entire Box account. Not only is this not recommended, it will exceed rate limits, cost lots of money, and probably break.

6. To create embeddings:

   ```bash
   python main.py
7. To answer queries about the created embeddings:

   ```bash
   python query.py
   ```

## Pinecone Assistant

New to this repository is a Pinecone Assistant demo. It relies on the same configuration as the other examples, so no additional setup is needed for the repo. You will need to make sure you have accessed the [Pinecone Console](https://app.pinecone.io/) and accepted the terms for using assistants.

The example will download the files from the prescribed folder in Box and upload the files to the assistant. You will then have access to a commandline chatbot to ask questions about the files you uploaded. Simply type quit or exit to end the chatbot, at which time the assistant and all the files uploaded will be deleted.

To run:

```bash
python assistant.py
```
