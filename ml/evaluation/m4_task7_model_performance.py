"""
M4-T7 - Model Performance and Stress Testing

Evaluates the actual MoodMentor emotion model and recommendation API.

Measures:
1. Emotion classification:
   - Accuracy
   - Macro Precision
   - Macro Recall
   - Macro F1
   - Inference time

2. Recommendation API:
   - Successful requests
   - Failed requests
   - Average response time
   - Minimum response time
   - Maximum response time
   - P95 response time

3. Stress testing:
   - 10 requests
   - 25 requests
   - 50 requests

This script does not modify the production model.
"""

import csv
import math
import time
import uuid

import requests
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
)

from ml.emotion import analyze_emotion


DATASET_PATH = "ml/evaluation/test_dataset.csv"
API_URL = "http://127.0.0.1:8000/recommend"

STRESS_LEVELS = [10, 25, 50]
TOP_K = 3


# ============================================================
# DATASET
# ============================================================

def load_dataset():
    """Load the controlled M4-T7 evaluation dataset."""

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return list(csv.DictReader(file))


# ============================================================
# PERCENTILE
# ============================================================

def percentile(values, percentile_value):
    """Calculate percentile using linear interpolation."""

    if not values:
        return 0.0

    sorted_values = sorted(values)

    position = (
        (len(sorted_values) - 1)
        * percentile_value
    )

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return sorted_values[lower]

    lower_value = sorted_values[lower]
    upper_value = sorted_values[upper]

    fraction = position - lower

    return (
        lower_value
        + (upper_value - lower_value)
        * fraction
    )


# ============================================================
# EMOTION MODEL EVALUATION
# ============================================================

def evaluate_emotion_model(dataset):

    print("\n" + "=" * 70)
    print("A. EMOTION MODEL PERFORMANCE")
    print("=" * 70)

    expected_labels = []
    predicted_labels = []
    inference_times = []

    per_case_results = []

    for test_case in dataset:

        text = test_case["text"]
        expected = test_case["dominant_emotion"]

        start_time = time.perf_counter()

        prediction = analyze_emotion(text)

        elapsed_time = (
            time.perf_counter()
            - start_time
        )

        predicted = prediction["emotion"]

        expected_labels.append(expected)
        predicted_labels.append(predicted)
        inference_times.append(elapsed_time)

        result = {
            "test_id": test_case["test_id"],
            "expected_emotion": expected,
            "predicted_emotion": predicted,
            "confidence": prediction["confidence"],
            "inference_time_seconds": round(
                elapsed_time,
                6,
            ),
            "correct": expected == predicted,
        }

        per_case_results.append(result)

        print("-" * 70)
        print(f"Test ID    : {test_case['test_id']}")
        print(f"Expected   : {expected}")
        print(f"Predicted  : {predicted}")
        print(
            f"Confidence : "
            f"{prediction['confidence']:.4f}"
        )
        print(
            f"Inference  : "
            f"{elapsed_time:.6f} seconds"
        )
        print(
            f"Correct    : "
            f"{expected == predicted}"
        )

    accuracy = accuracy_score(
        expected_labels,
        predicted_labels,
    )

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            expected_labels,
            predicted_labels,
            average="macro",
            zero_division=0,
        )
    )

    average_inference = (
        sum(inference_times)
        / len(inference_times)
        if inference_times
        else 0.0
    )

    minimum_inference = (
        min(inference_times)
        if inference_times
        else 0.0
    )

    maximum_inference = (
        max(inference_times)
        if inference_times
        else 0.0
    )

    p95_inference = percentile(
        inference_times,
        0.95,
    )

    print("\n" + "=" * 70)
    print("EMOTION MODEL OVERALL RESULTS")
    print("=" * 70)

    print(
        f"\nAccuracy        : "
        f"{accuracy:.4f}"
    )

    print(
        f"Macro Precision : "
        f"{precision:.4f}"
    )

    print(
        f"Macro Recall    : "
        f"{recall:.4f}"
    )

    print(
        f"Macro F1        : "
        f"{f1:.4f}"
    )

    print(
        f"Average Inference Time : "
        f"{average_inference:.6f} seconds"
    )

    print(
        f"Minimum Inference Time : "
        f"{minimum_inference:.6f} seconds"
    )

    print(
        f"Maximum Inference Time : "
        f"{maximum_inference:.6f} seconds"
    )

    print(
        f"P95 Inference Time    : "
        f"{p95_inference:.6f} seconds"
    )

    return {
        "test_cases": len(dataset),
        "accuracy": round(accuracy, 4),
        "macro_precision": round(
            precision,
            4,
        ),
        "macro_recall": round(
            recall,
            4,
        ),
        "macro_f1": round(
            f1,
            4,
        ),
        "average_inference_time_seconds": round(
            average_inference,
            6,
        ),
        "minimum_inference_time_seconds": round(
            minimum_inference,
            6,
        ),
        "maximum_inference_time_seconds": round(
            maximum_inference,
            6,
        ),
        "p95_inference_time_seconds": round(
            p95_inference,
            6,
        ),
        "per_test_case": per_case_results,
    }


