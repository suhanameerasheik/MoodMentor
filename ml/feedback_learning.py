import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


# ============================================================
# DATABASE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "moodmentor_history.db"
)


# ============================================================
# INITIALIZE FEEDBACK TABLE
# ============================================================

def initialize_feedback_database():

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS recommendation_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            recommendation_id TEXT NOT NULL,
            feedback TEXT NOT NULL,
            dominant_emotion TEXT,
            intensity REAL,
            polarity TEXT
        )
        """
    )

    connection.commit()
    connection.close()


# ============================================================
# SAVE FEEDBACK
# ============================================================

def save_recommendation_feedback(
    recommendation_id: str,
    feedback: str,
    emotional_state: Dict[str, Any]
) -> int:

    initialize_feedback_database()

    feedback = str(
        feedback
    ).lower().strip()

    if feedback not in {
        "helpful",
        "not_helpful"
    }:
        raise ValueError(
            "Feedback must be 'helpful' or 'not_helpful'"
        )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO recommendation_feedback (
            timestamp,
            recommendation_id,
            feedback,
            dominant_emotion,
            intensity,
            polarity
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(),
            recommendation_id,
            feedback,
            emotional_state.get(
                "dominant_emotion",
                "unknown"
            ),
            float(
                emotional_state.get(
                    "intensity",
                    0.0
                )
            ),
            emotional_state.get(
                "polarity",
                "neutral"
            )
        )
    )

    feedback_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return feedback_id


# ============================================================
# GET FEEDBACK STATISTICS
# ============================================================

def get_feedback_statistics() -> Dict[str, Any]:

    initialize_feedback_database()

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            recommendation_id,
            COUNT(*) AS total_feedback,
            SUM(
                CASE
                    WHEN feedback = 'helpful'
                    THEN 1
                    ELSE 0
                END
            ) AS helpful_count,
            SUM(
                CASE
                    WHEN feedback = 'not_helpful'
                    THEN 1
                    ELSE 0
                END
            ) AS not_helpful_count
        FROM recommendation_feedback
        GROUP BY recommendation_id
        """
    )

    rows = cursor.fetchall()

    connection.close()

    statistics = {}

    for row in rows:

        recommendation_id = row[0]
        total = row[1] or 0
        helpful = row[2] or 0
        not_helpful = row[3] or 0

        helpful_rate = (
            helpful / total
            if total > 0
            else 0.0
        )

        statistics[recommendation_id] = {
            "total_feedback": total,
            "helpful_count": helpful,
            "not_helpful_count": not_helpful,
            "helpful_rate": round(
                helpful_rate,
                4
            )
        }

    return statistics


# ============================================================
# FEEDBACK SCORE
# ============================================================

def get_feedback_score(
    recommendation_id: str
) -> float:

    statistics = (
        get_feedback_statistics()
    )

    recommendation_stats = (
        statistics.get(
            recommendation_id
        )
    )

    if not recommendation_stats:
        return 0.0

    helpful_rate = (
        recommendation_stats[
            "helpful_rate"
        ]
    )

    # Positive feedback increases score.
    if helpful_rate >= 0.70:
        return 0.15

    # Mostly positive feedback.
    if helpful_rate >= 0.50:
        return 0.05

    # Mostly negative feedback.
    if helpful_rate < 0.30:
        return -0.15

    return 0.0


# ============================================================
# APPLY FEEDBACK LEARNING
# ============================================================

def apply_feedback_learning(
    recommendations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    for recommendation in recommendations:

        recommendation_id = (
            recommendation["id"]
        )

        feedback_score = (
            get_feedback_score(
                recommendation_id
            )
        )

        original_score = float(
            recommendation.get(
                "score",
                0.0
            )
        )

        learned_score = max(
            0.0,
            min(
                1.0,
                original_score
                + feedback_score
            )
        )

        recommendation[
            "feedback_score"
        ] = round(
            feedback_score,
            4
        )

        recommendation[
            "learned_score"
        ] = round(
            learned_score,
            4
        )

    recommendations.sort(
        key=lambda item:
            item["learned_score"],
        reverse=True
    )

    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):

        recommendation["rank"] = index

    return recommendations


# ============================================================
# INITIALIZE
# ============================================================

initialize_feedback_database()