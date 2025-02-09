from fastapi import FastAPI, File, UploadFile, HTTPException
import fitz  # PyMuPDF for PDF handling
import os
from llm_analyzer import analyze_contract
from utils import detect_contradictions
from fastapi.middleware.cors import CORSMiddleware
from docx import Document  # For DOCX file handling

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
        # Validate file type
        if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx") or file.filename.endswith(".txt")):
            raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are allowed.")

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Extract text based on file type
        if file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif file.filename.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        elif file.filename.endswith(".txt"):
            text = extract_text_from_txt(file_path)

        if not text.strip():
            raise HTTPException(status_code=400, detail="Empty or unreadable document content.")

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
    """Extracts text from a PDF file."""
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

def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file."""
    try:
        print(f"Extracting text from DOCX: {file_path}")
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])

        if not text.strip():
            raise ValueError("Extracted text is empty.")

        return text

    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_txt(file_path):
    """Extracts text from a TXT file."""
    try:
        print(f"Extracting text from TXT: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        if not text.strip():
            raise ValueError("Extracted text is empty.")

        return text

    except Exception as e:
        print(f"Error extracting text from TXT: {e}")
        return ""