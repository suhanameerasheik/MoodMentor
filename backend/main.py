import sys
from pathlib import Path
import csv

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)

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
from ml.feedback_learning import (
    save_recommendation_feedback,
    get_feedback_statistics,
    apply_feedback_learning
)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():

    return {
        "message":
            "Employee Wellness Backend is running"
    }


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
        "wellness":
            wellness_result
    }


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
            "Text successfully analyzed",
        "history_record_id":
            record_id,
        **analysis_result
    }


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

    analysis_result = run_analysis(
        text
    )

    record_id = save_analysis_history(
        analysis_result
    )

    emotional_state = (
        analysis_result[
            "emotional_state"
        ]
    )

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

    recommendations = (
        recommendation_result[
            "recommendations"
        ]
    )

    recommendations = (
        apply_feedback_learning(
            recommendations
        )
    )

    recommendation_result[
        "recommendations"
    ] = recommendations

    recommendation_result[
        "top_recommendation"
    ] = (
        recommendations[0]
        if recommendations
        else None
    )

    recommendation_result[
        "ranking_order"
    ] = [
        item["id"]
        for item in recommendations
    ]

    recommendation_result[
        "method"
    ] = "hybrid_semantic_feedback"

    recommendation_result[
        "components"
    ].append(
        "feedback_learning"
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


@app.post("/recommendation-feedback")
def recommendation_feedback(
    data: dict
):

    recommendation_id = data.get(
        "recommendation_id",
        ""
    )

    feedback = data.get(
        "feedback",
        ""
    )

    emotional_state = data.get(
        "emotional_state",
        {}
    )

    if not recommendation_id:

        raise HTTPException(
            status_code=400,
            detail="recommendation_id is required"
        )

    try:

        feedback_id = (
            save_recommendation_feedback(
                recommendation_id=
                    recommendation_id,
                feedback=feedback,
                emotional_state=
                    emotional_state
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    return {
        "status": "success",
        "message":
            "Recommendation feedback saved successfully",
        "feedback_id":
            feedback_id,
        "recommendation_id":
            recommendation_id,
        "feedback":
            feedback
    }


@app.get("/recommendation-feedback")
def recommendation_feedback_stats():

    statistics = (
        get_feedback_statistics()
    )

    return {
        "status": "success",
        "message":
            "Recommendation feedback statistics retrieved successfully",
        "statistics":
            statistics
    }


@app.get("/emotional-trend")
def emotional_trend(
    limit: int = 20
):

    limit = max(
        1,
        min(
            int(limit),
            100
        )
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


@app.post("/analyze-file")
async def analyze_file(
    file: UploadFile = File(...)
):

    filename = file.filename.lower()

    if not (
        filename.endswith(".txt")
        or filename.endswith(".csv")
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
                    and feedback.strip()
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

    if not text.strip():

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
        "status": "success",
        "filename":
            file.filename,
        "history_record_id":
            record_id,
        **analysis_result
    }