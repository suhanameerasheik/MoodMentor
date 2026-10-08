"""
Task 9.10 - Advanced Recommendation Retest

Uses fresh user IDs so previous Task 9 evaluation history
does not influence the results.
"""

import csv
import json
import time
import requests


DATASET_PATH = "ml/evaluation/test_dataset.csv"
OUTPUT_PATH = "ml/evaluation/advanced_retest_results.json"

API_URL = "http://127.0.0.1:8000/recommend"


def load_dataset():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return list(csv.DictReader(file))


def parse_list(value):
    return [
        item.strip()
        for item in str(value).split(";")
        if item.strip()
    ]


def main():

    print("=" * 70)
    print("TASK 9.10 - ADVANCED ML RETEST")
    print("=" * 70)

    dataset = load_dataset()

    results = []

    successful_tests = 0

    for test_case in dataset:

        test_id = test_case["test_id"]

        expected = parse_list(
            test_case["expected_recommendations"]
        )

        preferences = parse_list(
            test_case["preferences"]
        )

        payload = {
            "text": test_case["text"],
            "preferences": preferences,
            "history": [],
            "top_k": 3,

            # IMPORTANT:
            # Fresh user ID prevents previous Task 9
            # history from affecting this retest.
            "user_id": f"task9_retest_{test_id}"
        }

        print("\n" + "-" * 70)
        print(f"Testing {test_id}")

        start_time = time.perf_counter()

        try:

            response = requests.post(
                API_URL,
                json=payload,
                timeout=60
            )

            elapsed_time = (
                time.perf_counter()
                - start_time
            )

            response.raise_for_status()

            response_data = response.json()

            recommendation_container = (
                response_data.get(
                    "recommendations",
                    {}
                )
            )

            recommendations = (
                recommendation_container.get(
                    "recommendations",
                    []
                )
            )

            recommended_ids = [
                recommendation["id"]
                for recommendation in recommendations
                if recommendation.get("id")
            ]

            relevant_ids = [
                recommendation_id
                for recommendation_id
                in recommended_ids
                if recommendation_id in expected
            ]

            result = {
                "test_id": test_id,
                "status": "success",
                "text": test_case["text"],
                "expected": expected,
                "recommended": recommended_ids,
                "relevant": relevant_ids,
                "relevant_count": len(relevant_ids),
                "response_time": round(
                    elapsed_time,
                    4
                ),
                "full_response": response_data
            }

            successful_tests += 1

            print(
                f"Expected      : {expected}"
            )

            print(
                f"Recommended   : {recommended_ids}"
            )

            print(
                f"Relevant      : {len(relevant_ids)}"
            )

            print(
                f"Response time : {elapsed_time:.4f}s"
            )

        except Exception as error:

            result = {
                "test_id": test_id,
                "status": "failed",
                "text": test_case["text"],
                "expected": expected,
                "recommended": [],
                "relevant": [],
                "relevant_count": 0,
                "response_time": None,
                "error": str(error)
            }

            print(
                f"ERROR: {error}"
            )

        results.append(result)

    successful_results = [
        result
        for result in results
        if result["status"] == "success"
    ]

    if successful_results:

        average_response_time = (
            sum(
                result["response_time"]
                for result in successful_results
            )
            /
            len(successful_results)
        )

    else:
        average_response_time = 0.0

    output = {
        "test_cases": len(dataset),
        "successful_tests": successful_tests,
        "average_response_time": round(
            average_response_time,
            4
        ),
        "results": results
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2
        )

    print("\n" + "=" * 70)

    print(
        f"Successful tests : "
        f"{successful_tests}/{len(dataset)}"
    )

    print(
        f"Average response : "
        f"{average_response_time:.4f}s"
    )

    print(
        f"Results saved to: "
        f"{OUTPUT_PATH}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()