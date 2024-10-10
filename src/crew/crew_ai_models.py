import os

from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_community.llms.ollama import Ollama
from langchain_openai import ChatOpenAI


class CrewAiModels:
    # ollama_instruct = Ollama(
    #     model=os.getenv("OLLAMA_MODEL_NAME"),
    #     base_url=os.getenv("OLLAMA_API_BASE")
    # )
    # ollama_python = Ollama(
    #     model=os.getenv("OLLAMA_MODEL_NAME_2"),
    #     base_url=os.getenv("OLLAMA_API_BASE_2")
    # )
    chatgpt = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=os.getenv("OPENAI_MODEL_NAME"),
    )
    # hugging_face = HuggingFaceEndpoint(
    #     endpoint_url=os.getenv("HUGGINGFACE_API_BASE"),
    #     huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY"),
    #     task="text-generation",
    #     max_new_tokens=2000,  # Moved from model_kwargs
    #     repetition_penalty=1.1,  # Moved from model_kwargs
    #     model_kwargs={
    #         "max_length": 4000,  # This can stay in model_kwargs
    #     }
    # )

    @classmethod
    def get_llm(cls, llm_name):
        llm_mapping = {
            # "ollama_instruct": cls.ollama_instruct,
            # "ollama_python": cls.ollama_python,
            "chatgpt": cls.chatgpt,
            # "hugging_face": cls.hugging_face
        }
        llm = llm_mapping.get(llm_name)
        if llm is None:
            raise ValueError(f"Invalid llm_name: {llm_name}")
        return llm

    default_llm = chatgpt
    developer_llm = default_llm