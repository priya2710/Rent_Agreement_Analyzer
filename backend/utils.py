import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("HF_API_TOKEN")  # Get token from environment variable
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# Hugging Face API for contradiction detection
NLI_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"

def query_huggingface_api(payload, max_retries=5, initial_wait=2):
    """Send a request to the Hugging Face API with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.post(NLI_API_URL, headers=HEADERS, json=payload)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code in [429, 503]:  # Too many requests or service unavailable
                wait_time = initial_wait * (2 ** attempt)  # Exponential backoff
                print(f"API busy (status {response.status_code}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"API error (status {response.status_code}): {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            time.sleep(initial_wait)
    print("Max retries reached. Could not get a valid response.")
    return None

def detect_contradictions(texts):
    """Detect contradictions in rent agreement clauses using an NLI model with retry logic."""
    
    if isinstance(texts, dict):  
        texts = list(texts.values())  

    extracted_texts = []
    for text in texts:
        if isinstance(text, dict):
            extracted_texts.append(" ".join(str(value) for value in text.values()))
        elif isinstance(text, str):
            extracted_texts.append(text)

    texts = [text.strip() for text in extracted_texts if text.strip()]
    
    if len(texts) < 2:
        return []  # Need at least two clauses to check contradictions

    contradictions = []

    # Compare each clause with every other clause
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            text1 = texts[i]
            text2 = texts[j]

            # Prepare API request
            payload = {
                "inputs": f"{text1} [SEP] {text2}",
                "parameters": {
                    "candidate_labels": ["contradiction", "entailment", "neutral"]
                }
            }

            result = query_huggingface_api(payload)

            if result and "labels" in result and "scores" in result:
                label_scores = dict(zip(result["labels"], result["scores"]))
                
                # If the model predicts "contradiction" with high confidence
                if label_scores.get("contradiction", 0) > 0.8:
                    contradictions.append({
                        "Clause 1": text1,
                        "Clause 2": text2,
                        "Confidence": label_scores["contradiction"]
                    })

    return contradictions