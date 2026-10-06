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
    get_emotional_trend,
    normalize_user_id
)
from ml.feedback_learning import (
    save_recommendation_feedback,
    get_feedback_statistics,
    apply_feedback_learning
)

from ml.interaction_history import (
    save_recommendation_interaction,
    get_previous_interactions
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


# ============================================================
# ANALYSIS
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
        "wellness":
            wellness_result
    }


# ============================================================
# SAVE ANALYSIS HISTORY
# ============================================================

def save_analysis_history(
    analysis_result,
    user_id="default_user"
):

    user_id = normalize_user_id(
        user_id
    )

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
            ],
        user_id=user_id
    )


# ============================================================
# ANALYZE TEXT
# ============================================================

@app.post("/analyze")
def analyze(data: dict):

    text = data.get(
        "text",
        ""
    )

    user_id = normalize_user_id(
        data.get(
            "user_id",
            "default_user"
        )
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
        analysis_result,
        user_id
    )

    return {
        "status": "success",
        "message":
            "Text successfully analyzed",
        "history_record_id":
            record_id,
        "user_id":
            user_id,
        **analysis_result
    }


# ============================================================
# PERSONALIZED RECOMMENDATIONS
# TASK 3 + TASK 4 + TASK 5 + TASK 6 + TASK 7
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

    # --------------------------------------------------
    # USER ID
    # --------------------------------------------------

    user_id = normalize_user_id(
        data.get(
            "user_id",
            "default_user"
        )
    )

    # --------------------------------------------------
    # Validate preferences
    # --------------------------------------------------

    if not isinstance(
        preferences,
        list
    ):
        preferences = []

    # --------------------------------------------------
    # Validate recommendation history
    # --------------------------------------------------

    if not isinstance(
        recommendation_history,
        list
    ):
        recommendation_history = []

    # --------------------------------------------------
    # Validate top_k
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Analyze current text
    # --------------------------------------------------

    analysis_result = run_analysis(
        text
    )

    emotional_state = (
        analysis_result[
            "emotional_state"
        ]
    )

    # --------------------------------------------------
    # TASK 6
    #
    # Read historical emotional state BEFORE saving
    # the current record.
    # --------------------------------------------------

    historical_emotional_context = (
        get_emotional_trend(
            limit=20,
            user_id=user_id
        )
    )

    historical_history = (
        historical_emotional_context.get(
            "history",
            []
        )
    )

    historical_trend_analysis = (
        historical_emotional_context.get(
            "trend_analysis",
            {}
        )
    )

    # --------------------------------------------------
    # Save current emotional state
    # --------------------------------------------------

    record_id = save_analysis_history(
        analysis_result,
        user_id
    )

    # --------------------------------------------------
    # Generate recommendations
    #
    # Existing hybrid + semantic +
    # collaborative recommendation logic
    # is preserved.
    #
    # Task 6 historical emotional context
    # is passed into the recommendation engine.
    # --------------------------------------------------

    recommendation_result = (
        generate_personalized_recommendations(
            emotional_state=emotional_state,
            preferences=preferences,
            recommendation_history=
                recommendation_history,
            top_k=top_k,
            text=text,
            user_id=user_id,
            historical_emotional_context=
                historical_emotional_context
        )
    )

    recommendations = (
        recommendation_result[
            "recommendations"
        ]
    )

    # --------------------------------------------------
    # TASK 6
    #
    # Apply emotional trend adjustment
    # before feedback learning.
    #
    # Original hybrid score is preserved.
    # --------------------------------------------------

    for recommendation in recommendations:

        base_hybrid_score = float(
            recommendation.get(
                "score",
                0.0
            )
        )

        trend_adjustment = float(
            recommendation.get(
                "trend_adjustment",
                0.0
            )
        )

        trend_adjusted_score = max(
            0.0,
            min(
                1.0,
                base_hybrid_score
                + trend_adjustment
            )
        )

        # Preserve original pure hybrid score.
        recommendation[
            "base_score"
        ] = round(
            base_hybrid_score,
            4
        )

        # Preserve Task 6 adjusted score.
        recommendation[
            "trend_adjusted_score"
        ] = round(
            trend_adjusted_score,
            4
        )

        # This becomes the input to
        # Task 7 feedback learning.
        recommendation[
            "score"
        ] = round(
            trend_adjusted_score,
            4
        )

    # --------------------------------------------------
    # TASK 7
    #
    # Apply user-specific feedback learning.
    #
    # Feedback from one user must not affect
    # another user's recommendations.
    # --------------------------------------------------

    recommendations = (
        apply_feedback_learning(
            recommendations,
            user_id=user_id
        )
    )

    # --------------------------------------------------
    # FINAL RANKING AFTER FEEDBACK LEARNING
    # --------------------------------------------------

    for recommendation in recommendations:

        recommendation[
            "score"
        ] = round(
            float(
                recommendation.get(
                    "learned_score",
                    recommendation.get(
                        "trend_adjusted_score",
                        recommendation.get(
                            "base_score",
                            0.0
                        )
                    )
                )
            ),
            4
        )

        # Keep explanation's final score
        # synchronized with actual score.

        if recommendation.get(
            "explanation"
        ):

            factors = recommendation[
                "explanation"
            ].get(
                "factors",
                {}
            )

            factors[
                "final_score"
            ] = round(
                recommendation[
                    "score"
                ],
                4
            )

    # --------------------------------------------------
    # Final sorting
    # --------------------------------------------------

    recommendations.sort(
        key=lambda item: (
            item.get(
                "score",
                0.0
            ),
            item.get(
                "base_score",
                0.0
            ),
            item.get(
                "semantic_score",
                0.0
            ),
            item.get(
                "collaborative_score",
                0.0
            ),
            item.get(
                "emotion_similarity_score",
                0.0
            )
        ),
        reverse=True
    )

    # --------------------------------------------------
    # Reassign ranks
    # --------------------------------------------------

    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):

        recommendation[
            "rank"
        ] = index

    # --------------------------------------------------
    # Update recommendation result
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Components
    # --------------------------------------------------

    if "components" not in recommendation_result:

        recommendation_result[
            "components"
        ] = []

    if (
        "feedback_learning"
        not in recommendation_result[
            "components"
        ]
    ):

        recommendation_result[
            "components"
        ].append(
            "feedback_learning"
        )

    # --------------------------------------------------
    # TASK 6
    #
    # Return historical trend summary.
    # --------------------------------------------------

    recommendation_result[
        "historical_emotional_trend"
    ] = historical_trend_analysis

    recommendation_result[
        "trend_influence"
    ] = {

        "enabled":
            len(
                historical_history
            ) >= 2,

        "records_analyzed":
            len(
                historical_history
            ),

        "trend":
            historical_trend_analysis.get(
                "trend",
                "insufficient_data"
            ),

        "dominant_emotion":
            historical_trend_analysis.get(
                "dominant_emotion",
                "unknown"
            ),

        "repeated_emotions":
            historical_trend_analysis.get(
                "repeated_emotions",
                []
            ),

        "latest_emotion":
            historical_trend_analysis.get(
                "latest_emotion",
                "unknown"
            ),

        "latest_polarity":
            historical_trend_analysis.get(
                "latest_polarity",
                "unknown"
            )
    }

    # --------------------------------------------------
    # Save recommendation interaction history
    # --------------------------------------------------

    save_recommendation_interaction(
        text=text,
        preferences=preferences,
        emotional_state=emotional_state,
        recommendations=recommendations,
        top_recommendation=
            recommendation_result[
                "top_recommendation"
            ]
    )

    return {
        "status": "success",
        "message":
            "Personalized recommendations generated successfully",
        "history_record_id":
            record_id,
        "user_id":
            user_id,
        "analysis":
            analysis_result,
        "recommendations":
            recommendation_result
    }


