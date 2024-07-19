import pytest
from src.old.main import prompt_llm_with_context

def test_prompt_llm_with_context():
    # Test prompt instructing the model to return "Hello, World!"
    test_prompt = "Respond only with: 'Hello, World!'"
    test_context = [("path/to/file1.py", "print('Hello, world!')")]

    # Assuming your model name and API key are set correctly
    model_name = "gpt-3.5-turbo"
    api_key = "your_api_key"

    # Call the function
    response = prompt_llm_with_context(test_prompt, test_context, model_name, api_key)

    # Check if the response is as expected
    assert response == "Hello, World!"
