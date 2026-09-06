from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


# Path of our trained BERT model
MODEL_PATH = "./ml/models/emotion_bert/final"


print("Loading emotion model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH
)

model.eval()

print("Emotion model loaded successfully.")


def analyze_emotion(text):

    # Convert text into BERT input
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    # Disable gradient calculation because we are only predicting
    with torch.no_grad():

        outputs = model(**inputs)

    # Convert model output into probabilities
    probabilities = torch.softmax(
        outputs.logits,
        dim=1
    )

    # Find the emotion with highest probability
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