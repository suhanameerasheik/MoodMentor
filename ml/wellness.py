def generate_wellness_insight(
    sentiment_result,
    emotion_result
):

    sentiment = sentiment_result[
        "sentiment"
    ]

    emotion = emotion_result[
        "emotion"
    ]


    # ========================================================
    # HIGH-RISK EMOTIONS
    # ========================================================

    high_risk_emotions = [

        "sadness",

        "fear"
    ]


    # ========================================================
    # MEDIUM-RISK EMOTIONS
    # ========================================================

    medium_risk_emotions = [

        "anger"
    ]


    # ========================================================
    # DETERMINE WELLNESS RISK
    # ========================================================

    if (
        sentiment == "negative"
        and
        emotion in high_risk_emotions
    ):

        risk_level = "high"

        insight = (
            "Employee feedback indicates a possible "
            "emotional wellness concern."
        )


    elif (
        sentiment == "negative"
        and
        emotion in medium_risk_emotions
    ):

        risk_level = "medium"

        insight = (
            "Employee feedback indicates possible "
            "workplace dissatisfaction or frustration."
        )


    elif sentiment == "negative":

        risk_level = "medium"

        insight = (
            "Negative workplace sentiment detected. "
            "Further attention may be useful."
        )


    elif sentiment == "positive":

        risk_level = "low"

        insight = (
            "Employee feedback indicates a generally "
            "positive workplace experience."
        )


    else:

        risk_level = "low"

        insight = (
            "Employee feedback appears relatively neutral."
        )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "risk_level":
            risk_level,

        "insight":
            insight
    }