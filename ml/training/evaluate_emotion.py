from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


print("Loading emotion dataset...")

dataset = load_dataset("dair-ai/emotion")

label_names = dataset["train"].features["label"].names

print("\nEmotion labels:")
print(label_names)


print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    "bert-base-uncased"
)

print("Tokenizer loaded successfully.")


def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=128
    )


print("\nTokenizing dataset...")

tokenized_dataset = dataset.map(
    tokenize_function,
    batched=True
)

print("Dataset tokenization completed.")


print("\nLoading trained BERT model...")

model_path = "./ml/models/emotion_bert/checkpoints/checkpoint-4000"

model = AutoModelForSequenceClassification.from_pretrained(
    model_path,
    num_labels=len(label_names)
)

print("Trained BERT model loaded successfully.")


def compute_metrics(eval_prediction):

    predictions, labels = eval_prediction

    predicted_labels = np.argmax(predictions, axis=1)

    accuracy = accuracy_score(
        labels,
        predicted_labels
    )

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels,
        predicted_labels,
        average="weighted",
        zero_division=0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


print("\nCreating evaluation trainer...")

training_args = TrainingArguments(
    output_dir="./ml/models/emotion_bert/evaluation",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    compute_metrics=compute_metrics
)


print("\nEvaluating model on test dataset...")

test_results = trainer.evaluate(
    tokenized_dataset["test"]
)


print("\n======================================")
print("BERT TEST RESULTS")
print("======================================")

print("Test Accuracy :", test_results["eval_accuracy"])
print("Test Precision:", test_results["eval_precision"])
print("Test Recall   :", test_results["eval_recall"])
print("Test F1 Score :", test_results["eval_f1"])

print("======================================")