import os
import weaviate
import json
from dotenv import load_dotenv

load_dotenv()
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        # Replace with your inference API key
        "X-HuggingFace-Api-Key": huggingface_api_key
    }
)

# Create a class
class_obj = {
    "class": "Mails",
    "vectorizer": "text2vec-huggingface",
    "description": "EMail data",

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
            "description": "Mail body",
            "moduleConfig": {
                "text2vec-huggingface": {
                    "vectorizePropertyName": True
                }
            },
            "name": "mailBody",
        },
        {
            "dataType": ["text"],
            "description": "Mail subject",
            "name": "mailSubject",
        },
        {
            "dataType": ["text"],
            "description": "Mail from",
            "name": "mailFrom",
        },
    ],
    "vectorIndexType": "hnsw",
}

schema = client.schema.create_class(class_obj)
    
data = (client.query.get("Mails", ["mailBody", "mailSubject"])
        .with_near_text({"concepts": ["Jatin Kshatriya"]})
        .with_limit(1)
      ).do()

print(data)
