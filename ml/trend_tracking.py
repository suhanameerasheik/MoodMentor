import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


# ============================================================
# DATABASE LOCATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "moodmentor_history.db"
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database() -> None:

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
        CREATE TABLE IF NOT EXISTS emotional_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            dominant_emotion TEXT NOT NULL,
            intensity REAL NOT NULL,
            polarity TEXT NOT NULL,
            severity TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            wellness_risk TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


# ============================================================
# SAVE EMOTIONAL STATE
# ============================================================

def save_emotional_state(
    emotional_state: Dict[str, Any],
    sentiment: Dict[str, Any],
    wellness: Dict[str, Any]
) -> int:

    initialize_database()

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO emotional_history (
            timestamp,
            dominant_emotion,
            intensity,
            polarity,
            severity,
            sentiment,
            sentiment_score,
            wellness_risk
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
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
            ),
            emotional_state.get(
                "severity",
                "low"
            ),
            sentiment.get(
                "sentiment",
                "neutral"
            ),
            float(
                sentiment.get(
                    "compound",
                    0.0
                )
            ),
            wellness.get(
                "risk_level",
                "unknown"
            )
        )
    )

    record_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return record_id


# ============================================================
# GET EMOTIONAL HISTORY
# ============================================================

def get_emotional_history(
    limit: int = 20
) -> List[Dict[str, Any]]:

    initialize_database()

    limit = max(
        1,
        min(
            int(limit),
            100
        )
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            timestamp,
            dominant_emotion,
            intensity,
            polarity,
            severity,
            sentiment,
            sentiment_score,
            wellness_risk
        FROM emotional_history
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# TREND CALCULATION
# ============================================================

def calculate_emotional_trend(
    history: List[Dict[str, Any]]
) -> Dict[str, Any]:

    if len(history) < 2:

        return {
            "trend": "insufficient_data",
            "message":
                "At least two emotional records are required to determine a trend.",
            "records_analyzed": len(history),
            "average_intensity": 0.0,
            "intensity_change": 0.0
        }

    # History is newest first.
    newest = history[0]
    oldest = history[-1]

    newest_intensity = float(
        newest.get(
            "intensity",
            0.0
        )
    )

    oldest_intensity = float(
        oldest.get(
            "intensity",
            0.0
        )
    )

    intensity_change = (
        newest_intensity
        - oldest_intensity
    )

    average_intensity = sum(
        float(
            record.get(
                "intensity",
                0.0
            )
        )
        for record in history
    ) / len(history)

    # --------------------------------------------------------
    # Determine emotional trend
    # --------------------------------------------------------

    if intensity_change <= -0.10:

        trend = "improving"

        message = (
            "Emotional intensity has decreased over the tracked period."
        )

    elif intensity_change >= 0.10:

        trend = "worsening"

        message = (
            "Emotional intensity has increased over the tracked period."
        )

    else:

        trend = "stable"

        message = (
            "Emotional intensity has remained relatively stable."
        )

    return {
        "trend": trend,

        "message": message,

        "records_analyzed": len(history),

        "average_intensity": round(
            average_intensity,
            4
        ),

        "intensity_change": round(
            intensity_change,
            4
        ),

        "latest_emotion":
            newest.get(
                "dominant_emotion",
                "unknown"
            ),

        "latest_polarity":
            newest.get(
                "polarity",
                "neutral"
            ),

        "latest_severity":
            newest.get(
                "severity",
                "low"
            )
    }


# ============================================================
# COMPLETE TREND ANALYSIS
# ============================================================

def get_emotional_trend(
    limit: int = 20
) -> Dict[str, Any]:

    history = get_emotional_history(
        limit
    )

    trend = calculate_emotional_trend(
        history
    )

    return {
        "trend_analysis": trend,
        "history": history
    }


# ============================================================
# INITIALIZE DATABASE WHEN MODULE LOADS
# ============================================================

initialize_database()