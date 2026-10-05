import sqlite3
import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    BASE_DIR / "recommendation_interactions.db"
)


def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS recommendation_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            preferences TEXT,
            emotional_state TEXT,
            recommendations TEXT,
            top_recommendation TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()

    connection.close()


def save_recommendation_interaction(
    text,
    preferences,
    emotional_state,
    recommendations,
    top_recommendation
):

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO recommendation_interactions (
            text,
            preferences,
            emotional_state,
            recommendations,
            top_recommendation,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            text,
            json.dumps(
                preferences,
                ensure_ascii=False
            ),
            json.dumps(
                emotional_state,
                ensure_ascii=False
            ),
            json.dumps(
                recommendations,
                ensure_ascii=False
            ),
            json.dumps(
                top_recommendation,
                ensure_ascii=False
            ),
            datetime.now().isoformat()
        )
    )

    connection.commit()

    interaction_id = cursor.lastrowid

    connection.close()

    return interaction_id


def get_previous_interactions(
    limit=20
):

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            text,
            preferences,
            emotional_state,
            recommendations,
            top_recommendation,
            created_at
        FROM recommendation_interactions
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    connection.close()

    interactions = []

    for row in rows:

        interactions.append(
            {
                "id": row["id"],
                "text": row["text"],
                "preferences": json.loads(
                    row["preferences"]
                )
                if row["preferences"]
                else [],
                "emotional_state": json.loads(
                    row["emotional_state"]
                )
                if row["emotional_state"]
                else {},
                "recommendations": json.loads(
                    row["recommendations"]
                )
                if row["recommendations"]
                else [],
                "top_recommendation": json.loads(
                    row["top_recommendation"]
                )
                if row["top_recommendation"]
                else None,
                "created_at": row["created_at"]
            }
        )

    return interactions