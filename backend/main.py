import sys
from pathlib import Path
import csv

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# ADD PROJECT ROOT TO PYTHON PATH
# ============================================================

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)


# ============================================================
# IMPORT ML MODULES
# ============================================================

from ml.preprocessing import preprocess_text

from ml.sentiment import analyze_sentiment

from ml.emotion import analyze_emotion

from ml.multilabel_emotion import (
    analyze_multilabel_emotion
)

from ml.emotion_intensity import (
    analyze_emotional_state
)

from ml.wellness import (
    generate_wellness_insight
)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI()


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# HOME ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {
        "message":
            "Employee Wellness Backend is running"
    }


# ============================================================
# ANALYZE DIRECT TEXT
# ============================================================

@app.post("/analyze")
def analyze(data: dict):

    # --------------------------------------------------------
    # Get text
    # --------------------------------------------------------

    text = data.get(
        "text",
        ""
    )


    # --------------------------------------------------------
    # Validate empty text
    # --------------------------------------------------------

    if not text.strip():

        return {

            "status": "error",

            "message":
                "Text cannot be empty"
        }


    # --------------------------------------------------------
    # Step 1: Preprocess
    # --------------------------------------------------------

    cleaned_text = preprocess_text(
        text
    )


    # --------------------------------------------------------
    # Step 2: Sentiment
    # --------------------------------------------------------

    sentiment_result = analyze_sentiment(
        cleaned_text
    )


    # --------------------------------------------------------
    # Step 3: BERT emotion
    # --------------------------------------------------------

    emotion_result = analyze_emotion(
        text
    )


    # --------------------------------------------------------
    # Step 4: Multi-label emotion
    # --------------------------------------------------------

    multilabel_emotion_result = (
        analyze_multilabel_emotion(
            text
        )
    )


    # --------------------------------------------------------
    # Step 5: Emotional state and intensity
    # --------------------------------------------------------

    emotional_state_result = (
        analyze_emotional_state(
            multilabel_emotion_result[
                "emotion_scores"
            ]
        )
    )


    # --------------------------------------------------------
    # Step 6: Wellness analysis
    # --------------------------------------------------------

    wellness_result = generate_wellness_insight(
        sentiment_result,
        emotion_result
    )


    # --------------------------------------------------------
    # Return complete analysis
    # --------------------------------------------------------

    return {

        "status":
            "success",

        "message":
            (
                "Text successfully passed through "
                "preprocessing, sentiment analysis, "
                "emotion analysis, multi-label emotion "
                "analysis, emotional intensity analysis "
                "and wellness analysis"
            ),

        "original_text":
            text,

        "preprocessed_text":
            cleaned_text,

        "sentiment":
            sentiment_result,

        "emotion":
            emotion_result,

        "multilabel_emotion":
            multilabel_emotion_result,

        "emotional_state":
            emotional_state_result,

        "wellness":
            wellness_result
    }


# ============================================================
# ANALYZE UPLOADED TXT / CSV FILE
# ============================================================

@app.post("/analyze-file")
async def analyze_file(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Get filename
    # --------------------------------------------------------

    filename = file.filename.lower()


    # --------------------------------------------------------
    # Validate file type
    # --------------------------------------------------------

    if not (
        filename.endswith(".txt")
        or
        filename.endswith(".csv")
    ):

        raise HTTPException(
            status_code=400,
            detail="Only .txt and .csv files are supported"
        )


    # --------------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------------

    content = await file.read()


    # --------------------------------------------------------
    # Decode file
    # --------------------------------------------------------

    try:

        text = content.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file must use UTF-8 text encoding"
        )


    # ========================================================
    # CSV PROCESSING
    # ========================================================

    if filename.endswith(".csv"):

        lines = []


        try:

            reader = csv.DictReader(
                text.splitlines()
            )


            # ------------------------------------------------
            # Check header
            # ------------------------------------------------

            if not reader.fieldnames:

                raise HTTPException(
                    status_code=400,
                    detail="CSV file must contain a header row"
                )


            # ------------------------------------------------
            # Check feedback column
            # ------------------------------------------------

            if "feedback" not in reader.fieldnames:

                raise HTTPException(
                    status_code=400,
                    detail="CSV must contain a 'feedback' column"
                )


            # ------------------------------------------------
            # Read feedback rows
            # ------------------------------------------------

            for row in reader:

                feedback = row.get(
                    "feedback",
                    ""
                )


                if (
                    feedback
                    and
                    feedback.strip()
                ):

                    lines.append(
                        feedback.strip()
                    )


        except HTTPException:

            raise


        except Exception:

            raise HTTPException(
                status_code=400,
                detail="Invalid CSV format"
            )


        # ----------------------------------------------------
        # Combine all feedback
        # ----------------------------------------------------

        text = " ".join(
            lines
        )


    # ========================================================
    # CHECK EMPTY FILE
    # ========================================================

    if text.strip() == "":

        raise HTTPException(
            status_code=400,
            detail="Uploaded file contains no valid text"
        )


    # ========================================================
    # PREPROCESSING
    # ========================================================

    cleaned_text = preprocess_text(
        text
    )


    # ========================================================
    # SENTIMENT
    # ========================================================

    sentiment_result = analyze_sentiment(
        cleaned_text
    )


    # ========================================================
    # BERT EMOTION
    # ========================================================

    emotion_result = analyze_emotion(
        text
    )


    # ========================================================
    # MULTI-LABEL EMOTION
    # ========================================================

    multilabel_emotion_result = (
        analyze_multilabel_emotion(
            text
        )
    )


    # ========================================================
    # EMOTIONAL STATE
    # ========================================================

    emotional_state_result = (
        analyze_emotional_state(
            multilabel_emotion_result[
                "emotion_scores"
            ]
        )
    )


    # ========================================================
    # WELLNESS
    # ========================================================

    wellness_result = generate_wellness_insight(
        sentiment_result,
        emotion_result
    )


    # ========================================================
    # RETURN COMPLETE RESULT
    # ========================================================

    return {

        "status":
            "success",

        "filename":
            file.filename,

        "original_text":
            text,

        "preprocessed_text":
            cleaned_text,

        "sentiment":
            sentiment_result,

        "emotion":
            emotion_result,

        "multilabel_emotion":
            multilabel_emotion_result,

        "emotional_state":
            emotional_state_result,

        "wellness":
            wellness_result
    }