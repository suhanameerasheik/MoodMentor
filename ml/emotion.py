from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

import torch


# ============================================================
# EMOTION MODEL
# ============================================================

MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading emotion model...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME
)

model.eval()

print("Emotion model loaded successfully.")


# ============================================================
# ANALYZE EMOTION
# ============================================================

def analyze_emotion(text):

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
    # Generate prediction
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model(**inputs)


    # --------------------------------------------------------
    # Convert logits to probabilities
    # --------------------------------------------------------

    probabilities = torch.softmax(
        outputs.logits,
        dim=1
    )


    # --------------------------------------------------------
    # Find highest probability
    # --------------------------------------------------------

    predicted_id = torch.argmax(
        probabilities,
        dim=1
    ).item()


    # --------------------------------------------------------
    # Get emotion name
    # --------------------------------------------------------

    emotion = model.config.id2label[
        predicted_id
    ]


    # --------------------------------------------------------
    # Get confidence
    # --------------------------------------------------------

    confidence = probabilities[
        0,
        predicted_id
    ].item()


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "emotion": emotion.lower(),
        "confidence": round(
            confidence,
            4
        )
    }