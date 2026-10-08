import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MoodMentor Dashboard",
    page_icon="MM",
    layout="wide",
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_previous_interactions(user_id):
    try:
        response = requests.get(
            f"{BACKEND_URL}/previous-interactions",
            params={"user_id": user_id},
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            interactions = data.get("interactions", [])

            if isinstance(interactions, list):
                return interactions

        if isinstance(data, list):
            return data

        return []

    except requests.RequestException as exc:
        st.error(
            f"Unable to load interaction history: {exc}"
        )
        return None

def analyze_and_recommend(
    text,
    user_id,
    preferences,
    top_k,
):
    """Send employee text to the recommendation API."""

    payload = {
        "text": text,
        "user_id": user_id,
        "preferences": preferences,
        "recommendation_history": [],
        "top_k": top_k,
    }

    try:

        response = requests.post(
            f"{BACKEND_URL}/recommend",
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:

        st.error(
            f"Could not connect to the backend: {error}"
        )

        return None


# ============================================================
# HEADER
# ============================================================

st.title("MoodMentor")

st.subheader(
    "Employee Wellness Management Dashboard"
)

st.write(
    "Analyze emotional state and receive personalized "
    "wellness recommendations."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Dashboard Settings")

    user_id = st.text_input(
        "User ID",
        value="default_user",
    )

    top_k = st.slider(
        "Number of recommendations",
        min_value=1,
        max_value=10,
        value=5,
    )

    preferences_text = st.text_input(
        "Wellness preferences",
        placeholder="music, relaxation, exercise",
    )

    preferences = [
        item.strip()
        for item in preferences_text.split(",")
        if item.strip()
    ]


# ============================================================
# USER INPUT
# ============================================================

st.header("Emotional Check-in")

text = st.text_area(
    "How are you feeling today?",
    height=150,
    placeholder=(
        "Example: I am feeling stressed and tired "
        "because of work."
    ),
)

analyze_button = st.button(
    "Analyze & Get Recommendations",
    type="primary",
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze_button:

    if not user_id.strip():

        st.warning(
            "Please enter a User ID."
        )

    elif not text.strip():

        st.warning(
            "Please enter some text before analyzing."
        )

    else:

        selected_user_id = user_id.strip()

        with st.spinner(
            "Analyzing emotional state and generating recommendations..."
        ):

            result = analyze_and_recommend(
                text=text.strip(),
                user_id=selected_user_id,
                preferences=preferences,
                top_k=top_k,
            )

        if result:

            if result.get("status") == "success":

                # ------------------------------------------------
                # Store latest result
                # ------------------------------------------------

                st.session_state["latest_result"] = result

                st.session_state["latest_user_id"] = (
                    selected_user_id
                )

                # ------------------------------------------------
                # IMPORTANT:
                # Refresh interaction history immediately after
                # a successful recommendation.
                # ------------------------------------------------

                history = get_previous_interactions(
                    selected_user_id
                )

                if history is not None:

                    st.session_state[
                        "interaction_history"
                    ] = history

                st.success(
                    "Analysis and recommendations generated successfully."
                )

            else:

                st.error(
                    result.get(
                        "message",
                        "The backend returned an error.",
                    )
                )


# ============================================================
# DISPLAY LATEST RESULT
# ============================================================

if "latest_result" in st.session_state:

    result = st.session_state["latest_result"]

    st.divider()

    st.header("Emotional Analysis")

    # --------------------------------------------------------
    # /recommend returns analysis inside the "analysis" key.
    # --------------------------------------------------------

    analysis = result.get(
        "analysis",
        {},
    )

    emotional_state = analysis.get(
        "emotional_state",
        {},
    )

    sentiment = analysis.get(
        "sentiment",
        {},
    )

    emotion = analysis.get(
        "emotion",
        {},
    )

    wellness = analysis.get(
        "wellness",
        {},
    )


    # ========================================================
    # MAIN METRICS
    # ========================================================

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Dominant Emotion",
            emotional_state.get(
                "dominant_emotion",
                "N/A",
            ).title(),
        )

    with col2:

        st.metric(
            "Intensity",
            f"{float(emotional_state.get('intensity', 0)):.2f}",
        )

    with col3:

        st.metric(
            "Polarity",
            emotional_state.get(
                "polarity",
                "N/A",
            ).title(),
        )

    with col4:

        st.metric(
            "Severity",
            emotional_state.get(
                "severity",
                "N/A",
            ).title(),
        )

    with col5:

        st.metric(
            "Risk Level",
            wellness.get(
                "risk_level",
                "N/A",
            ).title(),
        )


    # ========================================================
    # EMOTION MODEL INFORMATION
    # ========================================================

    st.subheader("Emotion Detection")

    emotion_col1, emotion_col2 = st.columns(2)

    with emotion_col1:

        st.write(
            "**Primary model emotion:**",
            emotion.get(
                "emotion",
                "N/A",
            ).title(),
        )

        st.write(
            "**Model confidence:**",
            f"{float(emotion.get('confidence', 0)):.2%}",
        )

    with emotion_col2:

        st.write(
            "**Sentiment:**",
            sentiment.get(
                "sentiment",
                "N/A",
            ).title(),
        )

        st.write(
            "**Sentiment compound score:**",
            sentiment.get(
                "compound",
                0,
            ),
        )


    # ========================================================
    # EMOTIONAL SCORES
    # ========================================================

    st.subheader("Emotional Scores")

    emotion_scores = emotional_state.get(
        "emotion_scores",
        {},
    )

    if isinstance(
        emotion_scores,
        dict,
    ) and emotion_scores:

        chart_data = {
            "Emotion": [
                emotion_name.title()
                for emotion_name in emotion_scores.keys()
            ],
            "Score": [
                float(score)
                for score in emotion_scores.values()
            ],
        }

        st.bar_chart(
            chart_data,
            x="Emotion",
            y="Score",
        )

    else:

        st.info(
            "No emotional score data available."
        )


    # ========================================================
    # WELLNESS INSIGHT
    # ========================================================

    st.subheader("Wellness Insight")

    insight = wellness.get(
        "insight",
        "No wellness insight available.",
    )

    st.info(insight)


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.divider()

    st.header("Personalized Recommendations")

    # --------------------------------------------------------
    # /recommend returns:
    #
    # "recommendations": {
    #     "recommendations": [...]
    # }
    # --------------------------------------------------------

    recommendation_result = result.get(
        "recommendations",
        {},
    )

    if isinstance(
        recommendation_result,
        dict,
    ):

        recommendations = recommendation_result.get(
            "recommendations",
            [],
        )

    elif isinstance(
        recommendation_result,
        list,
    ):

        recommendations = recommendation_result

    else:

        recommendations = []


    if recommendations:

        for index, recommendation in enumerate(
            recommendations,
            start=1,
        ):

            # Safety check
            if not isinstance(
                recommendation,
                dict,
            ):
                continue

            title = recommendation.get(
                "title",
                f"Recommendation {index}",
            )

            recommendation_type = recommendation.get(
                "type",
                "General",
            )

            description = recommendation.get(
                "description",
                "",
            )

            score = recommendation.get(
                "score",
                0,
            )

            rank = recommendation.get(
                "rank",
                index,
            )

            explanation = recommendation.get(
                "explanation",
                {},
            )

            ranking_reason = recommendation.get(
                "ranking_reason",
                [],
            )


            with st.expander(
                f"{rank}. {title}",
                expanded=(index == 1),
            ):

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**Type:** {recommendation_type}"
                    )

                with col2:

                    st.write(
                        f"**Score:** {float(score):.3f}"
                    )


                if description:

                    st.write(description)


                # ------------------------------------------------
                # Recommendation explanation
                # ------------------------------------------------

                if isinstance(
                    explanation,
                    dict,
                ):

                    summary = explanation.get(
                        "summary",
                        "",
                    )

                    reasons = explanation.get(
                        "reasons",
                        [],
                    )

                    if summary:

                        st.write(
                            "**Why this recommendation?**"
                        )

                        st.write(summary)

                    if (
                        isinstance(reasons, list)
                        and reasons
                    ):

                        for reason in reasons:

                            st.write(
                                f"- {reason}"
                            )

                elif isinstance(
                    explanation,
                    str,
                ):

                    st.write(
                        "**Why this recommendation?**"
                    )

                    st.write(explanation)


                # ------------------------------------------------
                # Ranking reasons
                # ------------------------------------------------

                if (
                    isinstance(
                        ranking_reason,
                        list,
                    )
                    and ranking_reason
                ):

                    st.write(
                        "**Ranking factors:**"
                    )

                    for reason in ranking_reason:

                        st.write(
                            f"- {reason}"
                        )

    else:

        st.info(
            "No recommendations were returned."
        )


# ============================================================
# PREVIOUS INTERACTION HISTORY
# ============================================================

st.divider()

st.header("Previous Interaction History")


# ------------------------------------------------------------
# Determine which user history should be displayed
# ------------------------------------------------------------

history_user_id = user_id.strip()


# ------------------------------------------------------------
# Detect user ID changes
# ------------------------------------------------------------
# If the user changes from default_user to another user,
# fetch that user's history instead of showing the old user's
# cached history.
# ------------------------------------------------------------

cached_history_user = st.session_state.get(
    "interaction_history_user_id"
)

current_user_id = user_id.strip()

if (
    cached_history_user is not None
    and cached_history_user != current_user_id
):

    st.session_state.pop(
        "interaction_history",
        None,
    )

    st.session_state[
        "interaction_history_user_id"
    ] = current_user_id

    history_user_id = current_user_id


# ------------------------------------------------------------
# REFRESH HISTORY BUTTON
# ------------------------------------------------------------

if st.button(
    "Refresh History"
):

    history = get_previous_interactions(
        history_user_id
    )

    if history is not None:

        st.session_state[
            "interaction_history"
        ] = history

        st.session_state[
            "interaction_history_user_id"
        ] = history_user_id

        st.success(
            "Interaction history refreshed."
        )


# ------------------------------------------------------------
# LOAD HISTORY IF NOT ALREADY LOADED
# ------------------------------------------------------------

if (
    "interaction_history" not in st.session_state
    or st.session_state.get(
        "interaction_history_user_id"
    ) != history_user_id
):

    history = get_previous_interactions(
        history_user_id
    )

    if history is not None:

        st.session_state[
            "interaction_history"
        ] = history

        st.session_state[
            "interaction_history_user_id"
        ] = history_user_id


# ------------------------------------------------------------
# GET CACHED HISTORY
# ------------------------------------------------------------

history = st.session_state.get(
    "interaction_history",
    [],
)


# ------------------------------------------------------------
# DISPLAY HISTORY
# ------------------------------------------------------------

if (
    isinstance(history, list)
    and history
):

    st.write(
        f"Showing {len(history)} previous interaction(s)."
    )

    for record in history[:20]:

        if not isinstance(
            record,
            dict,
        ):
            continue

        created_at = record.get(
            "created_at",
            "Unknown time",
        )

        record_text = record.get(
            "text",
            "",
        )

        emotional_state = record.get(
            "emotional_state",
            {},
        )

        if not isinstance(
            emotional_state,
            dict,
        ):

            emotional_state = {}

        dominant_emotion = emotional_state.get(
            "dominant_emotion",
            "N/A",
        )

        intensity = emotional_state.get(
            "intensity",
            0,
        )

        with st.expander(
            f"{created_at} — "
            f"{str(dominant_emotion).title()} "
            f"(Intensity: {float(intensity):.2f})"
        ):

            st.write(
                f"**Original text:** {record_text}"
            )

            st.write(
                f"**Dominant emotion:** "
                f"{str(dominant_emotion).title()}"
            )

            st.write(
                f"**Intensity:** "
                f"{float(intensity):.2f}"
            )

            st.write(
                f"**Polarity:** "
                f"{str(emotional_state.get('polarity', 'N/A')).title()}"
            )

            st.write(
                f"**Severity:** "
                f"{str(emotional_state.get('severity', 'N/A')).title()}"
            )


            # ------------------------------------------------
            # Previous recommendations
            # ------------------------------------------------

            previous_recommendations = record.get(
                "recommendations",
                [],
            )

            if isinstance(
                previous_recommendations,
                dict,
            ):

                previous_recommendations = (
                    previous_recommendations.get(
                        "recommendations",
                        [],
                    )
                )


            if (
                isinstance(
                    previous_recommendations,
                    list,
                )
                and previous_recommendations
            ):

                st.write(
                    "**Recommendations from this interaction:**"
                )

                for recommendation in previous_recommendations[:5]:

                    if isinstance(
                        recommendation,
                        dict,
                    ):

                        st.write(
                            f"- {recommendation.get('title', 'Unknown')}"
                        )

else:

    st.info(
        "No previous interaction history found "
        f"for user `{history_user_id}`."
    )