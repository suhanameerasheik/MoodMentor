import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from collections import Counter


# ============================================================
# DATABASE LOCATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "moodmentor_history.db"
)


DEFAULT_USER_ID = "default_user"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database() -> None:

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # Create the original table if it does not exist.
    #
    # user_id is included for new installations.
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS emotional_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_id TEXT NOT NULL DEFAULT 'default_user',
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

    # --------------------------------------------------------
    # Migration support for existing databases.
    #
    # Older versions of MoodMentor did not have user_id.
    # Add it without deleting existing records.
    # --------------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(emotional_history)"
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    if "user_id" not in columns:

        cursor.execute(
            """
            ALTER TABLE emotional_history
            ADD COLUMN user_id TEXT
            NOT NULL
            DEFAULT 'default_user'
            """
        )

    connection.commit()

    connection.close()


# ============================================================
# NORMALIZE USER ID
# ============================================================

def normalize_user_id(
    user_id: str = DEFAULT_USER_ID
) -> str:

    if not isinstance(
        user_id,
        str
    ):
        return DEFAULT_USER_ID

    user_id = user_id.strip()

    if not user_id:
        return DEFAULT_USER_ID

    return user_id


# ============================================================
# SAVE EMOTIONAL STATE
# ============================================================

def save_emotional_state(
    emotional_state: Dict[str, Any],
    sentiment: Dict[str, Any],
    wellness: Dict[str, Any],
    user_id: str = DEFAULT_USER_ID
) -> int:

    initialize_database()

    user_id = normalize_user_id(
        user_id
    )

    connection = get_connection()

    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO emotional_history (
            timestamp,
            user_id,
            dominant_emotion,
            intensity,
            polarity,
            severity,
            sentiment,
            sentiment_score,
            wellness_risk
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,

            user_id,

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
    limit: int = 20,
    user_id: str = DEFAULT_USER_ID
) -> List[Dict[str, Any]]:

    initialize_database()

    limit = max(
        1,
        min(
            int(limit),
            100
        )
    )

    user_id = normalize_user_id(
        user_id
    )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            timestamp,
            user_id,
            dominant_emotion,
            intensity,
            polarity,
            severity,
            sentiment,
            sentiment_score,
            wellness_risk
        FROM emotional_history
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            user_id,
            limit
        )
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# EMOTION FREQUENCY
# ============================================================

def calculate_emotion_frequency(
    history: List[Dict[str, Any]]
) -> Dict[str, int]:

    emotions = [
        str(
            record.get(
                "dominant_emotion",
                "unknown"
            )
        ).lower()
        for record in history
    ]

    return dict(
        Counter(emotions)
    )


# ============================================================
# POLARITY FREQUENCY
# ============================================================

def calculate_polarity_frequency(
    history: List[Dict[str, Any]]
) -> Dict[str, int]:

    polarities = [
        str(
            record.get(
                "polarity",
                "neutral"
            )
        ).lower()
        for record in history
    ]

    return dict(
        Counter(polarities)
    )


# ============================================================
# POSITIVE / NEGATIVE TREND
# ============================================================

def calculate_positive_negative_trend(
    history: List[Dict[str, Any]]
) -> Dict[str, Any]:

    if not history:

        return {
            "direction": "insufficient_data",
            "recent_negative_ratio": 0.0,
            "older_negative_ratio": 0.0,
            "negative_ratio_change": 0.0
        }

    # History is newest first.

    split_index = max(
        1,
        len(history) // 2
    )

    recent_records = history[
        :split_index
    ]

    older_records = history[
        split_index:
    ]

    def negative_ratio(records):

        if not records:
            return 0.0

        negative_count = sum(
            1
            for record in records
            if str(
                record.get(
                    "polarity",
                    "neutral"
                )
            ).lower()
            == "negative"
        )

        return (
            negative_count
            / len(records)
        )

    recent_negative_ratio = (
        negative_ratio(
            recent_records
        )
    )

    older_negative_ratio = (
        negative_ratio(
            older_records
        )
    )

    negative_ratio_change = (
        recent_negative_ratio
        - older_negative_ratio
    )

    if negative_ratio_change >= 0.20:

        direction = "more_negative"

    elif negative_ratio_change <= -0.20:

        direction = "more_positive"

    else:

        direction = "stable"

    return {
        "direction": direction,

        "recent_negative_ratio": round(
            recent_negative_ratio,
            4
        ),

        "older_negative_ratio": round(
            older_negative_ratio,
            4
        ),

        "negative_ratio_change": round(
            negative_ratio_change,
            4
        )
    }


# ============================================================
# TREND CALCULATION
# ============================================================

