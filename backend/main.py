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

from ml.recommendation import (
    generate_personalized_recommendations
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
# COMMON ANALYSIS FUNCTION
# ============================================================

def run_analysis(text):

    # --------------------------------------------------------
    # Validate text
    # --------------------------------------------------------

    if not text or not text.strip():

        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )


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
    # Step 5: Emotional state
    # --------------------------------------------------------

    emotional_state_result = (
        analyze_emotional_state(
            multilabel_emotion_result[
                "emotion_scores"
            ]
        )
    )


    # --------------------------------------------------------
    # Step 6: Wellness
    # --------------------------------------------------------

    wellness_result = generate_wellness_insight(
        sentiment_result,
        emotion_result
    )


    return {
        "original_text": text,
        "preprocessed_text": cleaned_text,
        "sentiment": sentiment_result,
        "emotion": emotion_result,
        "multilabel_emotion":
            multilabel_emotion_result,
        "emotional_state":
            emotional_state_result,
        "wellness": wellness_result
    }


# ============================================================
# ANALYZE DIRECT TEXT
# ============================================================

@app.post("/analyze")
def analyze(data: dict):

    text = data.get(
        "text",
        ""
    )

    try:

        analysis_result = run_analysis(
            text
        )

    except HTTPException:

        return {
            "status": "error",
            "message": "Text cannot be empty"
        }


    return {

        "status": "success",

        "message":
            (
                "Text successfully passed through "
                "preprocessing, sentiment analysis, "
                "emotion analysis, multi-label emotion "
                "analysis, emotional intensity analysis "
                "and wellness analysis"
            ),

        **analysis_result
    }


# ============================================================
# PERSONALIZED RECOMMENDATIONS
# ============================================================

@app.post("/recommend")
def recommend(data: dict):

    text = data.get(
        "text",
        ""
    )

    preferences = data.get(
        "preferences",
        []
    )

    recommendation_history = data.get(
        "recommendation_history",
        []
    )

    top_k = data.get(
        "top_k",
        5
    )


    # --------------------------------------------------------
    # Validate preferences
    # --------------------------------------------------------

    if not isinstance(
        preferences,
        list
    ):

        preferences = []


    # --------------------------------------------------------
    # Validate history
    # --------------------------------------------------------

    if not isinstance(
        recommendation_history,
        list
    ):

        recommendation_history = []


    # --------------------------------------------------------
    # Validate top_k
    # --------------------------------------------------------

    try:

        top_k = int(top_k)

    except (
        ValueError,
        TypeError
    ):

        top_k = 5


    top_k = max(
        1,
        min(top_k, 10)
    )


    # --------------------------------------------------------
    # Run ML analysis
    # --------------------------------------------------------

    try:

        analysis_result = run_analysis(
            text
        )

    except HTTPException as error:

        raise error


    emotional_state = (
        analysis_result[
            "emotional_state"
        ]
    )


    # --------------------------------------------------------
    # Generate personalized recommendations
    # --------------------------------------------------------

    recommendation_result = (
        generate_personalized_recommendations(
            emotional_state=emotional_state,
            preferences=preferences,
            recommendation_history=
                recommendation_history,
            top_k=top_k
        )
    )


    # --------------------------------------------------------
    # Return recommendation result
    # --------------------------------------------------------

    return {

        "status": "success",

        "message":
            "Personalized recommendations generated successfully",

        "analysis": analysis_result,

        "recommendations":
            recommendation_result
    }


# ============================================================
# ANALYZE UPLOADED TXT / CSV FILE
# ============================================================

@app.post("/analyze-file")
async def analyze_file(
    file: UploadFile = File(...)
):

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
    # RUN ANALYSIS
    # ========================================================

    analysis_result = run_analysis(
        text
    )


    # ========================================================
    # RETURN COMPLETE RESULT
    # ========================================================

    return {

        "status":
            "success",

        "filename":
            file.filename,

        **analysis_result
    }