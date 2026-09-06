from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


# ============================================================
# MULTI-LABEL EMOTION MODEL
# ============================================================

MODEL_NAME = "SamLowe/roberta-base-go_emotions"


# Emotions required for the wellness platform
REQUIRED_EMOTIONS = [
    "joy",
    "sadness",
    "anger",
    "fear",
    "surprise",
    "disgust"
]


# Minimum probability required to detect an emotion
THRESHOLD = 0.50


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading multi-label emotion model...")


tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)


model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME
)


model.eval()


print("Multi-label emotion model loaded successfully.")


# ============================================================
# ANALYZE MULTI-LABEL EMOTION
# ============================================================

def analyze_multilabel_emotion(text):

    # --------------------------------------------------------
    # Convert text into model input
    # --------------------------------------------------------

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )


    # --------------------------------------------------------
    # Generate model prediction
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model(**inputs)


    # --------------------------------------------------------
    # Multi-label classification uses sigmoid
    # --------------------------------------------------------

    probabilities = torch.sigmoid(
        outputs.logits
    )[0]


    # --------------------------------------------------------
    # Store scores for all 28 emotions
    # --------------------------------------------------------

    all_scores = {}


    for emotion, score in zip(
        model.config.id2label.values(),
        probabilities
    ):

        all_scores[emotion.lower()] = round(
            score.item(),
            4
        )


    # --------------------------------------------------------
    # Keep only required emotions
    # --------------------------------------------------------

    required_scores = {

        emotion: all_scores.get(
            emotion,
            0.0
        )

        for emotion in REQUIRED_EMOTIONS
    }


    # --------------------------------------------------------
    # Detect emotions above threshold
    # --------------------------------------------------------

    detected_emotions = [

        emotion

        for emotion, score in required_scores.items()

        if score >= THRESHOLD
    ]


    # --------------------------------------------------------
    # Select primary emotion
    # --------------------------------------------------------

    if not detected_emotions:

        primary_emotion = max(
            required_scores,
            key=required_scores.get
        )

    else:

        primary_emotion = max(
            detected_emotions,
            key=lambda emotion:
                required_scores[emotion]
        )


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        "detected_emotions":
            detected_emotions,

        "primary_emotion":
            primary_emotion,

        "emotion_scores":
            required_scores
    }