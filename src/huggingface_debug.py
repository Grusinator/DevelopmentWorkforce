import os

from dotenv import load_dotenv
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
import requests

load_dotenv()

API_URL = os.getenv("HUGGINGFACE_API_BASE")
API_KEY = os.getenv("HUGGINGFACE_API_KEY")

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


output = query({
    "inputs": "Can you please let us know more details about your API?",
    "parameters": {}
})
print(output)

hugging_face = HuggingFaceEndpoint(
    endpoint_url=API_URL,
    huggingfacehub_api_token=API_KEY
)
