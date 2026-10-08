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


def get_emotional_trend(user_id):
    try:
        response = requests.get(
            f"{BACKEND_URL}/emotional-trend",
            params={"user_id": user_id},
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            return data

        return None

    except requests.RequestException as exc:
        st.error(
            f"Unable to load emotional trend: {exc}"
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


def save_recommendation_feedback(
    recommendation_id,
    feedback,
    emotional_state,
    user_id,
    rating=None,
    interaction_type=None,
):
    """Save recommendation feedback through the backend API."""

    payload = {
        "recommendation_id": recommendation_id,
        "feedback": feedback,
        "emotional_state": emotional_state,
        "user_id": user_id,
    }

    if rating is not None:
        payload["rating"] = rating

    if interaction_type is not None:
        payload["interaction_type"] = interaction_type

    try:
        response = requests.post(
            f"{BACKEND_URL}/recommendation-feedback",
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        st.error(
            f"Unable to save feedback: {exc}"
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
                # Refresh interaction history immediately
                # ------------------------------------------------

                history = get_previous_interactions(
                    selected_user_id
                )

                if history is not None:

                    st.session_state[
                        "interaction_history"
                    ] = history

                    st.session_state[
                        "interaction_history_user_id"
                    ] = selected_user_id

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
            str(
                emotional_state.get(
                    "dominant_emotion",
                    "N/A",
                )
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
            str(
                emotional_state.get(
                    "polarity",
                    "N/A",
                )
            ).title(),
        )

    with col4:

        st.metric(
            "Severity",
            str(
                emotional_state.get(
                    "severity",
                    "N/A",
                )
            ).title(),
        )

    with col5:

        st.metric(
            "Risk Level",
            str(
                wellness.get(
                    "risk_level",
                    "N/A",
                )
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
            str(
                emotion.get(
                    "emotion",
                    "N/A",
                )
            ).title(),
        )

        st.write(
            "**Model confidence:**",
            f"{float(emotion.get('confidence', 0)):.2%}",
        )

    with emotion_col2:

        st.write(
            "**Sentiment:**",
            str(
                sentiment.get(
                    "sentiment",
                    "N/A",
                )
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

    if (
        isinstance(
            emotion_scores,
            dict,
        )
        and emotion_scores
    ):

        chart_data = {
            "Emotion": [
                str(
                    emotion_name
                ).title()
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
    # EMOTIONAL TREND
    # ========================================================

    st.divider()

    st.header("Emotional Trend")

    trend_user_id = st.session_state.get(
        "latest_user_id",
        user_id.strip(),
    )

    with st.spinner(
        "Loading emotional trend..."
    ):

        trend_result = get_emotional_trend(
            trend_user_id
        )

    if trend_result:

        trend_analysis = trend_result.get(
            "trend_analysis",
            {},
        )

        if not isinstance(
            trend_analysis,
            dict,
        ):
            trend_analysis = {}


        # ----------------------------------------------------
        # TREND SUMMARY
        # ----------------------------------------------------

        trend_col1, trend_col2, trend_col3, trend_col4 = st.columns(4)

        with trend_col1:

            st.metric(
                "Overall Trend",
                str(
                    trend_analysis.get(
                        "trend",
                        "N/A",
                    )
                ).title(),
            )

        with trend_col2:

            st.metric(
                "Records Analyzed",
                trend_analysis.get(
                    "records_analyzed",
                    0,
                ),
            )

        with trend_col3:

            st.metric(
                "Average Intensity",
                f"{float(trend_analysis.get('average_intensity', 0)):.2f}",
            )

        with trend_col4:

            st.metric(
                "Intensity Change",
                f"{float(trend_analysis.get('intensity_change', 0)):+.3f}",
            )


        trend_message = trend_analysis.get(
            "message",
            "",
        )

        if trend_message:

            st.info(
                trend_message
            )


        # ----------------------------------------------------
        # EMOTIONAL INTENSITY OVER TIME
        # ----------------------------------------------------

        st.subheader(
            "Emotional Intensity Over Time"
        )

        intensity_history = trend_analysis.get(
            "intensity_over_time",
            [],
        )

        if (
            isinstance(
                intensity_history,
                list,
            )
            and intensity_history
        ):

            trend_chart_data = []

            for item in intensity_history:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                timestamp = item.get(
                    "timestamp",
                )

                intensity = item.get(
                    "intensity",
                )

                if (
                    timestamp is not None
                    and intensity is not None
                ):

                    try:

                        trend_chart_data.append(
                            {
                                "Time": timestamp,
                                "Intensity": float(
                                    intensity
                                ),
                            }
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        continue

            if trend_chart_data:

                st.line_chart(
                    trend_chart_data,
                    x="Time",
                    y="Intensity",
                )

            else:

                st.info(
                    "No emotional intensity trend data available."
                )

        else:

            st.info(
                "No emotional intensity trend data available."
            )


        # ----------------------------------------------------
        # EMOTION AND SENTIMENT SUMMARY
        # ----------------------------------------------------

        trend_col1, trend_col2 = st.columns(2)

        with trend_col1:

            st.subheader(
                "Emotion Frequency"
            )

            emotion_frequency = trend_analysis.get(
                "emotion_frequency",
                {},
            )

            if (
                isinstance(
                    emotion_frequency,
                    dict,
                )
                and emotion_frequency
            ):

                emotion_frequency_data = {
                    "Emotion": [
                        str(
                            emotion_name
                        ).title()
                        for emotion_name
                        in emotion_frequency.keys()
                    ],
                    "Count": [
                        int(count)
                        for count
                        in emotion_frequency.values()
                    ],
                }

                st.bar_chart(
                    emotion_frequency_data,
                    x="Emotion",
                    y="Count",
                )

            else:

                st.info(
                    "No emotion frequency data available."
                )


        with trend_col2:

            st.subheader(
                "Sentiment Distribution"
            )

            polarity_frequency = trend_analysis.get(
                "polarity_frequency",
                {},
            )

            if (
                isinstance(
                    polarity_frequency,
                    dict,
                )
                and polarity_frequency
            ):

                sentiment_chart_data = {
                    "Sentiment": [
                        str(
                            name
                        ).title()
                        for name
                        in polarity_frequency.keys()
                    ],
                    "Count": [
                        int(count)
                        for count
                        in polarity_frequency.values()
                    ],
                }

                st.bar_chart(
                    sentiment_chart_data,
                    x="Sentiment",
                    y="Count",
                )

            else:

                st.info(
                    "No sentiment distribution data available."
                )


        # ----------------------------------------------------
        # RECENT EMOTIONAL STATE
        # ----------------------------------------------------

        st.subheader(
            "Recent Emotional State"
        )

        recent_state = trend_analysis.get(
            "recent_state",
            {},
        )

        if isinstance(
            recent_state,
            dict,
        ):

            state_col1, state_col2, state_col3, state_col4 = st.columns(4)

            with state_col1:

                st.metric(
                    "Latest Emotion",
                    str(
                        recent_state.get(
                            "emotion",
                            "N/A",
                        )
                    ).title(),
                )

            with state_col2:

                st.metric(
                    "Latest Intensity",
                    f"{float(recent_state.get('intensity', 0)):.2f}",
                )

            with state_col3:

                st.metric(
                    "Latest Polarity",
                    str(
                        recent_state.get(
                            "polarity",
                            "N/A",
                        )
                    ).title(),
                )

            with state_col4:

                st.metric(
                    "Latest Severity",
                    str(
                        recent_state.get(
                            "severity",
                            "N/A",
                        )
                    ).title(),
                )

        else:

            st.info(
                "Recent emotional state is not available."
            )

    else:

        st.info(
            "Emotional trend data is not available."
        )


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.divider()

    st.header("Personalized Recommendations")

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

            recommendation_id = recommendation.get(
                "id",
                "",
            )

            try:
                score_value = float(score)
            except (
                TypeError,
                ValueError,
            ):
                score_value = 0.0

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
                        f"**Score:** {score_value:.3f}"
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

                    st.write(
                        explanation
                    )


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


                # ------------------------------------------------
                # RECOMMENDATION FEEDBACK
                # ------------------------------------------------

                st.divider()

                st.write(
                    "**Was this recommendation helpful?**"
                )

                feedback_col1, feedback_col2 = st.columns(2)

                with feedback_col1:

                    if st.button(
                        "👍 Helpful",
                        key=(
                            f"helpful_"
                            f"{recommendation_id}_"
                            f"{index}"
                        ),
                    ):

                        if not recommendation_id:

                            st.error(
                                "Recommendation ID is missing."
                            )

                        else:

                            feedback_response = (
                                save_recommendation_feedback(
                                    recommendation_id=(
                                        recommendation_id
                                    ),
                                    feedback="helpful",
                                    emotional_state=(
                                        result.get(
                                            "analysis",
                                            {},
                                        ).get(
                                            "emotional_state",
                                            {},
                                        )
                                    ),
                                    user_id=user_id,
                                    interaction_type="accepted",
                                )
                            )

                            if feedback_response:

                                st.success(
                                    "Thank you! Your feedback was saved."
                                )


                with feedback_col2:

                    if st.button(
                        "👎 Not Helpful",
                        key=(
                            f"not_helpful_"
                            f"{recommendation_id}_"
                            f"{index}"
                        ),
                    ):

                        if not recommendation_id:

                            st.error(
                                "Recommendation ID is missing."
                            )

                        else:

                            feedback_response = (
                                save_recommendation_feedback(
                                    recommendation_id=(
                                        recommendation_id
                                    ),
                                    feedback="not_helpful",
                                    emotional_state=(
                                        result.get(
                                            "analysis",
                                            {},
                                        ).get(
                                            "emotional_state",
                                            {},
                                        )
                                    ),
                                    user_id=user_id,
                                    interaction_type="rejected",
                                )
                            )

                            if feedback_response:

                                st.success(
                                    "Thank you! Your feedback was saved."
                                )


                rating = st.select_slider(
                    "Rate this recommendation",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    key=(
                        f"rating_"
                        f"{recommendation_id}_"
                        f"{index}"
                    ),
                )

                if st.button(
                    "Submit Rating",
                    key=(
                        f"submit_rating_"
                        f"{recommendation_id}_"
                        f"{index}"
                    ),
                ):

                    if not recommendation_id:

                        st.error(
                            "Recommendation ID is missing."
                        )

                    else:

                        rating_response = (
                            save_recommendation_feedback(
                                recommendation_id=(
                                    recommendation_id
                                ),
                                feedback="helpful",
                                emotional_state=(
                                    result.get(
                                        "analysis",
                                        {},
                                    ).get(
                                        "emotional_state",
                                        {},
                                    )
                                ),
                                user_id=user_id,
                                rating=rating,
                                interaction_type="rating",
                            )
                        )

                        if rating_response:

                            st.success(
                                "Your rating was saved."
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


# ============================================================
# DETERMINE HISTORY USER
# ============================================================

history_user_id = user_id.strip()

cached_history_user = st.session_state.get(
    "interaction_history_user_id"
)

current_user_id = user_id.strip()


# ============================================================
# DETECT USER ID CHANGES
# ============================================================

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


# ============================================================
# REFRESH HISTORY BUTTON
# ============================================================

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


# ============================================================
# LOAD HISTORY IF NOT ALREADY LOADED
# ============================================================

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


# ============================================================
# GET CACHED HISTORY
# ============================================================

history = st.session_state.get(
    "interaction_history",
    [],
)


# ============================================================
# DISPLAY HISTORY
# ============================================================

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

        try:
            intensity_value = float(intensity)
        except (
            TypeError,
            ValueError,
        ):
            intensity_value = 0.0

        with st.expander(
            f"{created_at} — "
            f"{str(dominant_emotion).title()} "
            f"(Intensity: {intensity_value:.2f})"
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
                f"{intensity_value:.2f}"
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