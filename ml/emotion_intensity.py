from typing import Dict, Any


# ============================================================
# EMOTION GROUPS
# ============================================================

NEGATIVE_EMOTIONS = {
    "sadness",
    "anger",
    "fear",
    "disgust"
}

POSITIVE_EMOTIONS = {
    "joy",
    "love"
}


# ============================================================
# CALCULATE EMOTIONAL INTENSITY
# ============================================================

def calculate_emotion_intensity(
    emotion_scores: Dict[str, float]
) -> float:

    if not emotion_scores:
        return 0.0

    highest_score = max(
        emotion_scores.values()
    )

    return round(
        float(highest_score),
        4
    )


# ============================================================
# DETERMINE EMOTIONAL POLARITY
# ============================================================

def determine_polarity(
    emotion: str
) -> str:

    emotion = emotion.lower()

    if emotion in POSITIVE_EMOTIONS:
        return "positive"

    if emotion in NEGATIVE_EMOTIONS:
        return "negative"

    return "neutral"


# ============================================================
# DETECT MIXED EMOTIONAL STATE
# ============================================================

def detect_mixed_emotion(
    emotion_scores: Dict[str, float],
    threshold: float = 0.30
) -> bool:

    significant_emotions = [

        score

        for score in emotion_scores.values()

        if score >= threshold
    ]

    return len(significant_emotions) >= 2


# ============================================================
# DETERMINE EMOTIONAL SEVERITY
# ============================================================

def determine_severity(
    intensity: float,
    polarity: str
) -> str:

    if polarity == "negative":

        if intensity >= 0.80:
            return "high"

        if intensity >= 0.50:
            return "medium"

        return "low"

    if polarity == "positive":

        if intensity >= 0.80:
            return "high_positive"

        if intensity >= 0.50:
            return "moderate_positive"

        return "low_positive"

    return "low"


# ============================================================
# COMPLETE EMOTIONAL STATE ANALYSIS
# ============================================================

def analyze_emotional_state(
    emotion_scores: Dict[str, float]
) -> Dict[str, Any]:

    if not emotion_scores:

        return {
            "dominant_emotion": "unknown",
            "intensity": 0.0,
            "polarity": "neutral",
            "mixed_emotion": False,
            "severity": "low",
            "emotion_scores": {}
        }


    # --------------------------------------------------------
    # Dominant emotion
    # --------------------------------------------------------

    dominant_emotion = max(
        emotion_scores,
        key=emotion_scores.get
    )


    # --------------------------------------------------------
    # Emotional intensity
    # --------------------------------------------------------

    intensity = calculate_emotion_intensity(
        emotion_scores
    )


    # --------------------------------------------------------
    # Positive / negative / neutral
    # --------------------------------------------------------

    polarity = determine_polarity(
        dominant_emotion
    )


    # --------------------------------------------------------
    # Mixed emotional state
    # --------------------------------------------------------

    mixed_emotion = detect_mixed_emotion(
        emotion_scores
    )


    # --------------------------------------------------------
    # Emotional severity
    # --------------------------------------------------------

    severity = determine_severity(
        intensity,
        polarity
    )


    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {

        "dominant_emotion":
            dominant_emotion,

        "intensity":
            intensity,

        "polarity":
            polarity,

        "mixed_emotion":
            mixed_emotion,

        "severity":
            severity,

        "emotion_scores": {

            emotion:
                round(
                    float(score),
                    4
                )

            for emotion, score
            in emotion_scores.items()
        }
    }