"""
Task 9.10 - Precision@K, Recall@K and F1-score Retest

Calculates recommendation quality metrics using the
latest Task 9.10 advanced recommendation retest results.
"""

import json


RESULTS_PATH = "ml/evaluation/advanced_retest_results.json"

K = 3


def calculate_metrics(expected, recommended):
    """
    Calculate Precision@K, Recall@K and F1-score.
    """

    expected_set = set(expected)

    recommended_at_k = recommended[:K]
    recommended_set = set(recommended_at_k)

    relevant_count = len(
        expected_set.intersection(
            recommended_set
        )
    )

    precision = (
        relevant_count / K
        if K > 0
        else 0.0
    )

    recall = (
        relevant_count / len(expected_set)
        if expected_set
        else 0.0
    )

    if precision + recall > 0:
        f1 = (
            2 * precision * recall
            / (precision + recall)
        )
    else:
        f1 = 0.0

    return (
        precision,
        recall,
        f1,
        relevant_count
    )


def load_results():

    with open(
        RESULTS_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    # Handle dictionary-based result files
    if isinstance(data, dict):

        # If results are stored inside a "results" key
        if isinstance(
            data.get("results"),
            list
        ):
            return data["results"]

        # If each test case is a dictionary value
        return list(data.values())

    # Handle normal list-based result files
    if isinstance(data, list):
        return data

    return []


def main():

    print("=" * 70)
    print(
        "TASK 9.10 - RECOMMENDATION QUALITY RETEST METRICS"
    )
    print("=" * 70)

    results = load_results()

    successful_results = []

    for result in results:

        if not isinstance(result, dict):
            continue

        # Accept SUCCESS status
        if result.get("status") == "SUCCESS":
            successful_results.append(result)

        # Also accept results without status
        # when expected/recommended fields exist
        elif (
            "expected" in result
            and "recommended" in result
        ):
            successful_results.append(result)

    if not successful_results:

        print(
            "\nNo successful evaluation results found."
        )

        return

    evaluated_results = []

    total_precision = 0.0
    total_recall = 0.0
    total_f1 = 0.0

    print(
        f"\nEvaluating {len(successful_results)} test cases"
    )

    print(f"K = {K}\n")

    for result in successful_results:

        expected = result["expected"]
        recommended = result["recommended"]

        (
            precision,
            recall,
            f1,
            relevant_count,
        ) = calculate_metrics(
            expected,
            recommended,
        )

        test_id = result.get(
            "test_id",
            result.get(
                "id",
                "UNKNOWN"
            )
        )

        evaluated_result = {
            "test_id": test_id,
            "expected": expected,
            "recommended": recommended,
            "relevant_count": relevant_count,
            "precision_at_3": round(
                precision,
                4,
            ),
            "recall_at_3": round(
                recall,
                4,
            ),
            "f1_score": round(
                f1,
                4,
            ),
        }

        evaluated_results.append(
            evaluated_result
        )

        total_precision += precision
        total_recall += recall
        total_f1 += f1

        print("-" * 70)

        print(
            f"Test: {test_id}"
        )

        print(
            f"Expected     : {expected}"
        )

        print(
            f"Recommended  : {recommended}"
        )

        print(
            f"Relevant     : {relevant_count}"
        )

        print(
            f"Precision@3  : {precision:.4f}"
        )

        print(
            f"Recall@3     : {recall:.4f}"
        )

        print(
            f"F1-score     : {f1:.4f}"
        )

    count = len(
        successful_results
    )

    macro_precision = (
        total_precision / count
    )

    macro_recall = (
        total_recall / count
    )

    macro_f1 = (
        total_f1 / count
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "OVERALL RETEST RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        f"\nMacro Precision@3 : "
        f"{macro_precision:.4f}"
    )

    print(
        f"Macro Recall@3    : "
        f"{macro_recall:.4f}"
    )

    print(
        f"Macro F1-score    : "
        f"{macro_f1:.4f}"
    )

    metrics_output = {
        "k": K,
        "test_cases": count,
        "macro_precision_at_3": round(
            macro_precision,
            4,
        ),
        "macro_recall_at_3": round(
            macro_recall,
            4,
        ),
        "macro_f1_score": round(
            macro_f1,
            4,
        ),
        "per_test_case": evaluated_results,
    }

    output_path = (
        "ml/evaluation/"
        "advanced_retest_metrics.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics_output,
            file,
            indent=2,
        )

    print(
        f"\nMetrics saved to: {output_path}"
    )


if __name__ == "__main__":
    main()