"""
Task 9.10 - Calculate metrics for advanced retest
"""

import json


INPUT_PATH = "ml/evaluation/advanced_retest_results.json"
OUTPUT_PATH = "ml/evaluation/advanced_retest_metrics.json"

K = 3


def precision_at_k(recommended, expected):
    recommended_k = recommended[:K]

    if not recommended_k:
        return 0.0

    relevant = sum(
        1
        for item in recommended_k
        if item in expected
    )

    return relevant / len(recommended_k)


def recall_at_k(recommended, expected):
    recommended_k = recommended[:K]

    if not expected:
        return 0.0

    relevant = sum(
        1
        for item in recommended_k
        if item in expected
    )

    return relevant / len(expected)


def f1_score(precision, recall):
    if precision + recall == 0:
        return 0.0

    return (
        2 * precision * recall
        / (precision + recall)
    )


def main():

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    results = data["results"]

    per_test_case = []

    precision_values = []
    recall_values = []
    f1_values = []

    for result in results:

        if result["status"] != "success":
            continue

        recommended = result["recommended"]
        expected = result["expected"]

        precision = precision_at_k(
            recommended,
            expected
        )

        recall = recall_at_k(
            recommended,
            expected
        )

        f1 = f1_score(
            precision,
            recall
        )

        precision_values.append(precision)
        recall_values.append(recall)
        f1_values.append(f1)

        per_test_case.append({
            "test_id": result["test_id"],
            "precision_at_3": round(
                precision,
                4
            ),
            "recall_at_3": round(
                recall,
                4
            ),
            "f1_score": round(
                f1,
                4
            )
        })

        print(
            f"{result['test_id']}: "
            f"P={precision:.4f} "
            f"R={recall:.4f} "
            f"F1={f1:.4f}"
        )

    macro_precision = (
        sum(precision_values)
        / len(precision_values)
    )

    macro_recall = (
        sum(recall_values)
        / len(recall_values)
    )

    macro_f1 = (
        sum(f1_values)
        / len(f1_values)
    )

    output = {
        "k": K,
        "test_cases": len(per_test_case),
        "macro_precision_at_3": round(
            macro_precision,
            4
        ),
        "macro_recall_at_3": round(
            macro_recall,
            4
        ),
        "macro_f1_score": round(
            macro_f1,
            4
        ),
        "per_test_case": per_test_case
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

    print("\n" + "=" * 60)

    print(
        f"Macro Precision@3 = "
        f"{macro_precision:.4f} "
        f"({macro_precision * 100:.2f}%)"
    )

    print(
        f"Macro Recall@3    = "
        f"{macro_recall:.4f} "
        f"({macro_recall * 100:.2f}%)"
    )

    print(
        f"Macro F1          = "
        f"{macro_f1:.4f} "
        f"({macro_f1 * 100:.2f}%)"
    )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()