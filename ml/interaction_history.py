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

    # --------------------------------------------------
    # Create table if it does not exist
    # --------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS recommendation_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'default_user',
            text TEXT NOT NULL,
            preferences TEXT,
            emotional_state TEXT,
            recommendations TEXT,
            top_recommendation TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    # --------------------------------------------------
    # Database migration
    #
    # Existing databases created before Task 10 may
    # not have the user_id column.
    # --------------------------------------------------

    cursor.execute(
        """
        PRAGMA table_info(
            recommendation_interactions
        )
        """
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    if "user_id" not in columns:

        cursor.execute(
            """
            ALTER TABLE recommendation_interactions
            ADD COLUMN user_id TEXT
            DEFAULT 'default_user'
            """
        )

    connection.commit()

    connection.close()


def save_recommendation_interaction(
    text,
    preferences,
    emotional_state,
    recommendations,
    top_recommendation,
    user_id="default_user"
):

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO recommendation_interactions (
            user_id,
            text,
            preferences,
            emotional_state,
            recommendations,
            top_recommendation,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
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
    limit=20,
    user_id=None
):

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    if user_id:

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                text,
                preferences,
                emotional_state,
                recommendations,
                top_recommendation,
                created_at
            FROM recommendation_interactions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                user_id,
                limit
            )
        )

    else:

        cursor.execute(
            """
            SELECT
                id,
                user_id,
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
                "user_id": (
                    row["user_id"]
                    or "default_user"
                ),
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