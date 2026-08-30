
import sys
from pathlib import Path
import csv

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ml.preprocessing import preprocess_text
from ml.sentiment import analyze_sentiment


app = FastAPI()


# Allow the React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Employee Wellness Backend is running"
    }


# Analyze text entered directly in the website
@app.post("/analyze")
def analyze(data: dict):
    text = data.get("text", "")

    # Validate empty text
    if not text.strip():
        return {
            "status": "error",
            "message": "Text cannot be empty"
        }

    # Preprocess the text
    cleaned_text = preprocess_text(text)

    # Analyze sentiment
    sentiment_result = analyze_sentiment(cleaned_text)

    return {
        "status": "success",
        "message": "Text successfully passed through preprocessing and sentiment analysis",
        "original_text": text,
        "preprocessed_text": cleaned_text,
        "sentiment": sentiment_result
    }


# Analyze an uploaded .txt file
@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):

    filename = file.filename.lower()

    # Allow only TXT and CSV files
    if not (filename.endswith(".txt") or filename.endswith(".csv")):
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .csv files are supported"
        )

    # Read uploaded file
    content = await file.read()

    # Convert bytes to text
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file must use UTF-8 text encoding"
        )

    # Process CSV file
    if filename.endswith(".csv"):

        lines = []

        try:
            reader = csv.DictReader(text.splitlines())

            if not reader.fieldnames:
                raise HTTPException(
                    status_code=400,
                    detail="CSV file must contain a header row"
                )

            if "feedback" not in reader.fieldnames:
                raise HTTPException(
                    status_code=400,
                    detail="CSV must contain a 'feedback' column"
                )

            for row in reader:
                feedback = row.get("feedback", "")

                if feedback and feedback.strip():
                    lines.append(feedback.strip())

        except HTTPException:
            raise

        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid CSV format"
            )

        text = " ".join(lines)

    # Check empty content
    if text.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Uploaded file contains no valid text"
        )

    # Preprocess text
    cleaned_text = preprocess_text(text)

    # Sentiment analysis
    sentiment_result = analyze_sentiment(cleaned_text)

    return {
        "status": "success",
        "filename": file.filename,
        "original_text": text,
        "preprocessed_text": cleaned_text,
        "sentiment": sentiment_result
    }