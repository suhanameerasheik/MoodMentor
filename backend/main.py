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

from ml.trend_tracking import (
    save_emotional_state,
    get_emotional_trend
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

    if not text or not text.strip():

        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )

    cleaned_text = preprocess_text(
        text
    )

    sentiment_result = analyze_sentiment(
        cleaned_text
    )

    emotion_result = analyze_emotion(
        text
    )

    multilabel_emotion_result = (
        analyze_multilabel_emotion(
            text
        )
    )

    emotional_state_result = (
        analyze_emotional_state(
            multilabel_emotion_result[
                "emotion_scores"
            ]
        )
    )

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
# SAVE ANALYSIS HISTORY
# ============================================================

def save_analysis_history(
    analysis_result
):

    return save_emotional_state(
        emotional_state=
            analysis_result[
                "emotional_state"
            ],

        sentiment=
            analysis_result[
                "sentiment"
            ],

        wellness=
            analysis_result[
                "wellness"
            ]
    )


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

    record_id = save_analysis_history(
        analysis_result
    )

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

        "history_record_id":
            record_id,

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

    if not isinstance(
        preferences,
        list
    ):

        preferences = []

    if not isinstance(
        recommendation_history,
        list
    ):

        recommendation_history = []

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

    try:

        analysis_result = run_analysis(
            text
        )

    except HTTPException as error:

        raise error

    # --------------------------------------------------------
    # Save emotional state
    # --------------------------------------------------------

    record_id = save_analysis_history(
        analysis_result
    )

    emotional_state = (
        analysis_result[
            "emotional_state"
        ]
    )

    # --------------------------------------------------------
    # Generate recommendations
    # --------------------------------------------------------

    recommendation_result = (
        generate_personalized_recommendations(
            emotional_state=emotional_state,
            preferences=preferences,
            recommendation_history=
                recommendation_history,
            top_k=top_k,
            text=text
        )
    )

    return {

        "status": "success",

        "message":
            "Personalized recommendations generated successfully",

        "history_record_id":
            record_id,

        "analysis":
            analysis_result,

        "recommendations":
            recommendation_result
    }


# ============================================================
# EMOTIONAL TREND ENDPOINT
# ============================================================

@app.get("/emotional-trend")
def emotional_trend(
    limit: int = 20
):

    try:

        limit = int(limit)

    except (
        ValueError,
        TypeError
    ):

        limit = 20

    limit = max(
        1,
        min(limit, 100)
    )

    trend_result = get_emotional_trend(
        limit
    )

    return {

        "status": "success",

        "message":
            "Emotional trend retrieved successfully",

        **trend_result
    }


# ============================================================
# ANALYZE UPLOADED TXT / CSV FILE
# ============================================================

@app.post("/analyze-file")
async def analyze_file(
    file: UploadFile = File(...)
):

    filename = file.filename.lower()

    if not (
        filename.endswith(".txt")
        or
        filename.endswith(".csv")
    ):

        raise HTTPException(
            status_code=400,
            detail="Only .txt and .csv files are supported"
        )

    content = await file.read()

    try:

        text = content.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file must use UTF-8 text encoding"
        )

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

    if text.strip() == "":

        raise HTTPException(
            status_code=400,
            detail="Uploaded file contains no valid text"
        )

    analysis_result = run_analysis(
        text
    )

    record_id = save_analysis_history(
        analysis_result
    )

    return {

        "status":
            "success",

        "filename":
            file.filename,

        "history_record_id":
            record_id,

        **analysis_result
    }