import html
import io

import requests
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


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
            interactions = data.get(
                "interactions",
                [],
            )

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
# PDF HELPER FUNCTIONS
# ============================================================

def pdf_paragraph(
    value,
    style,
):
    """
    Convert a value into a ReportLab Paragraph.

    Paragraph is used instead of a plain string so that
    long text wraps correctly inside PDF table cells.
    """

    if value is None:
        value = ""

    safe_value = html.escape(
        str(value)
    )

    return Paragraph(
        safe_value,
        style,
    )


def format_pdf_date(timestamp):
    """
    Format an ISO timestamp so it does not collide with
    neighboring PDF table columns.

    Example:
    2026-10-08T23:59:13.687325

    becomes:

    2026-10-08
    23:59:13
    """

    if timestamp is None:
        return "Unknown"

    value = str(timestamp).strip()

    if "T" in value:
        date_part, time_part = value.split(
            "T",
            1,
        )

        if "." in time_part:
            time_part = time_part.split(
                ".",
                1,
            )[0]

        return (
            f"{html.escape(date_part)}"
            f"<br/>"
            f"{html.escape(time_part)}"
        )

    return html.escape(value)


# ============================================================
# PDF REPORT GENERATION
# ============================================================

def create_pdf_report(
    user_id,
    result,
    trend_result,
    history,
):
    """Create a PDF wellness report from dashboard data."""

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=18,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        spaceAfter=6,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
    )

    date_cell_style = ParagraphStyle(
        "DateCell",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=9,
    )

    story = []

    # ========================================================
    # REPORT TITLE
    # ========================================================

    story.append(
        Paragraph(
            "MoodMentor Wellness Report",
            title_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>User ID:</b> "
            f"{html.escape(str(user_id))}",
            body_style,
        )
    )

    story.append(
        Spacer(
            1,
            10,
        )
    )

    # ========================================================
    # CURRENT EMOTIONAL ANALYSIS
    # ========================================================

    analysis = {}

    if isinstance(result, dict):
        analysis = result.get(
            "analysis",
            {},
        )

    if not isinstance(analysis, dict):
        analysis = {}

    emotional_state = analysis.get(
        "emotional_state",
        {},
    )

    if not isinstance(emotional_state, dict):
        emotional_state = {}

    sentiment = analysis.get(
        "sentiment",
        {},
    )

    if not isinstance(sentiment, dict):
        sentiment = {}

    emotion = analysis.get(
        "emotion",
        {},
    )

    if not isinstance(emotion, dict):
        emotion = {}

    wellness = analysis.get(
        "wellness",
        {},
    )

    if not isinstance(wellness, dict):
        wellness = {}

    story.append(
        Paragraph(
            "Emotional Analysis",
            heading_style,
        )
    )

    try:
        intensity_value = float(
            emotional_state.get(
                "intensity",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        intensity_value = 0.0

    try:
        confidence_value = float(
            emotion.get(
                "confidence",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        confidence_value = 0.0

    analysis_data = [
        [
            pdf_paragraph(
                "Metric",
                table_header_style,
            ),
            pdf_paragraph(
                "Value",
                table_header_style,
            ),
        ],
        [
            pdf_paragraph(
                "Dominant Emotion",
                table_cell_style,
            ),
            pdf_paragraph(
                str(
                    emotional_state.get(
                        "dominant_emotion",
                        "N/A",
                    )
                ).title(),
                table_cell_style,
            ),
        ],
        [
            pdf_paragraph(
                "Intensity",
                table_cell_style,
            ),
            pdf_paragraph(
                f"{intensity_value:.2f}",
                table_cell_style,
            ),
        ],
        [
            pdf_paragraph(
                "Polarity",
                table_cell_style,
            ),
            pdf_paragraph(
                str(
                    emotional_state.get(
                        "polarity",
                        "N/A",
                    )
                ).title(),
                table_cell_style,
            ),
        ],
        [
            pdf_paragraph(
                "Severity",
                table_cell_style,
            ),
            pdf_paragraph(
                str(
                    emotional_state.get(
                        "severity",
                        "N/A",
                    )
                ).title(),
                table_cell_style,
            ),
        ],
        [
            pdf_paragraph(
                "Risk Level",
                table_cell_style,
            ),
            pdf_paragraph(
                str(
                    wellness.get(
                        "risk_level",
                        "N/A",
                    )
                ).title(),
                table_cell_style,
            ),
        ],
        [
            pdf_paragraph(
                "Model Emotion",
                table_cell_style,
            ),
            pdf_paragraph(
                str(
                    emotion.get(
                        "emotion",
                        "N/A",
                    )
                ).title(),
                table_cell_style,
            ),
        ],
        [
            pdf_paragraph(
                "Model Confidence",
                table_cell_style,
            ),
            pdf_paragraph(
                f"{confidence_value:.2%}",
                table_cell_style,
            ),
        ],
        [
            pdf_paragraph(
                "Sentiment",
                table_cell_style,
            ),
            pdf_paragraph(
                str(
                    sentiment.get(
                        "sentiment",
                        "N/A",
                    )
                ).title(),
                table_cell_style,
            ),
        ],
        [
            pdf_paragraph(
                "Sentiment Compound",
                table_cell_style,
            ),
            pdf_paragraph(
                str(
                    sentiment.get(
                        "compound",
                        0,
                    )
                ),
                table_cell_style,
            ),
        ],
    ]

    analysis_table = Table(
        analysis_data,
        colWidths=[
            2.3 * inch,
            3.7 * inch,
        ],
        repeatRows=1,
    )

    analysis_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        analysis_table
    )

    # ========================================================
    # EMOTIONAL SCORES
    # ========================================================

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

        story.append(
            Paragraph(
                "Emotional Scores",
                heading_style,
            )
        )

        score_data = [
            [
                pdf_paragraph(
                    "Emotion",
                    table_header_style,
                ),
                pdf_paragraph(
                    "Score",
                    table_header_style,
                ),
            ]
        ]

        for emotion_name, score in emotion_scores.items():

            try:
                score_value = float(score)
            except (
                TypeError,
                ValueError,
            ):
                continue

            score_data.append(
                [
                    pdf_paragraph(
                        str(
                            emotion_name
                        ).title(),
                        table_cell_style,
                    ),
                    pdf_paragraph(
                        f"{score_value:.4f}",
                        table_cell_style,
                    ),
                ]
            )

        if len(score_data) > 1:

            score_table = Table(
                score_data,
                colWidths=[
                    2.3 * inch,
                    1.5 * inch,
                ],
                repeatRows=1,
            )

            score_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey,
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey,
                        ),
                        (
                            "PADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                    ]
                )
            )

            story.append(
                score_table
            )

    # ========================================================
    # WELLNESS INSIGHT
    # ========================================================

    story.append(
        Paragraph(
            "Wellness Insight",
            heading_style,
        )
    )

    insight = wellness.get(
        "insight",
        "No wellness insight available.",
    )

    story.append(
        Paragraph(
            html.escape(
                str(insight)
            ),
            body_style,
        )
    )

    # ========================================================
    # EMOTIONAL TREND
    # ========================================================

    if isinstance(
        trend_result,
        dict,
    ):

        trend_analysis = trend_result.get(
            "trend_analysis",
            {},
        )

        if not isinstance(
            trend_analysis,
            dict,
        ):
            trend_analysis = {}

        story.append(
            Paragraph(
                "Emotional Trend",
                heading_style,
            )
        )

        try:
            average_intensity = float(
                trend_analysis.get(
                    "average_intensity",
                    0,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            average_intensity = 0.0

        try:
            intensity_change = float(
                trend_analysis.get(
                    "intensity_change",
                    0,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            intensity_change = 0.0

        trend_data = [
            [
                pdf_paragraph(
                    "Metric",
                    table_header_style,
                ),
                pdf_paragraph(
                    "Value",
                    table_header_style,
                ),
            ],
            [
                pdf_paragraph(
                    "Overall Trend",
                    table_cell_style,
                ),
                pdf_paragraph(
                    str(
                        trend_analysis.get(
                            "trend",
                            "N/A",
                        )
                    ).title(),
                    table_cell_style,
                ),
            ],
            [
                pdf_paragraph(
                    "Records Analyzed",
                    table_cell_style,
                ),
                pdf_paragraph(
                    str(
                        trend_analysis.get(
                            "records_analyzed",
                            0,
                        )
                    ),
                    table_cell_style,
                ),
            ],
            [
                pdf_paragraph(
                    "Average Intensity",
                    table_cell_style,
                ),
                pdf_paragraph(
                    f"{average_intensity:.2f}",
                    table_cell_style,
                ),
            ],
            [
                pdf_paragraph(
                    "Intensity Change",
                    table_cell_style,
                ),
                pdf_paragraph(
                    f"{intensity_change:+.3f}",
                    table_cell_style,
                ),
            ],
            [
                pdf_paragraph(
                    "Latest Emotion",
                    table_cell_style,
                ),
                pdf_paragraph(
                    str(
                        trend_analysis.get(
                            "latest_emotion",
                            "N/A",
                        )
                    ).title(),
                    table_cell_style,
                ),
            ],
            [
                pdf_paragraph(
                    "Latest Polarity",
                    table_cell_style,
                ),
                pdf_paragraph(
                    str(
                        trend_analysis.get(
                            "latest_polarity",
                            "N/A",
                        )
                    ).title(),
                    table_cell_style,
                ),
            ],
            [
                pdf_paragraph(
                    "Latest Severity",
                    table_cell_style,
                ),
                pdf_paragraph(
                    str(
                        trend_analysis.get(
                            "latest_severity",
                            "N/A",
                        )
                    ).title(),
                    table_cell_style,
                ),
            ],
        ]

        trend_table = Table(
            trend_data,
            colWidths=[
                2.3 * inch,
                3.7 * inch,
            ],
            repeatRows=1,
        )

        trend_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(
            trend_table
        )

        trend_message = trend_analysis.get(
            "message",
            "",
        )

        if trend_message:

            story.append(
                Paragraph(
                    html.escape(
                        str(trend_message)
                    ),
                    body_style,
                )
            )

    # ========================================================
    # PERSONALIZED RECOMMENDATIONS
    # ========================================================

    story.append(
        Paragraph(
            "Personalized Recommendations",
            heading_style,
        )
    )

    recommendation_result = {}

    if isinstance(result, dict):

        recommendation_result = result.get(
            "recommendations",
            {},
        )

    if isinstance(
        recommendation_result,
        dict,
    ):

        recommendations = (
            recommendation_result.get(
                "recommendations",
                [],
            )
        )

    elif isinstance(
        recommendation_result,
        list,
    ):

        recommendations = recommendation_result

    else:

        recommendations = []

    if recommendations:

        recommendation_data = [
            [
                pdf_paragraph(
                    "Recommendation",
                    table_header_style,
                ),
                pdf_paragraph(
                    "Type",
                    table_header_style,
                ),
                pdf_paragraph(
                    "Score",
                    table_header_style,
                ),
            ]
        ]

        for recommendation in recommendations[:10]:

            if not isinstance(
                recommendation,
                dict,
            ):
                continue

            recommendation_data.append(
                [
                    pdf_paragraph(
                        recommendation.get(
                            "title",
                            "Unknown",
                        ),
                        table_cell_style,
                    ),
                    pdf_paragraph(
                        recommendation.get(
                            "type",
                            "General",
                        ),
                        table_cell_style,
                    ),
                    pdf_paragraph(
                        recommendation.get(
                            "score",
                            0,
                        ),
                        table_cell_style,
                    ),
                ]
            )

        if len(recommendation_data) > 1:

            recommendation_table = Table(
                recommendation_data,
                colWidths=[
                    3.2 * inch,
                    1.3 * inch,
                    0.9 * inch,
                ],
                repeatRows=1,
            )

            recommendation_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey,
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey,
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                        (
                            "PADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                    ]
                )
            )

            story.append(
                recommendation_table
            )

    else:

        story.append(
            Paragraph(
                "No recommendations were available.",
                body_style,
            )
        )

    # ========================================================
    # PREVIOUS INTERACTION HISTORY
    # ========================================================

    story.append(
        Paragraph(
            "Previous Interaction History",
            heading_style,
        )
    )

    if (
        isinstance(
            history,
            list,
        )
        and history
    ):

        history_data = [
            [
                pdf_paragraph(
                    "Date",
                    table_header_style,
                ),
                pdf_paragraph(
                    "Emotion",
                    table_header_style,
                ),
                pdf_paragraph(
                    "Intensity",
                    table_header_style,
                ),
                pdf_paragraph(
                    "Polarity",
                    table_header_style,
                ),
                pdf_paragraph(
                    "Severity",
                    table_header_style,
                ),
            ]
        ]

        for record in history[:20]:

            if not isinstance(
                record,
                dict,
            ):
                continue

            record_emotional_state = record.get(
                "emotional_state",
                {},
            )

            if not isinstance(
                record_emotional_state,
                dict,
            ):
                record_emotional_state = {}

            intensity = record_emotional_state.get(
                "intensity",
                0,
            )

            try:
                intensity_value = float(
                    intensity
                )
            except (
                TypeError,
                ValueError,
            ):
                intensity_value = 0.0

            date_value = format_pdf_date(
                record.get(
                    "created_at",
                    "Unknown",
                )
            )

            history_data.append(
                [
                    Paragraph(
                        date_value,
                        date_cell_style,
                    ),
                    pdf_paragraph(
                        str(
                            record_emotional_state.get(
                                "dominant_emotion",
                                "N/A",
                            )
                        ).title(),
                        table_cell_style,
                    ),
                    pdf_paragraph(
                        f"{intensity_value:.2f}",
                        table_cell_style,
                    ),
                    pdf_paragraph(
                        str(
                            record_emotional_state.get(
                                "polarity",
                                "N/A",
                            )
                        ).title(),
                        table_cell_style,
                    ),
                    pdf_paragraph(
                        str(
                            record_emotional_state.get(
                                "severity",
                                "N/A",
                            )
                        ).title(),
                        table_cell_style,
                    ),
                ]
            )

        if len(history_data) > 1:

            history_table = Table(
                history_data,
                colWidths=[
                    1.65 * inch,
                    1.20 * inch,
                    0.85 * inch,
                    1.00 * inch,
                    1.20 * inch,
                ],
                repeatRows=1,
            )

            history_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey,
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey,
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                        (
                            "PADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                    ]
                )
            )

            story.append(
                history_table
            )

    else:

        story.append(
            Paragraph(
                "No previous interaction history available.",
                body_style,
            )
        )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story
    )

    buffer.seek(0)

    return buffer.getvalue()


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

                st.session_state[
                    "latest_result"
                ] = result

                st.session_state[
                    "latest_user_id"
                ] = selected_user_id

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

    result = st.session_state[
        "latest_result"
    ]

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

        try:
            display_intensity = float(
                emotional_state.get(
                    "intensity",
                    0,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            display_intensity = 0.0

        st.metric(
            "Intensity",
            f"{display_intensity:.2f}",
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

        try:
            display_confidence = float(
                emotion.get(
                    "confidence",
                    0,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            display_confidence = 0.0

        st.write(
            "**Model confidence:**",
            f"{display_confidence:.2%}",
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

    st.info(
        insight
    )

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

            try:
                average_intensity = float(
                    trend_analysis.get(
                        "average_intensity",
                        0,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                average_intensity = 0.0

            st.metric(
                "Average Intensity",
                f"{average_intensity:.2f}",
            )

        with trend_col4:

            try:
                intensity_change = float(
                    trend_analysis.get(
                        "intensity_change",
                        0,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                intensity_change = 0.0

            st.metric(
                "Intensity Change",
                f"{intensity_change:+.3f}",
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

                try:
                    latest_intensity = float(
                        recent_state.get(
                            "intensity",
                            0,
                        )
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    latest_intensity = 0.0

                st.metric(
                    "Latest Intensity",
                    f"{latest_intensity:.2f}",
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
            "Emotional trend data is not available."
        )

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.divider()

    st.header(
        "Personalized Recommendations"
    )

    recommendation_result = result.get(
        "recommendations",
        {},
    )

    if isinstance(
        recommendation_result,
        dict,
    ):

        recommendations = (
            recommendation_result.get(
                "recommendations",
                [],
            )
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

                    st.write(
                        description
                    )

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

                        st.write(
                            summary
                        )

                    if (
                        isinstance(
                            reasons,
                            list,
                        )
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
                    options=[
                        1,
                        2,
                        3,
                        4,
                        5,
                    ],
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

st.header(
    "Previous Interaction History"
)


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
# DISPLAY HISTORY WITH SEARCH AND FILTERING
# ============================================================

if (
    isinstance(
        history,
        list,
    )
    and history
):

    # --------------------------------------------------------
    # PREPARE FILTER OPTIONS
    # --------------------------------------------------------

    emotions = set()
    polarities = set()
    severities = set()
    recommendation_types = set()

    for record in history:

        if not isinstance(
            record,
            dict,
        ):
            continue

        record_emotional_state = record.get(
            "emotional_state",
            {},
        )

        if not isinstance(
            record_emotional_state,
            dict,
        ):
            record_emotional_state = {}

        dominant_emotion = record_emotional_state.get(
            "dominant_emotion"
        )

        polarity = record_emotional_state.get(
            "polarity"
        )

        severity = record_emotional_state.get(
            "severity"
        )

        if dominant_emotion:

            emotions.add(
                str(
                    dominant_emotion
                ).lower()
            )

        if polarity:

            polarities.add(
                str(
                    polarity
                ).lower()
            )

        if severity:

            severities.add(
                str(
                    severity
                ).lower()
            )

        record_recommendations = record.get(
            "recommendations",
            [],
        )

        if isinstance(
            record_recommendations,
            dict,
        ):

            record_recommendations = (
                record_recommendations.get(
                    "recommendations",
                    [],
                )
            )

        if isinstance(
            record_recommendations,
            list,
        ):

            for recommendation in record_recommendations:

                if not isinstance(
                    recommendation,
                    dict,
                ):
                    continue

                recommendation_type = recommendation.get(
                    "type"
                )

                if recommendation_type:

                    recommendation_types.add(
                        str(
                            recommendation_type
                        ).lower()
                    )

    # --------------------------------------------------------
    # SEARCH AND FILTER CONTROLS
    # --------------------------------------------------------

    st.subheader(
        "Search and Filter History"
    )

    search_text = st.text_input(
        "Search history",
        placeholder=(
            "Search by employee text or recommendation title"
        ),
    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:

        selected_emotion = st.selectbox(
            "Emotion",
            options=[
                "All"
            ]
            + sorted(
                emotion.title()
                for emotion in emotions
            ),
        )

    with filter_col2:

        selected_polarity = st.selectbox(
            "Polarity",
            options=[
                "All"
            ]
            + sorted(
                polarity.title()
                for polarity in polarities
            ),
        )

    with filter_col3:

        selected_severity = st.selectbox(
            "Severity",
            options=[
                "All"
            ]
            + sorted(
                severity.title()
                for severity in severities
            ),
        )

    filter_col4, filter_col5 = st.columns(2)

    with filter_col4:

        selected_type = st.selectbox(
            "Recommendation Type",
            options=[
                "All"
            ]
            + sorted(
                recommendation_type.title()
                for recommendation_type
                in recommendation_types
            ),
        )

    with filter_col5:

        sort_order = st.selectbox(
            "Sort History",
            options=[
                "Newest first",
                "Oldest first",
            ],
        )

    # --------------------------------------------------------
    # APPLY FILTERS
    # --------------------------------------------------------

    filtered_history = []

    search_query = search_text.strip().lower()

    for record in history:

        if not isinstance(
            record,
            dict,
        ):
            continue

        record_emotional_state = record.get(
            "emotional_state",
            {},
        )

        if not isinstance(
            record_emotional_state,
            dict,
        ):
            record_emotional_state = {}

        dominant_emotion = str(
            record_emotional_state.get(
                "dominant_emotion",
                "",
            )
        ).lower()

        polarity = str(
            record_emotional_state.get(
                "polarity",
                "",
            )
        ).lower()

        severity = str(
            record_emotional_state.get(
                "severity",
                "",
            )
        ).lower()

        record_text = str(
            record.get(
                "text",
                "",
            )
        ).lower()

        record_recommendations = record.get(
            "recommendations",
            [],
        )

        if isinstance(
            record_recommendations,
            dict,
        ):

            record_recommendations = (
                record_recommendations.get(
                    "recommendations",
                    [],
                )
            )

        if not isinstance(
            record_recommendations,
            list,
        ):

            record_recommendations = []

        recommendation_titles = []
        recommendation_types_for_record = []

        for recommendation in record_recommendations:

            if not isinstance(
                recommendation,
                dict,
            ):
                continue

            title = str(
                recommendation.get(
                    "title",
                    "",
                )
            ).lower()

            recommendation_type = str(
                recommendation.get(
                    "type",
                    "",
                )
            ).lower()

            if title:

                recommendation_titles.append(
                    title
                )

            if recommendation_type:

                recommendation_types_for_record.append(
                    recommendation_type
                )

        searchable_text = (
            record_text
            + " "
            + " ".join(
                recommendation_titles
            )
        )

        if (
            search_query
            and search_query
            not in searchable_text
        ):

            continue

        if (
            selected_emotion != "All"
            and dominant_emotion
            != selected_emotion.lower()
        ):

            continue

        if (
            selected_polarity != "All"
            and polarity
            != selected_polarity.lower()
        ):

            continue

        if (
            selected_severity != "All"
            and severity
            != selected_severity.lower()
        ):

            continue

        if (
            selected_type != "All"
            and selected_type.lower()
            not in recommendation_types_for_record
        ):

            continue

        filtered_history.append(
            record
        )

    # --------------------------------------------------------
    # SORT HISTORY
    # --------------------------------------------------------

    def history_sort_key(record):

        return str(
            record.get(
                "created_at",
                "",
            )
        )

    filtered_history.sort(
        key=history_sort_key,
        reverse=(
            sort_order == "Newest first"
        ),
    )

    # --------------------------------------------------------
    # FILTER SUMMARY
    # --------------------------------------------------------

    st.write(
        f"Showing {len(filtered_history)} "
        f"of {len(history)} interaction(s)."
    )

    # --------------------------------------------------------
    # DISPLAY FILTERED HISTORY
    # --------------------------------------------------------

    if filtered_history:

        for record in filtered_history[:20]:

            created_at = record.get(
                "created_at",
                "Unknown time",
            )

            record_text = record.get(
                "text",
                "",
            )

            record_emotional_state = record.get(
                "emotional_state",
                {},
            )

            if not isinstance(
                record_emotional_state,
                dict,
            ):

                record_emotional_state = {}

            dominant_emotion = (
                record_emotional_state.get(
                    "dominant_emotion",
                    "N/A",
                )
            )

            intensity = (
                record_emotional_state.get(
                    "intensity",
                    0,
                )
            )

            try:

                intensity_value = float(
                    intensity
                )

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
                    f"{str(record_emotional_state.get('polarity', 'N/A')).title()}"
                )

                st.write(
                    f"**Severity:** "
                    f"{str(record_emotional_state.get('severity', 'N/A')).title()}"
                )

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

                            recommendation_title = (
                                recommendation.get(
                                    "title",
                                    "Unknown",
                                )
                            )

                            recommendation_type = (
                                recommendation.get(
                                    "type",
                                    "",
                                )
                            )

                            if recommendation_type:

                                st.write(
                                    f"- {recommendation_title} "
                                    f"({recommendation_type})"
                                )

                            else:

                                st.write(
                                    f"- {recommendation_title}"
                                )

    else:

        st.info(
            "No interactions match the selected search and filters."
        )

else:

    st.info(
        "No previous interaction history found "
        f"for user `{history_user_id}`."
    )


# ============================================================
# M4-T5 REPORT GENERATION AND EXPORT
# ============================================================

st.divider()

st.header(
    "Report Generation and Export"
)

latest_result = st.session_state.get(
    "latest_result"
)

latest_user_id = st.session_state.get(
    "latest_user_id",
    user_id.strip(),
)

if latest_result is not None:

    with st.spinner(
        "Preparing wellness report..."
    ):

        latest_trend_result = get_emotional_trend(
            latest_user_id
        )

    latest_history = st.session_state.get(
        "interaction_history",
        [],
    )

    try:

        report_pdf = create_pdf_report(
            user_id=latest_user_id,
            result=latest_result,
            trend_result=latest_trend_result,
            history=latest_history,
        )

        st.download_button(
            label="Download Wellness Report",
            data=report_pdf,
            file_name=(
                "moodmentor_wellness_report.pdf"
            ),
            mime="application/pdf",
        )

    except Exception as exc:

        st.error(
            f"Unable to generate the wellness report: {exc}"
        )

else:

    st.info(
        "Analyze an employee check-in first "
        "to generate a wellness report."
    )