from fastapi import FastAPI, File, UploadFile, HTTPException
import fitz
import os
from llm_analyzer import analyze_contract
from utils import detect_contradictions

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Extract text from the PDF
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Empty or unreadable PDF content.")

        # Analyze contract using LLM
        clauses = analyze_contract(text)
        if not clauses:
            raise HTTPException(status_code=500, detail="Failed to extract clauses from the document.")

        # Detect contradictions
        contradictions = detect_contradictions(clauses)
        return {
            "clauses": clauses,
            "contradictions": contradictions
        }

    except HTTPException as e:
        return {"error": str(e.detail)}

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {"error": "An unexpected error occurred."}

def extract_text_from_pdf(file_path):
    try:
        print(f"Extracting text from PDF: {file_path}")
        doc = fitz.open(file_path)
        text = "\n".join([page.get_text("text") for page in doc])

        if not text.strip():
            raise ValueError("Extracted text is empty.")

        return text

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""