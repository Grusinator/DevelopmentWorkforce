import os
from src.ado_integrations.ado_tools import ado_tools

from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()



import requests

API_URL = "https://f9uundmw4bnxj2mu.eu-west-1.aws.endpoints.huggingface.cloud"
headers = {
	"Accept" : "application/json",
	"Authorization": "Bearer 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",
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

from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint

hugging_face = HuggingFaceEndpoint(
    endpoint_url=os.getenv("HUGGINGFACE_API_BASE"), 
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY")
    )