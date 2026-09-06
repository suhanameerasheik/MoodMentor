from transformers import AutoTokenizer, AutoModelForSequenceClassification

print("Loading trained BERT model...")

checkpoint_path = "./ml/models/emotion_bert/checkpoints/checkpoint-4000"

final_model_path = "./ml/models/emotion_bert/final"

model = AutoModelForSequenceClassification.from_pretrained(
    checkpoint_path
)

tokenizer = AutoTokenizer.from_pretrained(
    "bert-base-uncased"
)

print("Saving final model...")

model.save_pretrained(final_model_path)
tokenizer.save_pretrained(final_model_path)

print("\n======================================")
print("FINAL MODEL SAVED SUCCESSFULLY")
print("======================================")
print("Location:", final_model_path)