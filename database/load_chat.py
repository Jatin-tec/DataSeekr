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

uuid = client.data_object.create({
    "conversation": "Hello, how are you?",
    "chatIndex": 0
}, "Chat")

print(uuid)