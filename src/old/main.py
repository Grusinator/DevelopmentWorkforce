import os
from transformers import AutoModel, AutoTokenizer
from annoy import AnnoyIndex
from typing import List, Dict, Tuple
import llm
import hashlib
import dotenv

dotenv.load_dotenv()

# Load CodeBERT Model
model_name = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Function to generate a unique hash for a file path
def get_file_hash(file_path: str) -> int:
    return int(hashlib.sha256(file_path.encode()).hexdigest(), 16) % 1000000

# Map to store file content
file_content_map: Dict[int, Tuple[str, str]] = {}

def get_code_embedding(code: str):
    inputs = tokenizer(code, return_tensors="pt", max_length=512, truncation=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()

def load_code_to_vector_db(repo_path: str, vector_db: AnnoyIndex):
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code = f.read()
                    embedding = get_code_embedding(code)
                    file_hash = get_file_hash(file_path)
                    vector_db.add_item(file_hash, embedding)
                    file_content_map[file_hash] = (file_path, code)
    vector_db.build(10)

def get_relevant_context(query: str, vector_db: AnnoyIndex, n: int = 5) -> List[Tuple[str, str]]:
    query_embedding = get_code_embedding(query)
    nearest_ids = vector_db.get_nns_by_vector(query_embedding, n)
    return [(file_content_map[id][0], file_content_map[id][1]) for id in nearest_ids]

def prompt_llm_with_context(prompt: str, context: List[Tuple[str, str]], model_name: str = "gpt-3.5-turbo", api_key: str = None):
    # Format the context to include file path and code
    formatted_context = [f"File: {file_path}\n\nCode:\n{code}\n" for file_path, code in context]

    full_prompt = "\n\n".join(formatted_context + [prompt])
    model = llm.get_model(model_name)
    model.key = api_key
    response = model.prompt(full_prompt)
    return response.text()



if __name__ == "__main__":
    repo_path = "C:/Users/willi/repo/dinner_club"
    vector_db = AnnoyIndex(768, 'angular')
    load_code_to_vector_db(repo_path, vector_db)

    model_name = "all-MiniLM-L6-v2-f16"
    api_key = os.getenv("OPENAI_API_KEY")
    query = "how can i test the dinner club app better?"
    context = get_relevant_context(query, vector_db)
    print("\n\nContext:\n")
    print(context)
    response = prompt_llm_with_context(query, context, model_name,api_key)
    print("\n\nResponse:\n")
    print(response)
