
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_TABLES = {
    PROJECT_ROOT / "data" / "moodmentor_history.db": [
        "emotional_history",
        "recommendation_feedback",
    ],
    PROJECT_ROOT / "recommendation_interactions.db": [
        "recommendation_interactions",
    ],
}


def delete_user_data(user_id: str) -> dict:
    """Delete one user's records from MoodMentor's data stores."""

    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("A valid user ID is required")

    user_id = user_id.strip()
    deleted_counts = {}

    for database_path, tables in DATABASE_TABLES.items():
        database_name = database_path.name

        if not database_path.exists():
            for table in tables:
                deleted_counts[table] = 0
            continue

        connection = sqlite3.connect(database_path)

        try:
            cursor = connection.cursor()

            for table in tables:
                cursor.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = ? AND name = ?",
                    ("table", table),
                )

                if cursor.fetchone() is None:
                    deleted_counts[table] = 0
                    continue

                cursor.execute(f'PRAGMA table_info("{table}")')
                columns = {
                    row[1] for row in cursor.fetchall()
                }

                if "user_id" not in columns:
                    raise RuntimeError(
                        f"Cannot safely delete user data: "
                        f"{table} has no user_id column"
                    )

                cursor.execute(
                    f'DELETE FROM "{table}" WHERE user_id = ?',
                    (user_id,),
                )

                deleted_counts[table] = cursor.rowcount

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    return {
        "user_id": user_id,
        "deleted_records": deleted_counts,
        "total_deleted": sum(deleted_counts.values()),
    }