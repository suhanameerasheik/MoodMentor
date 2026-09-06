# ============================================================
# ISEAR BENCHMARK VALIDATION
# BERT Emotion Model vs ISEAR Test Dataset
# ============================================================

import sys
from pathlib import Path

# ------------------------------------------------------------
# Fix Python import path
# ------------------------------------------------------------

sys.path.append(str(Path(__file__).resolve().parents[2]))


# ------------------------------------------------------------
# Imports
# ------------------------------------------------------------

import torch

from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "./ml/models/emotion_bert/final"

# ISEAR contains:
# joy, fear, anger, sadness, disgust, shame, guilt
#
# Our BERT model contains:
# sadness, joy, love, anger, fear, surprise
#
# Therefore, only these four emotions can be
# directly compared.

SHARED_EMOTIONS = {
    "joy",
    "fear",
    "anger",
    "sadness"
}


# ============================================================
# START
# ============================================================

print("======================================")
print("ISEAR BENCHMARK VALIDATION")
print("======================================")


# ============================================================
# STEP 1 — LOAD ISEAR DATASET
# ============================================================

print("\nLoading ISEAR dataset...")

dataset = load_dataset(
    "savalera/isear-from-original",
    "filtered"
)

print("\nDataset loaded.")
print(dataset)


# ============================================================
# STEP 2 — USE TEST SPLIT
# ============================================================

data = dataset["test"]

print("\nUsing dataset split: TEST")
print("Number of test samples:", len(data))


# ============================================================
# STEP 3 — DISPLAY DATASET COLUMNS
# ============================================================

print("\nDataset columns:")
print(data.column_names)


# ============================================================
# STEP 4 — SELECT CORRECT COLUMNS
# ============================================================

# SIT = actual ISEAR situation/text
# Field1 = actual emotion label

text_column = "SIT"
label_column = "Field1"

print("\nUsing text column:", text_column)
print("Using emotion column:", label_column)


# ============================================================
# STEP 5 — CHECK REQUIRED COLUMNS
# ============================================================

if text_column not in data.column_names:

    raise ValueError(
        f"Text column '{text_column}' was not found."
    )


if label_column not in data.column_names:

    raise ValueError(
        f"Emotion column '{label_column}' was not found."
    )


# ============================================================
# STEP 6 — SHOW SAMPLE DATA
# ============================================================

print("\nSample ISEAR records:")

for i in range(min(3, len(data))):

    print("\nSample", i + 1)

    print("Text:")
    print(data[i][text_column])

    print("Expected emotion:")
    print(data[i][label_column])


# ============================================================
# STEP 7 — FILTER SHARED EMOTIONS
# ============================================================

print("\n======================================")
print("FILTERING SHARED EMOTIONS")
print("======================================")


texts = []
true_labels = []

ignored_count = 0


for row in data:

    text = row[text_column]
    label = row[label_column]

    # Make sure text is a string
    if text is None:
        text = ""

    text = str(text).strip()

    # Make sure label is a string
    if isinstance(label, str):

        label = label.strip().lower()

    else:

        label = str(label).strip().lower()


    # Use only emotions supported by our BERT model

    if label in SHARED_EMOTIONS:

        # Ignore empty text
        if text != "":

            texts.append(text)
            true_labels.append(label)

        else:

            ignored_count += 1

    else:

        ignored_count += 1


print("\nShared emotions:")
print(sorted(SHARED_EMOTIONS))

print("\nSamples used for evaluation:")
print(len(texts))

print("Samples ignored:")
print(ignored_count)


# ============================================================
# STEP 8 — CHECK DATA
# ============================================================

if len(texts) == 0:

    raise ValueError(
        "No samples with shared emotions were found."
    )


# ============================================================
# STEP 9 — DISPLAY EMOTION DISTRIBUTION
# ============================================================

print("\n======================================")
print("ISEAR TEST EMOTION DISTRIBUTION")
print("======================================")


for emotion in sorted(SHARED_EMOTIONS):

    count = true_labels.count(emotion)

    print(
        f"{emotion:10s}: {count}"
    )


# ============================================================
# STEP 10 — LOAD BERT MODEL
# ============================================================

print("\n======================================")
print("LOADING BERT MODEL")
print("======================================")


print("\nModel path:")
print(MODEL_PATH)


tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH
)


model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH
)


model.eval()


print("\nBERT model loaded successfully.")


# ============================================================
# STEP 11 — DISPLAY MODEL LABELS
# ============================================================

print("\nBERT model labels:")

print(model.config.id2label)