# ============================================================
# RECOMMENDATION API STRESS TEST
# ============================================================

def run_stress_test(dataset, request_count):

    print("\n" + "-" * 70)
    print(
        f"STRESS TEST: {request_count} REQUESTS"
    )
    print("-" * 70)

    response_times = []
    successful = 0
    failed = 0

    for index in range(request_count):

        test_case = dataset[
            index % len(dataset)
        ]

        payload = {
            "text": test_case["text"],
            "preferences": [
                item.strip()
                for item in test_case[
                    "preferences"
                ].split(";")
                if item.strip()
            ],
            "history": [],
            "top_k": TOP_K,

            # Unique user ID prevents previous
            # evaluation history from affecting
            # the current request.
            "user_id": (
                f"m4t7_stress_"
                f"{request_count}_"
                f"{index}_"
                f"{uuid.uuid4().hex[:8]}"
            ),
        }

        start_time = time.perf_counter()

        try:

            response = requests.post(
                API_URL,
                json=payload,
                timeout=120,
            )

            elapsed_time = (
                time.perf_counter()
                - start_time
            )

            response_times.append(
                elapsed_time
            )

            if response.status_code == 200:
                successful += 1
            else:
                failed += 1

        except Exception:
            elapsed_time = (
                time.perf_counter()
                - start_time
            )

            response_times.append(
                elapsed_time
            )

            failed += 1

    total_requests = (
        successful + failed
    )

    success_rate = (
        successful / total_requests * 100
        if total_requests
        else 0.0
    )

    average_response = (
        sum(response_times)
        / len(response_times)
        if response_times
        else 0.0
    )

    minimum_response = (
        min(response_times)
        if response_times
        else 0.0
    )

    maximum_response = (
        max(response_times)
        if response_times
        else 0.0
    )

    p95_response = percentile(
        response_times,
        0.95,
    )

    print(
        f"Total requests    : "
        f"{total_requests}"
    )

    print(
        f"Successful        : "
        f"{successful}"
    )

    print(
        f"Failed            : "
        f"{failed}"
    )

    print(
        f"Success rate      : "
        f"{success_rate:.2f}%"
    )

    print(
        f"Average response  : "
        f"{average_response:.6f} seconds"
    )

    print(
        f"Minimum response  : "
        f"{minimum_response:.6f} seconds"
    )

    print(
        f"Maximum response  : "
        f"{maximum_response:.6f} seconds"
    )

    print(
        f"P95 response      : "
        f"{p95_response:.6f} seconds"
    )

    return {
        "request_count": request_count,
        "successful_requests": successful,
        "failed_requests": failed,
        "success_rate_percent": round(
            success_rate,
            2,
        ),
        "average_response_time_seconds": round(
            average_response,
            6,
        ),
        "minimum_response_time_seconds": round(
            minimum_response,
            6,
        ),
        "maximum_response_time_seconds": round(
            maximum_response,
            6,
        ),
        "p95_response_time_seconds": round(
            p95_response,
            6,
        ),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("M4-T7 - MODEL PERFORMANCE AND STRESS TESTING")
    print("=" * 70)

    dataset = load_dataset()

    print(
        f"\nLoaded {len(dataset)} evaluation cases."
    )

    print(
        f"API: {API_URL}"
    )

    # --------------------------------------------------------
    # Emotion model
    # --------------------------------------------------------

    emotion_results = evaluate_emotion_model(
        dataset
    )

    # --------------------------------------------------------
    # API stress testing
    # --------------------------------------------------------

    stress_results = []

    for request_count in STRESS_LEVELS:

        result = run_stress_test(
            dataset,
            request_count,
        )

        stress_results.append(result)

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    output = {
        "task": "M4-T7",
        "description": (
            "Model performance and stress testing"
        ),
        "emotion_model": (
            "j-hartmann/"
            "emotion-english-distilroberta-base"
        ),
        "emotion_evaluation": emotion_results,
        "stress_testing": stress_results,
    }

    output_path = (
        "ml/evaluation/"
        "m4_task7_results.json"
    )

    import json

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
        )

    print("\n" + "=" * 70)
    print("M4-T7 EVALUATION COMPLETE")
    print("=" * 70)

    print(
        f"\nResults saved to:"
        f"\n{output_path}"
    )


if __name__ == "__main__":
    main()