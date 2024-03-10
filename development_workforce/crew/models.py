import os

from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_community.llms.ollama import Ollama
from langchain_openai import ChatOpenAI

ollama_instruct = Ollama(
    model=os.getenv("OLLAMA_MODEL_NAME"),
    base_url=os.getenv("OLLAMA_API_BASE")
)
ollama_python = Ollama(
    model=os.getenv("OLLAMA_MODEL_NAME_2"),
    base_url=os.getenv("OLLAMA_API_BASE_2")
)
chatgpt = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name=os.getenv("OPENAI_MODEL_NAME"),
)
hugging_face = HuggingFaceEndpoint(
    endpoint_url=os.getenv("HUGGINGFACE_API_BASE"),
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY"),
    task="text-generation",
    model_kwargs={
        "max_new_tokens": 2000,  # Adjust based on input size to keep total under 1024
        # "top_k": 50,
        # "temperature": 0.2,
        "repetition_penalty": 1.1,
        "max_length": 4000,  # Ensure input + max_new_tokens <= 1024
    }
)


def get_llm(llm_name):
    llm_mapping = {
        "ollama_instruct": ollama_instruct,
        "ollama_python": ollama_python,
        "chatgpt": chatgpt,
        "hugging_face": hugging_face
    }
    llm = llm_mapping.get(llm_name)
    if llm is None:
        raise ValueError(f"Invalid llm_name: {llm_name}")


default_llm = chatgpt
developer_llm = default_llm
