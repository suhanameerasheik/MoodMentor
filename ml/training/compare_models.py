import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

import numpy as np
import torch

from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


BERT_PATH = "./ml/models/emotion_bert/final"
DISTILBERT_PATH = "./ml/models/emotion_distilbert/final"


def evaluate_model(model_path, model_name):

    print("\n======================================")
    print(f"EVALUATING {model_name}")
    print("======================================")

    dataset = load_dataset("dair-ai/emotion")

    test_dataset = dataset["test"]

    tokenizer = AutoTokenizer.from_pretrained(model_path)

    model = AutoModelForSequenceClassification.from_pretrained(
        model_path
    )

    model.eval()

    predictions = []
    actual_labels = []

    print("Running predictions...")

    for example in test_dataset:

        text = example["text"]
        actual_label = example["label"]

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )

        with torch.no_grad():
            outputs = model(**inputs)

        predicted_label = torch.argmax(
            outputs.logits,
            dim=1
        ).item()

        predictions.append(predicted_label)
        actual_labels.append(actual_label)

    accuracy = accuracy_score(
        actual_labels,
        predictions
    )

    precision = precision_score(
        actual_labels,
        predictions,
        average="macro",
        zero_division=0
    )

    recall = recall_score(
        actual_labels,
        predictions,
        average="macro",
        zero_division=0
    )

    macro_f1 = f1_score(
        actual_labels,
        predictions,
        average="macro",
        zero_division=0
    )

    print("\nResults:")
    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"Macro F1  : {macro_f1:.4f}")

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "macro_f1": macro_f1
    }


print("======================================")
print("BERT vs DISTILBERT EVALUATION")
print("======================================")

bert_results = evaluate_model(
    BERT_PATH,
    "BERT"
)

distilbert_results = evaluate_model(
    DISTILBERT_PATH,
    "DISTILBERT"
)


print("\n======================================")
print("FINAL MODEL COMPARISON")
print("======================================")

print("\nMetric          BERT        DistilBERT")

print(
    f"Accuracy        "
    f"{bert_results['accuracy']:.4f}      "
    f"{distilbert_results['accuracy']:.4f}"
)

print(
    f"Precision       "
    f"{bert_results['precision']:.4f}      "
    f"{distilbert_results['precision']:.4f}"
)

print(
    f"Recall          "
    f"{bert_results['recall']:.4f}      "
    f"{distilbert_results['recall']:.4f}"
)

print(
    f"Macro F1        "
    f"{bert_results['macro_f1']:.4f}      "
    f"{distilbert_results['macro_f1']:.4f}"
)


if (
    distilbert_results["macro_f1"]
    > bert_results["macro_f1"]
):
    print("\nBetter model: DistilBERT")

elif (
    bert_results["macro_f1"]
    > distilbert_results["macro_f1"]
):
    print("\nBetter model: BERT")

else:
    print("\nBoth models have the same Macro F1.")