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

batch_size = 100
class_name = "Mails"
class_properties = ["mailBody", "mailSubject"]
cursor = None

# query = (
#     client.query.get(class_name, class_properties)
#     .with_additional(["id vector"])
#     .with_limit(batch_size)
# )
# print(len(query.do()["data"]["Get"]["Mails"]))

class_name = "Chat"
class_properties = ['conversation', 'chatIndex']
cursor = None

query = (
    client.query.get(class_name, class_properties)
    .with_additional(["id vector"])
    .with_limit(batch_size)
)
print(query.do()["data"]["Get"]["Chat"])