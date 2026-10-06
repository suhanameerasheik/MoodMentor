from typing import Dict, List, Any
from collections import defaultdict
import math

from sentence_transformers import (
    SentenceTransformer,
    util
)

from ml.feedback_learning import (
    get_all_user_interactions
)


# ============================================================
# SEMANTIC MODEL
# ============================================================

SEMANTIC_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Loading semantic wellness model...")

semantic_model = SentenceTransformer(
    SEMANTIC_MODEL_NAME
)

print("Semantic wellness model loaded successfully.")


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
# PRECOMPUTE WELLNESS CONTENT EMBEDDINGS
# ============================================================

WELLNESS_TEXTS = [
    (
        content["title"]
        + ". "
        + content["description"]
        + ". "
        + " ".join(content["tags"])
    )
    for content in WELLNESS_CONTENT
]

WELLNESS_EMBEDDINGS = semantic_model.encode(
    WELLNESS_TEXTS,
    convert_to_tensor=True
)


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

    times_seen = recommendation_history.count(
        content_id
    )

    if times_seen == 0:
        return 0.20

    if times_seen == 1:
        return 0.0

    return -0.15


# ============================================================
# RULE-BASED SCORE
# ============================================================

def calculate_rule_score(
    content: Dict[str, Any],
    dominant_emotion: str,
    intensity: float,
    polarity: str
) -> float:

    score = 0.0

    if dominant_emotion in content["emotions"]:
        score += 0.50

    score += (
        intensity_match(
            intensity,
            content["intensity"]
        ) * 0.30
    )

    if content["polarity"] == polarity:
        score += 0.20

    return round(
        score,
        4
    )


# ============================================================
# CONTENT-BASED EMOTION SCORE
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
# EMOTION SIMILARITY
# ============================================================

def calculate_emotion_similarity_score(
    content: Dict[str, Any],
    emotion_scores: Dict[str, float]
) -> float:

    if not emotion_scores:
        return 0.0

    content_emotions = set(
        content.get(
            "emotions",
            []
        )
    )

    if not content_emotions:
        return 0.0

    user_vector = []
    content_vector = []

    for emotion, score in emotion_scores.items():

        user_vector.append(
            float(score)
        )

        content_vector.append(
            1.0
            if emotion in content_emotions
            else 0.0
        )

    user_magnitude = math.sqrt(
        sum(
            value * value
            for value in user_vector
        )
    )

    content_magnitude = math.sqrt(
        sum(
            value * value
            for value in content_vector
        )
    )

    if (
        user_magnitude == 0.0
        or content_magnitude == 0.0
    ):
        return 0.0

    dot_product = sum(
        user_value * content_value
        for user_value, content_value
        in zip(
            user_vector,
            content_vector
        )
    )

    similarity = (
        dot_product
        /
        (
            user_magnitude
            *
            content_magnitude
        )
    )

    return round(
        max(
            0.0,
            min(
                1.0,
                similarity
            )
        ),
        4
    )


# ============================================================
# HISTORICAL USER BEHAVIOR
# ============================================================

