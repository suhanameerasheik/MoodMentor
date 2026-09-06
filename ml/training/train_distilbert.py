from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support
)


# ============================================================
# 1. LOAD DATASET
# ============================================================

print("Loading emotion dataset...")

dataset = load_dataset("dair-ai/emotion")

print("\nDataset loaded successfully.")
print(dataset)


# ============================================================
# 2. GET EMOTION LABELS
# ============================================================

label_names = dataset["train"].features["label"].names

print("\nEmotion labels:")
print(label_names)


# Create label mappings
id2label = {
    i: label
    for i, label in enumerate(label_names)
}

label2id = {
    label: i
    for i, label in enumerate(label_names)
}


# ============================================================
# 3. LOAD DISTILBERT TOKENIZER
# ============================================================

print("\nLoading DistilBERT tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased"
)

print("DistilBERT tokenizer loaded successfully.")


# ============================================================
# 4. TOKENIZE DATASET
# ============================================================

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


# ============================================================
# 5. LOAD DISTILBERT MODEL
# ============================================================

print("\nLoading DistilBERT model...")

model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(label_names),
    id2label=id2label,
    label2id=label2id
)

print("DistilBERT model loaded successfully.")

print("Number of emotion classes:", len(label_names))
print("Labels:", label_names)


# ============================================================
# 6. EVALUATION METRICS
# ============================================================

def compute_metrics(eval_prediction):

    predictions, labels = eval_prediction

    predicted_labels = np.argmax(
        predictions,
        axis=1
    )

    accuracy = accuracy_score(
        labels,
        predicted_labels
    )

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels,
        predicted_labels,
        average="macro",
        zero_division=0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "macro_f1": f1
    }


# ============================================================
# 7. TRAINING CONFIGURATION
# ============================================================

print("\nConfiguring DistilBERT training...")

training_args = TrainingArguments(

    output_dir="./ml/models/emotion_distilbert/checkpoints",

    eval_strategy="epoch",

    save_strategy="epoch",

    learning_rate=2e-5,

    per_device_train_batch_size=8,

    per_device_eval_batch_size=8,

    num_train_epochs=2,

    weight_decay=0.01,

    logging_steps=100,

    load_best_model_at_end=True,

    metric_for_best_model="macro_f1",

    greater_is_better=True,

    report_to="none"
)


# ============================================================
# 8. CREATE TRAINER
# ============================================================

trainer = Trainer(

    model=model,

    args=training_args,

    train_dataset=tokenized_dataset["train"],

    eval_dataset=tokenized_dataset["validation"],

    compute_metrics=compute_metrics
)


print("Training configuration completed.")


# ============================================================
# 9. START TRAINING
# ============================================================

print("\n======================================")
print("STARTING DISTILBERT TRAINING")
print("======================================")

trainer.train()


print("\n======================================")
print("DISTILBERT TRAINING COMPLETED")
print("======================================")