# ============================================================
# STEP 12 — CREATE LABEL MAPPING
# ============================================================

model_labels = {
    int(index): label.lower()
    for index, label
    in model.config.id2label.items()
}


print("\nProcessed model labels:")

print(model_labels)


# ============================================================
# STEP 13 — VERIFY COMPATIBILITY
# ============================================================

available_model_emotions = set(
    model_labels.values()
)


missing_emotions = (
    SHARED_EMOTIONS -
    available_model_emotions
)


if missing_emotions:

    raise ValueError(
        "The following shared emotions are missing "
        f"from the BERT model: {missing_emotions}"
    )


# ============================================================
# STEP 14 — RUN BERT PREDICTIONS
# ============================================================

print("\n======================================")
print("RUNNING BERT PREDICTIONS")
print("======================================")


predicted_labels = []

prediction_confidences = []

incorrect_predictions = []


for index, text in enumerate(texts):

    # --------------------------------------------------------
    # Tokenize text
    # --------------------------------------------------------

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )


    # --------------------------------------------------------
    # Run model
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model(**inputs)


    # --------------------------------------------------------
    # Convert logits into probabilities
    # --------------------------------------------------------

    probabilities = torch.softmax(
        outputs.logits,
        dim=1
    )[0]


    # --------------------------------------------------------
    # Get highest probability
    # --------------------------------------------------------

    predicted_index = torch.argmax(
        probabilities
    ).item()


    # --------------------------------------------------------
    # Get predicted emotion
    # --------------------------------------------------------

    predicted_emotion = model_labels[
        predicted_index
    ]


    # --------------------------------------------------------
    # Get confidence
    # --------------------------------------------------------

    confidence = probabilities[
        predicted_index
    ].item()


    confidence = round(
        confidence,
        4
    )


    # --------------------------------------------------------
    # Save prediction
    # --------------------------------------------------------

    predicted_labels.append(
        predicted_emotion
    )


    prediction_confidences.append(
        confidence
    )


    # --------------------------------------------------------
    # Save incorrect prediction
    # --------------------------------------------------------

    if predicted_emotion != true_labels[index]:

        incorrect_predictions.append({

            "text": text,

            "expected": true_labels[index],

            "predicted": predicted_emotion,

            "confidence": confidence
        })


    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    if (index + 1) % 100 == 0:

        print(
            f"Processed "
            f"{index + 1}/{len(texts)} samples..."
        )


print("\nPrediction completed.")


# ============================================================
# STEP 15 — OVERALL PERFORMANCE
# ============================================================

print("\n======================================")
print("OVERALL PERFORMANCE")
print("======================================")


accuracy = accuracy_score(
    true_labels,
    predicted_labels
)


precision = precision_score(
    true_labels,
    predicted_labels,
    labels=sorted(SHARED_EMOTIONS),
    average="macro",
    zero_division=0
)


recall = recall_score(
    true_labels,
    predicted_labels,
    labels=sorted(SHARED_EMOTIONS),
    average="macro",
    zero_division=0
)


macro_f1 = f1_score(
    true_labels,
    predicted_labels,
    labels=sorted(SHARED_EMOTIONS),
    average="macro",
    zero_division=0
)


print(
    f"\nAccuracy : {accuracy:.4f} "
    f"({accuracy * 100:.2f}%)"
)


print(
    f"Precision: {precision:.4f}"
)


print(
    f"Recall   : {recall:.4f}"
)


print(
    f"Macro F1 : {macro_f1:.4f}"
)


# ============================================================
# STEP 16 — EMOTION-WISE PERFORMANCE
# ============================================================

print("\n======================================")
print("EMOTION-WISE PERFORMANCE")
print("======================================")


report = classification_report(
    true_labels,
    predicted_labels,
    labels=sorted(SHARED_EMOTIONS),
    target_names=sorted(SHARED_EMOTIONS),
    zero_division=0
)


print(report)


# ============================================================
# STEP 17 — CONFUSION MATRIX
# ============================================================

print("\n======================================")
print("CONFUSION MATRIX")
print("======================================")


emotion_order = sorted(
    SHARED_EMOTIONS
)


cm = confusion_matrix(
    true_labels,
    predicted_labels,
    labels=emotion_order
)


print("\nEmotion order:")
print(emotion_order)


print("\nRows = Expected")
print("Columns = Predicted\n")


print(cm)


# ============================================================
# STEP 18 — INCORRECT PREDICTIONS
# ============================================================

print("\n======================================")
print("INCORRECT PREDICTIONS")
print("======================================")


print(
    "\nTotal incorrect predictions:",
    len(incorrect_predictions)
)


