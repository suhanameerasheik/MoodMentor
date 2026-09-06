from transformers import AutoTokenizer, AutoModelForSequenceClassification


print("Loading trained DistilBERT model...")

checkpoint_path = "./ml/models/emotion_distilbert/checkpoints/checkpoint-4000"

final_model_path = "./ml/models/emotion_distilbert/final"


model = AutoModelForSequenceClassification.from_pretrained(
    checkpoint_path
)

tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased"
)


print("Saving final DistilBERT model...")

model.save_pretrained(final_model_path)

tokenizer.save_pretrained(final_model_path)


print("\n======================================")
print("DISTILBERT FINAL MODEL SAVED")
print("======================================")
print("Location:", final_model_path)