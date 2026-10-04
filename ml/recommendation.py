from typing import Dict, List, Any


# ============================================================
# WELLNESS CONTENT CATALOG
# ============================================================

WELLNESS_CONTENT = [
    {
        "id": "breathing_01",
        "title": "5-Minute Deep Breathing",
        "type": "breathing",
        "emotions": ["fear", "anger", "sadness"],
        "polarity": "negative",
        "intensity": "high",
        "tags": ["breathing", "stress", "calm"],
        "description": "A short breathing exercise to reduce immediate stress and tension."
    },
    {
        "id": "mindfulness_01",
        "title": "Mindfulness Reset",
        "type": "mindfulness",
        "emotions": ["fear", "sadness", "anger"],
        "polarity": "negative",
        "intensity": "medium",
        "tags": ["mindfulness", "relaxation", "focus"],
        "description": "A simple mindfulness activity to help regain emotional balance."
    },
    {
        "id": "walk_01",
        "title": "Take a Short Walk",
        "type": "physical_activity",
        "emotions": ["anger", "sadness", "fear"],
        "polarity": "negative",
        "intensity": "medium",
        "tags": ["walking", "exercise", "stress"],
        "description": "Take a short walk away from your workspace to refresh your mind."
    },
    {
        "id": "break_01",
        "title": "Take a Screen Break",
        "type": "break",
        "emotions": ["sadness", "fear", "anger"],
        "polarity": "negative",
        "intensity": "low",
        "tags": ["break", "rest", "relaxation"],
        "description": "Step away from the screen for a few minutes and reset."
    },
    {
        "id": "music_01",
        "title": "Listen to Calming Music",
        "type": "music",
        "emotions": ["sadness", "fear", "anger"],
        "polarity": "negative",
        "intensity": "medium",
        "tags": ["music", "relaxation", "calm"],
        "description": "Listen to calming music to create a more relaxed environment."
    },
    {
        "id": "journaling_01",
        "title": "Write Down Your Thoughts",
        "type": "journaling",
        "emotions": ["sadness", "fear", "anger"],
        "polarity": "negative",
        "intensity": "medium",
        "tags": ["journaling", "reflection", "mental-health"],
        "description": "Write down what is bothering you and identify the main source of stress."
    },
    {
        "id": "gratitude_01",
        "title": "Gratitude Reflection",
        "type": "reflection",
        "emotions": ["joy", "sadness"],
        "polarity": "positive",
        "intensity": "low",
        "tags": ["gratitude", "positive", "reflection"],
        "description": "Spend a few minutes identifying things that went well today."
    },
    {
        "id": "social_01",
        "title": "Talk to Someone You Trust",
        "type": "social_support",
        "emotions": ["sadness", "fear", "anger"],
        "polarity": "negative",
        "intensity": "high",
        "tags": ["social-support", "communication", "support"],
        "description": "Connect with a trusted colleague, friend, or support person."
    },
    {
        "id": "focus_01",
        "title": "Focus Reset Exercise",
        "type": "productivity",
        "emotions": ["fear", "anger"],
        "polarity": "negative",
        "intensity": "medium",
        "tags": ["focus", "productivity", "work"],
        "description": "Break your workload into one small achievable task at a time."
    },
    {
        "id": "celebrate_01",
        "title": "Celebrate a Small Win",
        "type": "positive_activity",
        "emotions": ["joy"],
        "polarity": "positive",
        "intensity": "high",
        "tags": ["joy", "motivation", "positive"],
        "description": "Recognize one achievement from your day and build on that positive feeling."
    },
    {
        "id": "relax_01",
        "title": "Guided Relaxation",
        "type": "relaxation",
        "emotions": ["fear", "sadness", "anger"],
        "polarity": "negative",
        "intensity": "high",
        "tags": ["relaxation", "stress", "calm"],
        "description": "Follow a short guided relaxation exercise to release tension."
    },
    {
        "id": "planning_01",
        "title": "Workload Planning Reset",
        "type": "productivity",
        "emotions": ["fear", "anger", "sadness"],
        "polarity": "negative",
        "intensity": "high",
        "tags": ["planning", "workload", "productivity"],
        "description": "List your tasks and prioritize the most important items first."
    }
]


