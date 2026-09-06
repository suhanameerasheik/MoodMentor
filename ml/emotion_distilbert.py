from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


# ============================================================
# DISTILBERT MODEL PATH
# ============================================================

MODEL_PATH = "./ml/models/emotion_distilbert/final"


print("Loading DistilBERT emotion model...")


# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)


# Load trained model
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH
)


# Set model to evaluation mode
model.eval()


print("DistilBERT emotion model loaded successfully.")


# ============================================================
# EMOTION ANALYSIS FUNCTION
# ============================================================

def analyze_emotion_distilbert(text):

    # Convert text into DistilBERT inputs
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    # Disable gradient calculation during prediction
    with torch.no_grad():

        outputs = model(**inputs)


    # Convert logits into probabilities
    probabilities = torch.softmax(
        outputs.logits,
        dim=1
    )


    # Find emotion with highest probability
    predicted_id = torch.argmax(
        probabilities,
        dim=1
    ).item()


    # Get emotion name
    emotion = model.config.id2label[predicted_id]


    # Get confidence
    confidence = probabilities[0][predicted_id].item()


    return {
        "emotion": emotion,
        "confidence": round(confidence, 4)
    }