# ============================================================
# PREVIOUS RECOMMENDATION INTERACTIONS
# ============================================================

@app.get("/previous-interactions")
def previous_interactions(
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

    interactions = (
        get_previous_interactions(
            limit
        )
    )

    return {
        "status": "success",
        "message":
            "Previous recommendation interactions retrieved successfully",
        "count":
            len(interactions),
        "interactions":
            interactions
    }


# ============================================================
# TASK 7
# RECOMMENDATION FEEDBACK
# ============================================================

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

    user_id = normalize_user_id(
        data.get(
            "user_id",
            "default_user"
        )
    )

    # --------------------------------------------------
    # Optional rating
    # --------------------------------------------------

    rating = data.get(
        "rating",
        None
    )

    # --------------------------------------------------
    # Optional interaction type
    #
    # Supported:
    # viewed
    # accepted
    # rejected
    # rating
    # preference_changed
    # --------------------------------------------------

    interaction_type = data.get(
        "interaction_type",
        None
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
                    emotional_state,
                user_id=user_id,
                rating=rating,
                interaction_type=
                    interaction_type
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
            feedback,
        "rating":
            rating,
        "interaction_type":
            interaction_type,
        "user_id":
            user_id
    }


# ============================================================
# TASK 7
# FEEDBACK STATISTICS
# ============================================================

@app.get("/recommendation-feedback")
def recommendation_feedback_stats(
    user_id: str = None
):

    if user_id:

        user_id = normalize_user_id(
            user_id
        )

    statistics = (
        get_feedback_statistics(
            user_id=user_id
        )
    )

    return {
        "status": "success",
        "message":
            "Recommendation feedback statistics retrieved successfully",
        "user_id":
            user_id,
        "statistics":
            statistics
    }


# ============================================================
# TASK 6
# EMOTIONAL TREND & USER STATE TRACKING
# ============================================================

@app.get("/emotional-trend")
def emotional_trend(
    limit: int = 20,
    user_id: str = "default_user"
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

    user_id = normalize_user_id(
        user_id
    )

    trend_result = get_emotional_trend(
        limit=limit,
        user_id=user_id
    )

    return {
        "status": "success",
        "message":
            "Emotional trend retrieved successfully",
        **trend_result
    }


# ============================================================
# FILE ANALYSIS
# ============================================================

@app.post("/analyze-file")
async def analyze_file(
    file: UploadFile = File(...),
    user_id: str = "default_user"
):

    user_id = normalize_user_id(
        user_id
    )

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

    # --------------------------------------------------
    # CSV
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Validate uploaded text
    # --------------------------------------------------

    if not text.strip():

        raise HTTPException(
            status_code=400,
            detail="Uploaded file contains no valid text"
        )

    # --------------------------------------------------
    # Analyze
    # --------------------------------------------------

    analysis_result = run_analysis(
        text
    )

    # --------------------------------------------------
    # Save user-specific history
    # --------------------------------------------------

    record_id = save_analysis_history(
        analysis_result,
        user_id
    )

    return {
        "status": "success",
        "filename":
            file.filename,
        "history_record_id":
            record_id,
        "user_id":
            user_id,
        **analysis_result
    }