# ============================================================
# INTENSITY MATCHING
# ============================================================

def intensity_match(
    user_intensity: float,
    content_intensity: str
) -> float:

    if user_intensity >= 0.80:
        expected = "high"

    elif user_intensity >= 0.50:
        expected = "medium"

    else:
        expected = "low"

    if expected == content_intensity:
        return 1.0

    if {
        expected,
        content_intensity
    } <= {"high", "medium"}:
        return 0.6

    if {
        expected,
        content_intensity
    } <= {"medium", "low"}:
        return 0.5

    return 0.2


# ============================================================
# EMOTION MATCHING
# ============================================================

def emotion_match(
    emotion_scores: Dict[str, float],
    content_emotions: List[str]
) -> float:

    if not emotion_scores:
        return 0.0

    score = 0.0

    for emotion in content_emotions:

        score = max(
            score,
            float(
                emotion_scores.get(
                    emotion,
                    0.0
                )
            )
        )

    return score


# ============================================================
# PREFERENCE MATCHING
# ============================================================

def preference_match(
    preferences: List[str],
    content_tags: List[str]
) -> float:

    if not preferences:
        return 0.0

    user_preferences = {
        str(preference).lower()
        for preference in preferences
    }

    matching_tags = [
        tag
        for tag in content_tags
        if tag.lower() in user_preferences
    ]

    if not matching_tags:
        return 0.0

    return min(
        len(matching_tags)
        / len(user_preferences),
        1.0
    )


# ============================================================
# HISTORY SCORE
# ============================================================

def history_score(
    recommendation_history: List[str],
    content_id: str
) -> float:

    if not recommendation_history:
        return 0.0

    times_seen = (
        recommendation_history.count(
            content_id
        )
    )

    # Never recommended before
    if times_seen == 0:
        return 0.20

    # Seen once - small neutral effect
    if times_seen == 1:
        return 0.0

    # Repeatedly shown - reduce score
    return -0.15


# ============================================================
# RULE-BASED RECOMMENDATION SCORE
# ============================================================

def calculate_rule_score(
    content: Dict[str, Any],
    dominant_emotion: str,
    intensity: float,
    polarity: str
) -> float:

    score = 0.0

    # Emotion rule
    if dominant_emotion in content["emotions"]:
        score += 0.50

    # Intensity rule
    score += (
        intensity_match(
            intensity,
            content["intensity"]
        ) * 0.30
    )

    # Polarity rule
    if content["polarity"] == polarity:
        score += 0.20

    return round(
        score,
        4
    )


# ============================================================
# CONTENT-BASED SCORE
# ============================================================

def calculate_content_score(
    content: Dict[str, Any],
    emotion_scores: Dict[str, float]
) -> float:

    return round(
        emotion_match(
            emotion_scores,
            content["emotions"]
        ),
        4
    )


# ============================================================
# PERSONALIZATION SCORE
# ============================================================

def calculate_personalization_score(
    content: Dict[str, Any],
    preferences: List[str],
    recommendation_history: List[str]
) -> float:

    preference_score = preference_match(
        preferences,
        content["tags"]
    )

    history_value = history_score(
        recommendation_history,
        content["id"]
    )

    # Keep history adjustment inside 0-1 range
    history_adjustment = max(
        0.0,
        min(
            1.0,
            0.5 + history_value
        )
    )

    return round(
        (
            (preference_score * 0.70)
            +
            (history_adjustment * 0.30)
        ),
        4
    )


# ============================================================
# HYBRID RECOMMENDATION SCORE
# ============================================================

