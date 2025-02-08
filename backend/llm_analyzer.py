import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("HF_API_TOKEN")  # Get token from environment variable
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"

def analyze_contract(text):
    """Analyze rent agreement text and extract clauses using Hugging Face API."""
    
    if not text or not isinstance(text, str):
        print("Error: Invalid text input. Text must be a non-empty string.")
        return []

    try:
        print(f"Analyzing contract: {text}")
        prompt = f"Extract clauses from this rent agreement:\n\n{text}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 300,
                "temperature": 0.7,
                "do_sample": True
            }
        }

        response = requests.post(API_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            response_json = response.json()
            if not response_json or not isinstance(response_json, list) or "generated_text" not in response_json[0]:
                print("Error: Unexpected API response format.")
                return []

            generated_text = response_json[0]["generated_text"]
            clauses = re.split(r"\n\d+\.\s", generated_text)  # Assuming LLM returns numbered clauses
            clauses = [{"text": clause.strip()} for clause in clauses if clause.strip()]
            return clauses

        else:
            print(f"Error: API request failed with status {response.status_code}, Response: {response.text}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return []

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return []