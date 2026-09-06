from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import AutoTokenizer

print("Loading emotion dataset...")

dataset = load_dataset("dair-ai/emotion")

print("\nDataset structure:")
print(dataset)

print("\nEmotion labels:")
print(dataset["train"].features["label"].names)

print("\nFirst training example:")
print(dataset["train"][0])

print("\nLoading BERT tokenizer...")

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

print("BERT tokenizer loaded successfully.")
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

print("\nTokenized example:")
print(tokenized_dataset["train"][0])
from transformers import AutoModelForSequenceClassification

print("\nLoading BERT model...")

label_names = dataset["train"].features["label"].names

id2label = {i: label for i, label in enumerate(label_names)}
label2id = {label: i for i, label in enumerate(label_names)}

model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=len(label_names),
    id2label=id2label,
    label2id=label2id
)

print("BERT model loaded successfully.")
print("Number of emotion classes:", len(label_names))
print("Labels:", label_names)
def compute_metrics(eval_prediction):
    predictions, labels = eval_prediction

    predicted_labels = np.argmax(predictions, axis=1)

    accuracy = accuracy_score(labels, predicted_labels)

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


print("\nConfiguring BERT training...")

training_args = TrainingArguments(
    output_dir="./ml/models/emotion_bert/checkpoints",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=2,
    weight_decay=0.01,
    logging_steps=100,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    compute_metrics=compute_metrics
)

print("Training configuration completed.")
print("\nStarting BERT training...")

trainer.train()

print("\nBERT training completed.")
print("\nEvaluating BERT model on test dataset...")

test_results = trainer.evaluate(
    tokenized_dataset["test"]
)

print("\nTest Results:")
print(test_results)