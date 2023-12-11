import os
from dotenv import load_dotenv
import weaviate

load_dotenv()

API_TOKEN = os.getenv("HUGGINGFACE_APIKEY")

client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        "X-HuggingFace-Api-Key": API_TOKEN
    }
)

# Create chat class
chat_class_obj = {
        "class": "Chat",
        "vectorizer": "text2vec-huggingface",
        "description": "Chat History",

        "moduleConfig": {
            "text2vec-huggingface": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "options": {
                    "waitForModel": True
                }
            }
        },

        "properties": [
            {
                "dataType": ["text"],
                "description": "Conversation Chunk",
                "moduleConfig": {
                    "text2vec-huggingface": {
                        "vectorizePropertyName": True
                    }
                },
                "name": "conversation",
            },
            {
                "dataType": ["int"],
                "description": "Chat Index",
                "name": "chatIndex",
            }
        ],
        "vectorIndexType": "hnsw",
    }

if client.schema.exists("Chat"):
    client.schema.delete_class("Chat")
    client.schema.create_class(chat_class_obj)
else:
    client.schema.create_class(chat_class_obj)
