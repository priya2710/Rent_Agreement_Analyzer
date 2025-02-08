from fastapi import FastAPI, File, UploadFile, HTTPException
import fitz  # PyMuPDF
import os
from llm_analyzer import analyze_contract
from utils import detect_contradictions

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Extract text from the PDF
    text = extract_text_from_pdf(file_path)
    print(f"Extracted text: {text}")

    # Analyze contract using LLM
    clauses = analyze_contract(text)
    print(f"Analyzed contract: {clauses}")

    # Detect contradictions
    contradictions = detect_contradictions(clauses)
    print(f"Clauses: {clauses}")
    print(f"Contradictions: {contradictions}")
    return {
        "clauses": clauses,
        "contradictions": contradictions
    }

def extract_text_from_pdf(file_path):
    print(f"Extracting text from PDF: {file_path}")
    doc = fitz.open(file_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text