def calculate_emotional_trend(
    history: List[Dict[str, Any]]
) -> Dict[str, Any]:

    records_analyzed = len(
        history
    )

    # --------------------------------------------------------
    # No history
    # --------------------------------------------------------

    if records_analyzed == 0:

        return {
            "trend": "insufficient_data",

            "message":
                "No emotional history is available for this user.",

            "records_analyzed": 0,

            "average_intensity": 0.0,

            "intensity_change": 0.0,

            "intensity_over_time": [],

            "emotion_frequency": {},

            "dominant_emotion": "unknown",

            "repeated_emotions": [],

            "polarity_frequency": {},

            "positive_records": 0,

            "negative_records": 0,

            "neutral_records": 0,

            "positive_negative_trend": {
                "direction": "insufficient_data",
                "recent_negative_ratio": 0.0,
                "older_negative_ratio": 0.0,
                "negative_ratio_change": 0.0
            },

            "recent_emotions": [],

            "recent_state": {
                "emotion": "unknown",
                "intensity": 0.0,
                "polarity": "neutral",
                "severity": "low"
            }
        }

    # --------------------------------------------------------
    # Basic statistics
    # --------------------------------------------------------

    emotion_frequency = (
        calculate_emotion_frequency(
            history
        )
    )

    polarity_frequency = (
        calculate_polarity_frequency(
            history
        )
    )

    # --------------------------------------------------------
    # Dominant historical emotion
    # --------------------------------------------------------

    dominant_emotion = max(
        emotion_frequency,
        key=emotion_frequency.get
    )

    # --------------------------------------------------------
    # Repeated emotional patterns
    #
    # An emotion appearing at least twice is considered
    # a repeated historical pattern.
    # --------------------------------------------------------

    repeated_emotions = sorted(
        [
            emotion
            for emotion, count
            in emotion_frequency.items()
            if count >= 2
        ],
        key=lambda emotion:
            emotion_frequency[emotion],
        reverse=True
    )

    # --------------------------------------------------------
    # Intensity over time
    #
    # Returned oldest -> newest for easier visualization.
    # --------------------------------------------------------

    chronological_history = list(
        reversed(history)
    )

    intensity_over_time = [
        {
            "timestamp":
                record.get(
                    "timestamp",
                    ""
                ),

            "intensity": round(
                float(
                    record.get(
                        "intensity",
                        0.0
                    )
                ),
                4
            ),

            "emotion":
                record.get(
                    "dominant_emotion",
                    "unknown"
                )
        }
        for record
        in chronological_history
    ]

    # --------------------------------------------------------
    # Intensity statistics
    # --------------------------------------------------------

    intensities = [
        float(
            record.get(
                "intensity",
                0.0
            )
        )
        for record in history
    ]

    average_intensity = (
        sum(intensities)
        / len(intensities)
    )

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

    # --------------------------------------------------------
    # Determine intensity trend
    # --------------------------------------------------------

    if records_analyzed < 2:

        trend = "insufficient_data"

        message = (
            "At least two emotional records are required "
            "to determine a trend."
        )

    elif intensity_change <= -0.10:

        trend = "improving"

        message = (
            "Emotional intensity has decreased over "
            "the tracked period."
        )

    elif intensity_change >= 0.10:

        trend = "worsening"

        message = (
            "Emotional intensity has increased over "
            "the tracked period."
        )

    else:

        trend = "stable"

        message = (
            "Emotional intensity has remained relatively stable."
        )

    # --------------------------------------------------------
    # Positive / negative records
    # --------------------------------------------------------

    positive_records = polarity_frequency.get(
        "positive",
        0
    )

    negative_records = polarity_frequency.get(
        "negative",
        0
    )

    neutral_records = polarity_frequency.get(
        "neutral",
        0
    )

    # --------------------------------------------------------
    # Positive / negative trend
    # --------------------------------------------------------

    positive_negative_trend = (
        calculate_positive_negative_trend(
            history
        )
    )

    # --------------------------------------------------------
    # Recent emotions
    # --------------------------------------------------------

    recent_emotions = [
        record.get(
            "dominant_emotion",
            "unknown"
        )
        for record in history[:5]
    ]

    # --------------------------------------------------------
    # Recent emotional state
    # --------------------------------------------------------

    recent_state = {
        "emotion":
            newest.get(
                "dominant_emotion",
                "unknown"
            ),

        "intensity": round(
            newest_intensity,
            4
        ),

        "polarity":
            newest.get(
                "polarity",
                "neutral"
            ),

        "severity":
            newest.get(
                "severity",
                "low"
            )
    }

    return {
        "trend": trend,

        "message": message,

        "records_analyzed":
            records_analyzed,

        "average_intensity": round(
            average_intensity,
            4
        ),

        "intensity_change": round(
            intensity_change,
            4
        ),

        "intensity_over_time":
            intensity_over_time,

        "emotion_frequency":
            emotion_frequency,

        "dominant_emotion":
            dominant_emotion,

        "repeated_emotions":
            repeated_emotions,

        "polarity_frequency":
            polarity_frequency,

        "positive_records":
            positive_records,

        "negative_records":
            negative_records,

        "neutral_records":
            neutral_records,

        "positive_negative_trend":
            positive_negative_trend,

        "recent_emotions":
            recent_emotions,

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
            ),

        "recent_state":
            recent_state
    }


# ============================================================
# COMPLETE TREND ANALYSIS
# ============================================================

def get_emotional_trend(
    limit: int = 20,
    user_id: str = DEFAULT_USER_ID
) -> Dict[str, Any]:

    user_id = normalize_user_id(
        user_id
    )

    history = get_emotional_history(
        limit=limit,
        user_id=user_id
    )

    trend = calculate_emotional_trend(
        history
    )

    return {
        "trend_analysis": trend,
        "history": history,
        "user_id": user_id
    }


# ============================================================
# INITIALIZE DATABASE WHEN MODULE LOADS
# ============================================================

initialize_database()