def calculate_hybrid_score(
    content: Dict[str, Any],
    emotional_state: Dict[str, Any],
    preferences: List[str],
    recommendation_history: List[str]
) -> Dict[str, float]:

    emotion_scores = emotional_state.get(
        "emotion_scores",
        {}
    )

    dominant_emotion = emotional_state.get(
        "dominant_emotion",
        "unknown"
    )

    intensity = float(
        emotional_state.get(
            "intensity",
            0.0
        )
    )

    polarity = emotional_state.get(
        "polarity",
        "neutral"
    )

    # --------------------------------------------------------
    # Rule-based component
    # --------------------------------------------------------

    rule_score = calculate_rule_score(
        content,
        dominant_emotion,
        intensity,
        polarity
    )

    # --------------------------------------------------------
    # Content-based component
    # --------------------------------------------------------

    content_score = calculate_content_score(
        content,
        emotion_scores
    )

    # --------------------------------------------------------
    # Personalization component
    # --------------------------------------------------------

    personalization_score = (
        calculate_personalization_score(
            content,
            preferences,
            recommendation_history
        )
    )

    # --------------------------------------------------------
    # Hybrid weighted score
    # --------------------------------------------------------

    hybrid_score = (
        (rule_score * 0.35)
        +
        (content_score * 0.35)
        +
        (personalization_score * 0.30)
    )

    return {
        "rule_score": round(
            rule_score,
            4
        ),
        "content_score": round(
            content_score,
            4
        ),
        "personalization_score": round(
            personalization_score,
            4
        ),
        "hybrid_score": round(
            hybrid_score,
            4
        )
    }


# ============================================================
# GENERATE HYBRID RECOMMENDATIONS
# ============================================================

def generate_hybrid_recommendations(
    emotional_state: Dict[str, Any],
    preferences: List[str] = None,
    recommendation_history: List[str] = None,
    top_k: int = 5
) -> Dict[str, Any]:

    preferences = preferences or []

    recommendation_history = (
        recommendation_history or []
    )

    top_k = max(
        1,
        min(
            int(top_k),
            10
        )
    )

    scored_recommendations = []

    # --------------------------------------------------------
    # Score every wellness item
    # --------------------------------------------------------

    for content in WELLNESS_CONTENT:

        score_details = (
            calculate_hybrid_score(
                content=content,
                emotional_state=emotional_state,
                preferences=preferences,
                recommendation_history=
                    recommendation_history
            )
        )

        scored_recommendations.append(
            {
                "id": content["id"],
                "title": content["title"],
                "type": content["type"],
                "description": content["description"],
                "tags": content["tags"],
                "rule_score":
                    score_details["rule_score"],
                "content_score":
                    score_details["content_score"],
                "personalization_score":
                    score_details[
                        "personalization_score"
                    ],
                "score":
                    score_details["hybrid_score"]
            }
        )

    # --------------------------------------------------------
    # Dynamic ranking
    # --------------------------------------------------------

    scored_recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    selected = scored_recommendations[
        :top_k
    ]

    # --------------------------------------------------------
    # Assign ranking
    # --------------------------------------------------------

    for index, recommendation in enumerate(
        selected,
        start=1
    ):

        recommendation["rank"] = index

    # --------------------------------------------------------
    # Return hybrid result
    # --------------------------------------------------------

    return {
        "recommendations":
            selected,

        "count":
            len(selected),

        "method":
            "hybrid",

        "components": [
            "rule_based",
            "content_based",
            "preference_matching",
            "history_based"
        ],

        "personalization": {
            "dominant_emotion":
                emotional_state.get(
                    "dominant_emotion",
                    "unknown"
                ),
            "intensity":
                emotional_state.get(
                    "intensity",
                    0.0
                ),
            "polarity":
                emotional_state.get(
                    "polarity",
                    "neutral"
                ),
            "preferences":
                preferences,
            "history_used":
                len(recommendation_history)
        }
    }


# ============================================================
# M3-T2 COMPATIBILITY FUNCTION
# ============================================================

def generate_personalized_recommendations(
    emotional_state: Dict[str, Any],
    preferences: List[str] = None,
    recommendation_history: List[str] = None,
    top_k: int = 5
) -> Dict[str, Any]:

    return generate_hybrid_recommendations(
        emotional_state=emotional_state,
        preferences=preferences,
        recommendation_history=
            recommendation_history,
        top_k=top_k
    )