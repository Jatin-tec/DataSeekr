import weaviate
import os
from dotenv import load_dotenv

load_dotenv()
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        "X-HuggingFace-Api-Key": huggingface_api_key
    }
)

batch_size = 1000
class_name = "Mails"
class_properties = ["mailBody"]
cursor = None

query = (
    client.query.get(class_name, class_properties)
    .with_additional(["id vector"])
    .with_limit(batch_size)
)

print(len(query.do()["data"]["Get"][class_name]))