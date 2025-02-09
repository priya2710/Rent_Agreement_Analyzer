import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("HF_API_TOKEN")  # Get token from environment variable
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"

def classify_clause(clause):
    """Classifies clause as favorable to Lessor, Lessee, or neutral."""
    
    classification_prompt = f"Classify this rental agreement clause as 'Favorable to Lessor', 'Favorable to Lessee', or 'Neutral'. Provide a reason why:\n\nClause: {clause}"
    
    payload = {
        "inputs": classification_prompt,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7,
            "do_sample": True
        }
    }
    
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        response_json = response.json()
        if response_json and isinstance(response_json, list) and "generated_text" in response_json[0]:
            return response_json[0]["generated_text"]
    
    return "Classification failed"

def analyze_contract(text):
    """Analyze rent agreement text and extract clauses with classification."""
    
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
            
            # Classify each clause
            for clause in clauses:
                classification = classify_clause(clause["text"])
                clause["classification"] = classification
            
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