def calculate_historical_behavior_score(
    recommendation_history: List[str],
    content_id: str
) -> float:

    history_value = history_score(
        recommendation_history,
        content_id
    )

    return round(
        max(
            0.0,
            min(
                1.0,
                0.5 + history_value
            )
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
# SEMANTIC CONTENT MATCHING
# ============================================================

def calculate_semantic_scores(
    text: str
) -> List[float]:

    if not text or not text.strip():
        return [
            0.0
            for _ in WELLNESS_CONTENT
        ]

    text_embedding = semantic_model.encode(
        text,
        convert_to_tensor=True
    )

    similarities = util.cos_sim(
        text_embedding,
        WELLNESS_EMBEDDINGS
    )[0]

    return [
        round(
            max(
                0.0,
                float(score)
            ),
            4
        )
        for score in similarities
    ]


# ============================================================
# TASK 3C — COLLABORATIVE FILTERING
# ============================================================

def _feedback_value(
    feedback: str
) -> float:

    feedback = str(
        feedback
    ).lower().strip()

    if feedback == "helpful":
        return 1.0

    if feedback == "not_helpful":
        return -1.0

    return 0.0


def _build_user_item_matrix(
    interactions: List[Dict[str, Any]]
) -> Dict[str, Dict[str, float]]:

    matrix = defaultdict(dict)

    for interaction in interactions:

        user_id = interaction.get(
            "user_id"
        )

        recommendation_id = (
            interaction.get(
                "recommendation_id"
            )
        )

        if not user_id or not recommendation_id:
            continue

        value = _feedback_value(
            interaction.get(
                "feedback",
                ""
            )
        )

        if value == 0.0:
            continue

        matrix[
            str(user_id)
        ][
            str(recommendation_id)
        ] = value

    return dict(matrix)


def _cosine_similarity(
    first_vector: Dict[str, float],
    second_vector: Dict[str, float]
) -> float:

    common_items = (
        set(first_vector.keys())
        &
        set(second_vector.keys())
    )

    if not common_items:
        return 0.0

    first_values = [
        first_vector[item]
        for item in common_items
    ]

    second_values = [
        second_vector[item]
        for item in common_items
    ]

    dot_product = sum(
        first_value * second_value
        for first_value, second_value
        in zip(
            first_values,
            second_values
        )
    )

    first_magnitude = math.sqrt(
        sum(
            value * value
            for value in first_values
        )
    )

    second_magnitude = math.sqrt(
        sum(
            value * value
            for value in second_values
        )
    )

    if (
        first_magnitude == 0.0
        or second_magnitude == 0.0
    ):
        return 0.0

    return (
        dot_product
        /
        (
            first_magnitude
            *
            second_magnitude
        )
    )


def calculate_collaborative_scores(
    user_id: str = "default_user"
) -> Dict[str, float]:

    if not user_id:
        return {}

    interactions = (
        get_all_user_interactions()
    )

    user_item_matrix = (
        _build_user_item_matrix(
            interactions
        )
    )

    target_user = str(
        user_id
    )

    target_vector = (
        user_item_matrix.get(
            target_user,
            {}
        )
    )

    if not target_vector:
        return {}

    collaborative_totals = defaultdict(float)
    similarity_totals = defaultdict(float)

    for other_user, other_vector in (
        user_item_matrix.items()
    ):

        if other_user == target_user:
            continue

        similarity = _cosine_similarity(
            target_vector,
            other_vector
        )

        if similarity <= 0.0:
            continue

        for recommendation_id, feedback_value in (
            other_vector.items()
        ):

            if recommendation_id in target_vector:
                continue

            collaborative_totals[
                recommendation_id
            ] += (
                similarity
                *
                feedback_value
            )

            similarity_totals[
                recommendation_id
            ] += similarity

    collaborative_scores = {}

    for recommendation_id, total in (
        collaborative_totals.items()
    ):

        similarity_total = (
            similarity_totals[
                recommendation_id
            ]
        )

        if similarity_total <= 0.0:
            continue

        raw_score = (
            total
            /
            similarity_total
        )

        normalized_score = (
            raw_score + 1.0
        ) / 2.0

        collaborative_scores[
            recommendation_id
        ] = round(
            max(
                0.0,
                min(
                    1.0,
                    normalized_score
                )
            ),
            4
        )

    return collaborative_scores


def calculate_collaborative_score(
    content_id: str,
    user_id: str = "default_user"
) -> float:

    scores = (
        calculate_collaborative_scores(
            user_id
        )
    )

    return round(
        float(
            scores.get(
                content_id,
                0.0
            )
        ),
        4
    )


# ============================================================
# TASK 6 — HISTORICAL EMOTIONAL PATTERN SCORE
# ============================================================

def calculate_historical_emotion_score(
    content: Dict[str, Any],
    historical_history: List[Dict[str, Any]]
) -> float:

    """
    Calculates how strongly the recommendation matches
    the user's previous emotional patterns.

    Recent emotional records receive higher weight than
    older records.

    Returns a value between 0.0 and 1.0.

    0.5 represents neutral/no strong historical influence.
    """

    if not historical_history:
        return 0.5

    content_emotions = set(
        content.get(
            "emotions",
            []
        )
    )

    if not content_emotions:
        return 0.5

    weighted_match = 0.0
    total_weight = 0.0

    for index, record in enumerate(
        historical_history
    ):

        dominant_emotion = str(
            record.get(
                "dominant_emotion",
                "unknown"
            )
        ).lower().strip()

        try:
            intensity = float(
                record.get(
                    "intensity",
                    0.0
                )
            )
        except (
            TypeError,
            ValueError
        ):
            intensity = 0.0

        intensity = max(
            0.0,
            min(
                1.0,
                intensity
            )
        )

        # More recent records receive more influence.
        recency_weight = (
            0.85 ** index
        )

        # Stronger emotional records receive slightly
        # more influence than weak emotional records.
        intensity_factor = (
            0.5
            +
            (0.5 * intensity)
        )

        emotion_match_value = (
            1.0
            if dominant_emotion in content_emotions
            else 0.0
        )

        weighted_match += (
            recency_weight
            *
            emotion_match_value
            *
            intensity_factor
        )

        total_weight += recency_weight

    if total_weight == 0.0:
        return 0.5

    score = (
        weighted_match
        /
        total_weight
    )

    return round(
        max(
            0.0,
            min(
                1.0,
                score
            )
        ),
        4
    )


# ============================================================
# TASK 6 — HISTORICAL TREND SCORE
# ============================================================

def calculate_historical_trend_score(
    content: Dict[str, Any],
    historical_emotional_context: Dict[str, Any]
) -> float:

    """
    Combines historical emotional patterns and trend
    information into one Task 6 score.

    The existing hybrid score is NOT changed.

    Returns a value between 0.0 and 1.0.
    """

    if not historical_emotional_context:
        return 0.5

    history = (
        historical_emotional_context.get(
            "history",
            []
        )
    )

    # A single record is not enough to establish
    # an emotional pattern.
    if len(history) < 2:
        return 0.5

    trend_analysis = (
        historical_emotional_context.get(
            "trend_analysis",
            {}
        )
    )

    historical_emotion_score = (
        calculate_historical_emotion_score(
            content,
            history
        )
    )

    trend = str(
        trend_analysis.get(
            "trend",
            "insufficient_data"
        )
    ).lower()

    latest_polarity = str(
        trend_analysis.get(
            "latest_polarity",
            "neutral"
        )
    ).lower()

    content_polarity = str(
        content.get(
            "polarity",
            "neutral"
        )
    ).lower()

    # Historical emotional pattern has the strongest
    # influence.
    pattern_component = (
        historical_emotion_score * 0.60
    )

    # Trend alignment provides an additional signal.
    #
    # For improving/worsening/stable trends, the current
    # emotional pattern remains the main signal. Therefore
    # the trend component is intentionally small.
    if trend == "worsening":
        trend_component = 0.65

    elif trend == "improving":
        trend_component = 0.45

    elif trend == "stable":
        trend_component = 0.50

    else:
        trend_component = 0.50

    trend_component *= 0.25

    # Latest polarity alignment.
    if (
        latest_polarity != "neutral"
        and latest_polarity == content_polarity
    ):
        polarity_component = 1.0

    elif latest_polarity == "neutral":
        polarity_component = 0.5

    else:
        polarity_component = 0.0

    polarity_component *= 0.15

    score = (
        pattern_component
        +
        trend_component
        +
        polarity_component
    )

    return round(
        max(
            0.0,
            min(
                1.0,
                score
            )
        ),
        4
    )


# ============================================================
# TASK 6 — TREND ADJUSTMENT
# ============================================================

def calculate_trend_adjustment(
    historical_trend_score: float
) -> float:

    """
    Converts the Task 6 trend score into a small
    recommendation adjustment.

    Maximum influence = +/- 0.05.

    This intentionally keeps Task 6 from overpowering
    the existing recommendation engine.
    """

    try:
        historical_trend_score = float(
            historical_trend_score
        )
    except (
        TypeError,
        ValueError
    ):
        historical_trend_score = 0.5

    historical_trend_score = max(
        0.0,
        min(
            1.0,
            historical_trend_score
        )
    )

    adjustment = (
        historical_trend_score - 0.5
    ) * 0.10

    return round(
        max(
            -0.05,
            min(
                0.05,
                adjustment
            )
        ),
        4
    )


# ============================================================
# TASK 3D — HYBRID RECOMMENDATION SCORE
# ============================================================

def calculate_hybrid_score(
    content: Dict[str, Any],
    emotional_state: Dict[str, Any],
    preferences: List[str],
    recommendation_history: List[str],
    semantic_score: float = 0.0,
    collaborative_score: float = 0.0
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
    # 1. Rule-based recommendation
    # --------------------------------------------------------

    rule_score = calculate_rule_score(
        content,
        dominant_emotion,
        intensity,
        polarity
    )

    # --------------------------------------------------------
    # 2. Content-based filtering
    # --------------------------------------------------------

    content_score = calculate_content_score(
        content,
        emotion_scores
    )

    # --------------------------------------------------------
    # 3. User preference matching
    # --------------------------------------------------------

    preference_score = preference_match(
        preferences,
        content["tags"]
    )

    # --------------------------------------------------------
    # 4. Historical user behavior
    # --------------------------------------------------------

    historical_behavior_score = (
        calculate_historical_behavior_score(
            recommendation_history,
            content["id"]
        )
    )

    # --------------------------------------------------------
    # 5. Emotion similarity
    # --------------------------------------------------------

    emotion_similarity_score = (
        calculate_emotion_similarity_score(
            content,
            emotion_scores
        )
    )

    # --------------------------------------------------------
    # 6. Existing personalization score
    #
    # Kept for backward compatibility and explainability.
    # It is NOT added separately to the final score because
    # preference + history are already individual components.
    # --------------------------------------------------------

    personalization_score = (
        calculate_personalization_score(
            content,
            preferences,
            recommendation_history
        )
    )

    # --------------------------------------------------------
    # 7. Collaborative filtering
    # --------------------------------------------------------

    collaborative_score = max(
        0.0,
        min(
            1.0,
            float(
                collaborative_score
            )
        )
    )

    # No collaborative information means neutral influence.
    # This prevents new users from being unfairly penalized.
    collaborative_component = (
        collaborative_score
        if collaborative_score > 0.0
        else 0.5
    )

    # --------------------------------------------------------
    # FINAL HYBRID WEIGHTS
    #
    # Rule-based             = 20%
    # Content-based          = 15%
    # Preferences            = 15%
    # Collaborative         = 15%
    # Emotion similarity     = 10%
    # Historical behavior   = 10%
    # Semantic similarity    = 15%
    #
    # Total                  = 100%
    #
    # IMPORTANT:
    # Task 6 does NOT modify these weights.
    # --------------------------------------------------------

    hybrid_score = (
        (rule_score * 0.20)
        +
        (content_score * 0.15)
        +
        (preference_score * 0.15)
        +
        (collaborative_component * 0.15)
        +
        (emotion_similarity_score * 0.10)
        +
        (historical_behavior_score * 0.10)
        +
        (semantic_score * 0.15)
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

        "preference_score": round(
            preference_score,
            4
        ),

        "collaborative_score": round(
            collaborative_component,
            4
        ),

        "emotion_similarity_score": round(
            emotion_similarity_score,
            4
        ),

        "historical_behavior_score": round(
            historical_behavior_score,
            4
        ),

        "personalization_score": round(
            personalization_score,
            4
        ),

        "semantic_score": round(
            semantic_score,
            4
        ),

        "hybrid_score": round(
            hybrid_score,
            4
        )
    }


# ============================================================
# RANKING REASON
# ============================================================

def generate_ranking_reason(
    recommendation: Dict[str, Any]
) -> List[str]:

    reasons = []

    if recommendation["rule_score"] >= 0.70:
        reasons.append(
            "strong emotional and intensity match"
        )

    elif recommendation["rule_score"] >= 0.50:
        reasons.append(
            "good emotional and intensity match"
        )

    if recommendation["content_score"] >= 0.50:
        reasons.append(
            "strong emotion-score similarity"
        )

    elif recommendation["content_score"] >= 0.20:
        reasons.append(
            "moderate emotion-score similarity"
        )

    if recommendation.get(
        "preference_score",
        0.0
    ) >= 0.50:

        reasons.append(
            "matches user preferences"
        )

    if recommendation.get(
        "collaborative_score",
        0.0
    ) >= 0.70:

        reasons.append(
            "supported by similar-user feedback"
        )

    if recommendation.get(
        "emotion_similarity_score",
        0.0
    ) >= 0.50:

        reasons.append(
            "strong emotion-vector similarity"
        )

    if recommendation.get(
        "historical_behavior_score",
        0.0
    ) >= 0.70:

        reasons.append(
            "fits the user's historical recommendation behavior"
        )

    if recommendation.get(
        "historical_emotion_score",
        0.0
    ) >= 0.60:

        reasons.append(
            "matches repeated emotional patterns from the user's history"
        )

    if recommendation.get(
        "historical_trend_score",
        0.0
    ) >= 0.60:

        reasons.append(
            "aligned with the user's recent emotional trend"
        )

    if recommendation["semantic_score"] >= 0.60:
        reasons.append(
            "strong semantic similarity"
        )

    elif recommendation["semantic_score"] >= 0.40:
        reasons.append(
            "moderate semantic similarity"
        )

    if recommendation["personalization_score"] >= 0.70:
        reasons.append(
            "strong personalization match"
        )

    elif recommendation["personalization_score"] >= 0.50:
        reasons.append(
            "good personalization match"
        )

    if not reasons:
        reasons.append(
            "general wellness relevance"
        )

    return reasons


# ============================================================
# M3-T8 RECOMMENDATION EXPLAINABILITY
# ============================================================

def generate_explanation(
    recommendation: Dict[str, Any],
    emotional_state: Dict[str, Any],
    preferences: List[str]
) -> Dict[str, Any]:

    reasons = []

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

    if recommendation["rule_score"] >= 0.70:
        reasons.append(
            f"Strong match for your current {dominant_emotion} emotional state"
        )

    elif recommendation["rule_score"] >= 0.50:
        reasons.append(
            f"Good match for your current {dominant_emotion} emotional state"
        )

    if recommendation["rule_score"] >= 0.50:

        if intensity >= 0.80:
            reasons.append(
                "Suitable for your high emotional intensity"
            )

        elif intensity >= 0.50:
            reasons.append(
                "Suitable for your moderate emotional intensity"
            )

        else:
            reasons.append(
                "Suitable for your current low emotional intensity"
            )

    if recommendation["content_score"] >= 0.50:
        reasons.append(
            "Strong similarity with your detected emotions"
        )

    elif recommendation["content_score"] >= 0.20:
        reasons.append(
            "Moderate similarity with your detected emotions"
        )

    if recommendation.get(
        "emotion_similarity_score",
        0.0
    ) >= 0.50:

        reasons.append(
            "Strong similarity between your emotion profile and this wellness activity"
        )

    if recommendation.get(
        "collaborative_score",
        0.0
    ) >= 0.70:

        reasons.append(
            "Similar users gave positive feedback for this recommendation"
        )

    if recommendation.get(
        "historical_behavior_score",
        0.0
    ) >= 0.70:

        reasons.append(
            "Fits your previous recommendation interaction pattern"
        )

    if recommendation.get(
        "historical_emotion_score",
        0.0
    ) >= 0.60:

        reasons.append(
            "Matches emotional patterns repeatedly observed in your history"
        )

    if recommendation.get(
        "historical_trend_score",
        0.0
    ) >= 0.60:

        reasons.append(
            "Takes your recent emotional trend into account"
        )

    if recommendation["semantic_score"] >= 0.60:
        reasons.append(
            "Strong semantic match with your current concern"
        )

    elif recommendation["semantic_score"] >= 0.40:
        reasons.append(
            "Moderate semantic match with your current concern"
        )

    if preferences and recommendation.get(
        "preference_score",
        0.0
    ) >= 0.50:

        reasons.append(
            "Matches your preferred wellness activities"
        )

    elif preferences and recommendation["personalization_score"] >= 0.50:

        reasons.append(
            "Matches some of your preferred wellness activities"
        )

    if polarity != "neutral":
        reasons.append(
            f"Aligned with your current {polarity} emotional state"
        )

    if not reasons:
        reasons.append(
            "Selected because it provides general wellness relevance"
        )

    unique_reasons = list(
        dict.fromkeys(reasons)
    )

    if len(unique_reasons) >= 2:
        summary = (
            "Recommended using multiple signals from your "
            "emotional state, preferences, behavior, and wellness content."
        )

    else:
        summary = (
            "Recommended because it provides relevant "
            "wellness support."
        )

    factors = {
        "emotional_match": round(
            recommendation["rule_score"],
            4
        ),

        "content_based": round(
            recommendation["content_score"],
            4
        ),

        "preference_matching": round(
            recommendation.get(
                "preference_score",
                0.0
            ),
            4
        ),

        "collaborative_filtering": round(
            recommendation.get(
                "collaborative_score",
                0.0
            ),
            4
        ),

        "emotion_similarity": round(
            recommendation.get(
                "emotion_similarity_score",
                0.0
            ),
            4
        ),

        "historical_behavior": round(
            recommendation.get(
                "historical_behavior_score",
                0.0
            ),
            4
        ),

        "historical_emotion_pattern": round(
            recommendation.get(
                "historical_emotion_score",
                0.5
            ),
            4
        ),

        "historical_trend": round(
            recommendation.get(
                "historical_trend_score",
                0.5
            ),
            4
        ),

        "trend_adjustment": round(
            recommendation.get(
                "trend_adjustment",
                0.0
            ),
            4
        ),

        "personalization": round(
            recommendation["personalization_score"],
            4
        ),

        "semantic_similarity": round(
            recommendation["semantic_score"],
            4
        ),

        "final_score": round(
            recommendation["score"],
            4
        )
    }

    return {
        "summary": summary,
        "reasons": unique_reasons,
        "factors": factors
    }


# ============================================================
# DUPLICATE FILTER
# ============================================================

def remove_duplicate_recommendations(
    recommendations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    unique_recommendations = []
    seen_ids = set()

    for recommendation in recommendations:

        recommendation_id = recommendation["id"]

        if recommendation_id in seen_ids:
            continue

        seen_ids.add(
            recommendation_id
        )

        unique_recommendations.append(
            recommendation
        )

    return unique_recommendations


# ============================================================
# LOW-RELEVANCE FILTER
# ============================================================

def filter_low_relevance(
    recommendations: List[Dict[str, Any]],
    minimum_score: float = 0.15
) -> List[Dict[str, Any]]:

    return [
        recommendation
        for recommendation in recommendations
        if recommendation["score"] >= minimum_score
    ]


# ============================================================
# RECOMMENDATION RANKING MODEL
# ============================================================

def rank_recommendations(
    recommendations: List[Dict[str, Any]],
    top_k: int = 5,
    emotional_state: Dict[str, Any] = None,
    preferences: List[str] = None
) -> Dict[str, Any]:

    top_k = max(
        1,
        min(
            int(top_k),
            10
        )
    )

    emotional_state = emotional_state or {}
    preferences = preferences or []

    unique_recommendations = (
        remove_duplicate_recommendations(
            recommendations
        )
    )

    duplicate_filtered = (
        len(recommendations)
        - len(unique_recommendations)
    )

    relevant_recommendations = (
        filter_low_relevance(
            unique_recommendations
        )
    )

    low_relevance_filtered = (
        len(unique_recommendations)
        - len(relevant_recommendations)
    )

    relevant_recommendations.sort(
        key=lambda item: (
            item["score"],
            item["semantic_score"],
            item.get(
                "collaborative_score",
                0.0
            ),
            item.get(
                "emotion_similarity_score",
                0.0
            ),
            item["content_score"],
            item["personalization_score"]
        ),
        reverse=True
    )

    selected = relevant_recommendations[
        :top_k
    ]

    for index, recommendation in enumerate(
        selected,
        start=1
    ):

        recommendation["rank"] = index

        recommendation["ranking_reason"] = (
            generate_ranking_reason(
                recommendation
            )
        )

        recommendation["explanation"] = (
            generate_explanation(
                recommendation=recommendation,
                emotional_state=emotional_state,
                preferences=preferences
            )
        )

    ranking_order = [
        recommendation["id"]
        for recommendation in selected
    ]

    top_recommendation = (
        selected[0]
        if selected
        else None
    )

    return {
        "recommendations":
            selected,

        "count":
            len(selected),

        "top_recommendation":
            top_recommendation,

        "ranking_order":
            ranking_order,

        "duplicate_filtered":
            duplicate_filtered,

        "low_relevance_filtered":
            low_relevance_filtered
    }


# ============================================================
# GENERATE HYBRID RECOMMENDATIONS
# ============================================================

def generate_hybrid_recommendations(
    emotional_state: Dict[str, Any],
    preferences: List[str] = None,
    recommendation_history: List[str] = None,
    top_k: int = 5,
    text: str = "",
    user_id: str = "default_user",
    historical_emotional_context: Dict[str, Any] = None
) -> Dict[str, Any]:

    preferences = preferences or []

    recommendation_history = (
        recommendation_history or []
    )

    user_id = (
        str(user_id).strip()
        if user_id
        else "default_user"
    )

    top_k = max(
        1,
        min(
            int(top_k),
            10
        )
    )

    historical_emotional_context = (
        historical_emotional_context or {}
    )

    historical_history = (
        historical_emotional_context.get(
            "history",
            []
        )
    )

    semantic_scores = calculate_semantic_scores(
        text
    )

    collaborative_scores = (
        calculate_collaborative_scores(
            user_id
        )
    )

    scored_recommendations = []

    for index, content in enumerate(
        WELLNESS_CONTENT
    ):

        score_details = (
            calculate_hybrid_score(
                content=content,
                emotional_state=emotional_state,
                preferences=preferences,
                recommendation_history=
                    recommendation_history,
                semantic_score=
                    semantic_scores[index],
                collaborative_score=
                    collaborative_scores.get(
                        content["id"],
                        0.0
                    )
            )
        )

        # ----------------------------------------------------
        # TASK 6
        # Historical emotional pattern influence.
        #
        # This does NOT modify the existing hybrid score.
        # ----------------------------------------------------

        historical_emotion_score = (
            calculate_historical_emotion_score(
                content=content,
                historical_history=historical_history
            )
        )

        historical_trend_score = (
            calculate_historical_trend_score(
                content=content,
                historical_emotional_context=
                    historical_emotional_context
            )
        )

        trend_adjustment = (
            calculate_trend_adjustment(
                historical_trend_score
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

                "preference_score":
                    score_details["preference_score"],

                "collaborative_score":
                    score_details["collaborative_score"],

                "emotion_similarity_score":
                    score_details[
                        "emotion_similarity_score"
                    ],

                "historical_behavior_score":
                    score_details[
                        "historical_behavior_score"
                    ],

                "personalization_score":
                    score_details[
                        "personalization_score"
                    ],

                "semantic_score":
                    score_details[
                        "semantic_score"
                    ],

                # Existing hybrid score is preserved.
                "score":
                    score_details["hybrid_score"],

                # Task 6 additions.
                "base_score":
                    score_details["hybrid_score"],

                "historical_emotion_score":
                    historical_emotion_score,

                "historical_trend_score":
                    historical_trend_score,

                "trend_adjustment":
                    trend_adjustment,

                "trend_adjusted_score":
                    round(
                        max(
                            0.0,
                            min(
                                1.0,
                                score_details["hybrid_score"]
                                +
                                trend_adjustment
                            )
                        ),
                        4
                    )
            }
        )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Ranking inside this module continues to use the existing
    # hybrid score. main.py will apply the Task 6 adjustment
    # before feedback learning and final ranking.
    #
    # This preserves all previous ranking behavior.
    # --------------------------------------------------------

    ranking_result = rank_recommendations(
        recommendations=scored_recommendations,
        top_k=top_k,
        emotional_state=emotional_state,
        preferences=preferences
    )

    trend_analysis = (
        historical_emotional_context.get(
            "trend_analysis",
            {}
        )
    )

    ranking_result.update(
        {
            # Kept compatible with the existing API.
            "method": "hybrid_semantic_feedback",

            "components": [
                "rule_based",
                "content_based",
                "preference_matching",
                "collaborative_filtering",
                "emotion_similarity",
                "historical_behavior",
                "semantic_similarity",
                "emotional_trend_tracking",
                "historical_emotion_patterns",
                "dynamic_ranking",
                "duplicate_filtering",
                "low_relevance_filtering",
                "recommendation_explainability"
            ],

            "hybrid_weights": {
                "rule_based": 0.20,
                "content_based": 0.15,
                "preference_matching": 0.15,
                "collaborative_filtering": 0.15,
                "emotion_similarity": 0.10,
                "historical_behavior": 0.10,
                "semantic_similarity": 0.15
            },

            "user_id":
                user_id,

            "collaborative_users_available":
                len(
                    set(
                        interaction.get(
                            "user_id"
                        )
                        for interaction
                        in get_all_user_interactions()
                        if interaction.get(
                            "user_id"
                        )
                    )
                ),

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
                    len(recommendation_history),

                "collaborative_history_used":
                    bool(
                        collaborative_scores
                    ),

                # Task 6 information.
                "emotional_history_records":
                    len(historical_history),

                "historical_emotion_tracking":
                    len(historical_history) >= 2,

                "historical_dominant_emotion":
                    trend_analysis.get(
                        "dominant_emotion",
                        "unknown"
                    ),

                "historical_repeated_emotions":
                    trend_analysis.get(
                        "repeated_emotions",
                        []
                    ),

                "historical_trend":
                    trend_analysis.get(
                        "trend",
                        "insufficient_data"
                    )
            }
        }
    )

    return ranking_result


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def generate_personalized_recommendations(
    emotional_state: Dict[str, Any],
    preferences: List[str] = None,
    recommendation_history: List[str] = None,
    top_k: int = 5,
    text: str = "",
    user_id: str = "default_user",
    historical_emotional_context: Dict[str, Any] = None
) -> Dict[str, Any]:

    return generate_hybrid_recommendations(
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