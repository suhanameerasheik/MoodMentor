"""
Task 9.3 - Advanced ML Recommendation Evaluation

Runs the existing Advanced ML recommendation system against
the controlled Task 9 evaluation dataset.

This script does NOT modify the production recommendation system.
"""

import csv
import json
import time
import requests


API_URL = "http://127.0.0.1:8000/recommend"

DATASET_PATH = "ml/evaluation/test_dataset.csv"

TOP_K = 3


def load_test_dataset():
    """Load the controlled evaluation dataset."""

    test_cases = []

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["expected_recommendations"] = [
                item.strip()
                for item in row["expected_recommendations"].split(";")
            ]

            row["preferences"] = [
                item.strip()
                for item in row["preferences"].split(";")
            ]

            row["intensity"] = float(row["intensity"])

            test_cases.append(row)

    return test_cases


def extract_recommendation_ids(response_data):
    """
    Extract recommendation IDs from the actual /recommend
    response structure.
    """

    recommendation_container = response_data.get(
        "recommendations",
        {},
    )

    recommendations = recommendation_container.get(
        "recommendations",
        [],
    )

    recommendation_ids = []

    for recommendation in recommendations[:TOP_K]:

        recommendation_id = (
            recommendation.get("id")
            or recommendation.get("recommendation_id")
        )

        if recommendation_id:
            recommendation_ids.append(recommendation_id)

    return recommendation_ids


def evaluate_case(test_case):
    """Run one evaluation test case."""

    payload = {
        "text": test_case["text"],
        "preferences": test_case["preferences"],
        "history": [],
        "top_k": TOP_K,
        "user_id": f"task9_{test_case['test_id']}",
    }

    start_time = time.perf_counter()

    response = requests.post(
        API_URL,
        json=payload,
        timeout=120,
    )

    end_time = time.perf_counter()

    response_time = end_time - start_time

    if response.status_code != 200:
        return {
            "test_id": test_case["test_id"],
            "status": "FAILED",
            "http_status": response.status_code,
            "response_time": round(response_time, 4),
            "error": response.text,
        }

    response_data = response.json()

    recommendation_ids = extract_recommendation_ids(
        response_data
    )

    expected_ids = test_case["expected_recommendations"]

    relevant = [
        recommendation_id
        for recommendation_id in recommendation_ids
        if recommendation_id in expected_ids
    ]

    return {
        "test_id": test_case["test_id"],
        "status": "SUCCESS",
        "text": test_case["text"],
        "expected": expected_ids,
        "recommended": recommendation_ids,
        "relevant": relevant,
        "relevant_count": len(relevant),
        "response_time": round(response_time, 4),
        "full_response": response_data,
    }


def main():
    print("=" * 70)
    print("TASK 9.3 - ADVANCED ML RECOMMENDATION EVALUATION")
    print("=" * 70)

    test_cases = load_test_dataset()

    print(f"\nLoaded {len(test_cases)} test cases.")
    print(f"Testing Top-K = {TOP_K}")
    print(f"API = {API_URL}\n")

    results = []

    for test_case in test_cases:

        print("-" * 70)
        print(f"Running {test_case['test_id']}...")
        print(f"Text: {test_case['text']}")

        try:
            result = evaluate_case(test_case)
            results.append(result)

            if result["status"] == "SUCCESS":

                print(
                    f"Expected     : "
                    f"{result['expected']}"
                )

                print(
                    f"Recommended  : "
                    f"{result['recommended']}"
                )

                print(
                    f"Relevant     : "
                    f"{result['relevant']}"
                )

                print(
                    f"Response time: "
                    f"{result['response_time']} seconds"
                )

            else:

                print(
                    f"FAILED - HTTP "
                    f"{result['http_status']}"
                )

                print(result["error"])

        except Exception as error:

            print(f"ERROR: {error}")

            results.append(
                {
                    "test_id": test_case["test_id"],
                    "status": "ERROR",
                    "error": str(error),
                }
            )

    output_path = "ml/evaluation/advanced_results.json"

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    print("\n" + "=" * 70)
    print("TASK 9.3 COMPLETE")
    print("=" * 70)

    successful = [
        result
        for result in results
        if result.get("status") == "SUCCESS"
    ]

    print(
        f"\nSuccessful tests: "
        f"{len(successful)}/{len(test_cases)}"
    )

    if successful:

        average_time = sum(
            result["response_time"]
            for result in successful
        ) / len(successful)

        print(
            f"Average response time: "
            f"{average_time:.4f} seconds"
        )

    print(
        f"\nRaw results saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()