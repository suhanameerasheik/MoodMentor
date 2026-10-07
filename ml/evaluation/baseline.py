"""
Task 9.2 - Baseline Recommendation Method

Simple keyword/rule-based recommender used only for
comparison with the advanced ML recommendation system.

This file intentionally does NOT import recommendation.py,
sentence-transformers, transformers, or torch.
"""

WELLNESS_BASELINE = {
    "breathing_01": {
        "title": "5-Minute Deep Breathing",
        "keywords": {
            "fear", "anxiety", "anxious", "scared",
            "stress", "stressed", "nervous", "calm"
        },
    },
    "mindfulness_01": {
        "title": "Mindfulness Reset",
        "keywords": {
            "sadness", "anxiety", "anxious", "stress",
            "mindfulness", "calm", "reflection"
        },
    },
    "walk_01": {
        "title": "Take a Short Walk",
        "keywords": {
            "anger", "angry", "frustrated", "stress",
            "walk", "walking", "overwhelmed"
        },
    },
    "break_01": {
        "title": "Take a Screen Break",
        "keywords": {
            "stress", "overwhelmed", "workload",
            "tired", "concentrate", "focus"
        },
    },
    "music_01": {
        "title": "Listen to Calming Music",
        "keywords": {
            "sadness", "sad", "stress", "calm",
            "relaxation", "difficult", "reflection"
        },
    },
    "journaling_01": {
        "title": "Write Down Your Thoughts",
        "keywords": {
            "sadness", "sad", "reflection", "thoughts",
            "difficult", "bothering", "journaling"
        },
    },
    "gratitude_01": {
        "title": "Gratitude Reflection",
        "keywords": {
            "happy", "joy", "positive", "gratitude",
            "good", "completed", "win"
        },
    },
    "social_01": {
        "title": "Talk to Someone You Trust",
        "keywords": {
            "fear", "scared", "isolated", "alone",
            "support", "social", "talk", "someone"
        },
    },
    "focus_01": {
        "title": "Focus Reset Exercise",
        "keywords": {
            "focus", "concentrate", "concentration",
            "workload", "overwhelmed", "productivity"
        },
    },
    "celebrate_01": {
        "title": "Celebrate a Small Win",
        "keywords": {
            "happy", "joy", "positive", "completed",
            "success", "win", "achievement"
        },
    },
    "relax_01": {
        "title": "Guided Relaxation",
        "keywords": {
            "fear", "anxiety", "anxious", "stress",
            "stressed", "angry", "sad", "calm",
            "relax", "relaxation"
        },
    },
    "planning_01": {
        "title": "Workload Planning Reset",
        "keywords": {
            "workload", "work", "tasks", "planning",
            "productivity", "organize", "organized",
            "deadline", "concentrate"
        },
    },
}


def generate_baseline_recommendations(
    text: str,
    emotion: str,
    intensity: float,
    polarity: str,
    top_k: int = 3,
):
    """
    Generate recommendations using simple keyword matching.

    This is intentionally much simpler than the advanced
    hybrid ML recommendation system.
    """

    text_lower = text.lower()

    scored = []

    for recommendation_id, item in WELLNESS_BASELINE.items():

        score = 0

        # Match dominant emotion
        if emotion.lower() in item["keywords"]:
            score += 3

        # Match words from the user's text
        for keyword in item["keywords"]:
            if keyword in text_lower:
                score += 1

        # Negative feedback gives a small preference to
        # calming/supportive recommendations.
        if polarity.lower() == "negative":
            if recommendation_id in {
                "breathing_01",
                "mindfulness_01",
                "music_01",
                "social_01",
                "relax_01",
            }:
                score += 1

        # High intensity slightly favors calming actions.
        if intensity >= 0.8:
            if recommendation_id in {
                "breathing_01",
                "relax_01",
                "mindfulness_01",
            }:
                score += 1

        scored.append(
            {
                "id": recommendation_id,
                "title": item["title"],
                "score": score,
            }
        )

    # Highest score first
    scored.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    recommendations = scored[:top_k]

    for rank, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        recommendation["rank"] = rank

    return recommendations