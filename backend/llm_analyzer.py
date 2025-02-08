from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import re  # Import regex to extract structured clauses

# Define model name (using TinyLlama for better performance)
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="cpu")

# Create the text-generation pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="cpu")

def analyze_contract(text):
    """Analyze rent agreement text and extract clauses."""
    prompt = f"Extract clauses from this rent agreement:\n\n{text}"

    response = pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)

    generated_text = response[0]['generated_text']
    
    # 🔹 Process text into structured clauses (basic regex-based extraction)
    clauses = re.split(r"\n\d+\.\s", generated_text)  # Assuming LLM returns clauses numbered (1. , 2. , ...)
    clauses = [{"text": clause.strip()} for clause in clauses if clause.strip()]

    print(f"Extracted Clauses: {clauses}")
    return clauses  # ✅ Now returning a list of dictionaries