if len(incorrect_predictions) > 0:

    print(
        "\nShowing first 10 incorrect predictions:\n"
    )


    for i, item in enumerate(
        incorrect_predictions[:10]
    ):

        print("--------------------------------------")

        print(
            f"Incorrect Prediction {i + 1}"
        )


        print("\nText:")
        print(item["text"])


        print(
            "\nExpected:",
            item["expected"]
        )


        print(
            "Predicted:",
            item["predicted"]
        )


        print(
            "Confidence:",
            item["confidence"]
        )


else:

    print(
        "\nNo incorrect predictions found."
    )


# ============================================================
# STEP 19 — CONFIDENCE ANALYSIS
# ============================================================

print("\n======================================")
print("CONFIDENCE ANALYSIS")
print("======================================")


if len(prediction_confidences) > 0:

    average_confidence = (
        sum(prediction_confidences)
        /
        len(prediction_confidences)
    )


    maximum_confidence = max(
        prediction_confidences
    )


    minimum_confidence = min(
        prediction_confidences
    )


    print(
        f"\nAverage confidence : "
        f"{average_confidence:.4f}"
    )


    print(
        f"Maximum confidence : "
        f"{maximum_confidence:.4f}"
    )


    print(
        f"Minimum confidence : "
        f"{minimum_confidence:.4f}"
    )


# ============================================================
# STEP 20 — SAMPLE CONFIDENCE SCORES
# ============================================================

print("\n======================================")
print("SAMPLE CONFIDENCE SCORES")
print("======================================")


for i in range(
    min(10, len(texts))
):

    print("\n--------------------------------------")


    print(
        "Text:",
        texts[i]
    )


    print(
        "Expected:",
        true_labels[i]
    )


    print(
        "Predicted:",
        predicted_labels[i]
    )


    print(
        "Confidence:",
        prediction_confidences[i]
    )


# ============================================================
# STEP 21 — CORRECT VS INCORRECT CONFIDENCE
# ============================================================

print("\n======================================")
print("CORRECT VS INCORRECT CONFIDENCE")
print("======================================")


correct_confidences = []

incorrect_confidences = []


for i in range(
    len(predicted_labels)
):

    if (
        predicted_labels[i]
        ==
        true_labels[i]
    ):

        correct_confidences.append(
            prediction_confidences[i]
        )

    else:

        incorrect_confidences.append(
            prediction_confidences[i]
        )


if len(correct_confidences) > 0:

    average_correct_confidence = (
        sum(correct_confidences)
        /
        len(correct_confidences)
    )


    print(
        "\nAverage confidence "
        "for correct predictions:",
        round(
            average_correct_confidence,
            4
        )
    )


if len(incorrect_confidences) > 0:

    average_incorrect_confidence = (
        sum(incorrect_confidences)
        /
        len(incorrect_confidences)
    )


    print(
        "Average confidence "
        "for incorrect predictions:",
        round(
            average_incorrect_confidence,
            4
        )
    )


# ============================================================
# STEP 22 — LABEL COMPATIBILITY
# ============================================================

print("\n======================================")
print("LABEL COMPATIBILITY")
print("======================================")


print(
    "\nISEAR emotions:"
)


print(
    "joy, fear, anger, sadness, "
    "disgust, shame, guilt"
)


print(
    "\nCurrent BERT emotions:"
)


print(
    "sadness, joy, love, anger, "
    "fear, surprise"
)


print(
    "\nDirectly evaluated:"
)


print(
    "joy, fear, anger, sadness"
)


print(
    "\nNot evaluated:"
)


print(
    "disgust, shame, guilt"
)


print(
    "\nReason:"
)


print(
    "The current BERT model does not "
    "contain disgust, shame, or guilt "
    "as output classes."
)


# ============================================================
# STEP 23 — FINAL SUMMARY
# ============================================================

print("\n======================================")
print("ISEAR VALIDATION SUMMARY")
print("======================================")


correct_count = (
    len(texts)
    -
    len(incorrect_predictions)
)


print(
    f"\nTest samples evaluated: "
    f"{len(texts)}"
)


print(
    f"Correct predictions: "
    f"{correct_count}"
)


print(
    f"Incorrect predictions: "
    f"{len(incorrect_predictions)}"
)


print(
    f"Accuracy: "
    f"{accuracy * 100:.2f}%"
)


print(
    f"Macro F1: "
    f"{macro_f1:.4f}"
)


print("\n======================================")
print("ISEAR BENCHMARK VALIDATION COMPLETE")
print("======================================")