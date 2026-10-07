"""
Task 9.9 - Baseline Recommendation Evaluation

Runs the simple baseline recommendation system
against the same controlled dataset used for the
advanced ML recommendation system.

Metrics:
- Precision@3
- Recall@3
- F1-score
- MRR
- NDCG@3
- Response time
- Diversity
"""

import csv
import json
import math
import time

from baseline import generate_baseline_recommendations


DATASET_PATH = "ml/evaluation/test_dataset.csv"
OUTPUT_PATH = "ml/evaluation/baseline_results.json"

K = 3


def precision_at_k(expected, recommended):
    expected_set = set(expected)
    recommended_k = recommended[:K]

    if not recommended_k:
        return 0.0

    relevant = sum(
        1
        for item in recommended_k
        if item in expected_set
    )

    return relevant / len(recommended_k)


def recall_at_k(expected, recommended):
    expected_set = set(expected)
    recommended_k = recommended[:K]

    if not expected_set:
        return 0.0

    relevant = sum(
        1
        for item in recommended_k
        if item in expected_set
    )

    return relevant / len(expected_set)


def f1_score(precision, recall):

    if precision + recall == 0:
        return 0.0

    return (
        2
        * precision
        * recall
        / (precision + recall)
    )


def reciprocal_rank(expected, recommended):

    expected_set = set(expected)

    for rank, recommendation_id in enumerate(
        recommended[:K],
        start=1,
    ):
        if recommendation_id in expected_set:
            return 1.0 / rank

    return 0.0


def dcg_at_k(expected, recommended):

    relevance_scores = {
        recommendation_id: len(expected) - index
        for index, recommendation_id in enumerate(expected)
    }

    dcg = 0.0

    for rank, recommendation_id in enumerate(
        recommended[:K],
        start=1,
    ):

        relevance = relevance_scores.get(
            recommendation_id,
            0,
        )

        dcg += (
            relevance
            / math.log2(rank + 1)
        )

    return dcg


def ideal_dcg_at_k(expected):

    ideal_recommendations = expected[:K]

    relevance_scores = {
        recommendation_id: len(expected) - index
        for index, recommendation_id in enumerate(expected)
    }

    ideal_dcg = 0.0

    for rank, recommendation_id in enumerate(
        ideal_recommendations,
        start=1,
    ):

        relevance = relevance_scores.get(
            recommendation_id,
            0,
        )

        ideal_dcg += (
            relevance
            / math.log2(rank + 1)
        )

    return ideal_dcg


def ndcg_at_k(expected, recommended):

    ideal_dcg = ideal_dcg_at_k(expected)

    if ideal_dcg == 0:
        return 0.0

    return (
        dcg_at_k(expected, recommended)
        / ideal_dcg
    )


def main():

    print("=" * 70)
    print("TASK 9.9 - BASELINE RECOMMENDATION EVALUATION")
    print("=" * 70)

    dataset = []

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            dataset.append(row)

    print(
        f"\nEvaluating {len(dataset)} test cases"
    )

    results = []

    total_precision = 0.0
    total_recall = 0.0
    total_f1 = 0.0
    total_mrr = 0.0
    total_ndcg = 0.0
    total_response_time = 0.0

    all_recommendations = set()

    for test_case in dataset:

        expected = (
            test_case["expected_recommendations"]
            .split(";")
        )

        start_time = time.perf_counter()

        recommendations = (
            generate_baseline_recommendations(
                text=test_case["text"],
                emotion=test_case["dominant_emotion"],
                intensity=float(
                    test_case["intensity"]
                ),
                polarity=test_case["polarity"],
                top_k=K,
            )
        )

        response_time = (
            time.perf_counter()
            - start_time
        )

        recommended = [
            recommendation["id"]
            for recommendation in recommendations
        ]

        precision = precision_at_k(
            expected,
            recommended,
        )

        recall = recall_at_k(
            expected,
            recommended,
        )

        f1 = f1_score(
            precision,
            recall,
        )

        mrr = reciprocal_rank(
            expected,
            recommended,
        )

        ndcg = ndcg_at_k(
            expected,
            recommended,
        )

        all_recommendations.update(
            recommended
        )

        total_precision += precision
        total_recall += recall
        total_f1 += f1
        total_mrr += mrr
        total_ndcg += ndcg
        total_response_time += response_time

        result = {
            "test_id": test_case["test_id"],
            "expected": expected,
            "recommended": recommended,
            "precision_at_3": round(
                precision,
                4,
            ),
            "recall_at_3": round(
                recall,
                4,
            ),
            "f1": round(
                f1,
                4,
            ),
            "mrr": round(
                mrr,
                4,
            ),
            "ndcg_at_3": round(
                ndcg,
                4,
            ),
            "response_time": round(
                response_time,
                6,
            ),
            "unique_recommendations": len(
                set(recommended)
            ),
        }

        results.append(result)

        print("-" * 70)
        print(f"Test: {test_case['test_id']}")
        print(f"Expected    : {expected}")
        print(f"Recommended : {recommended}")
        print(
            f"Precision@3 : {precision:.4f}"
        )
        print(
            f"Recall@3    : {recall:.4f}"
        )
        print(
            f"F1          : {f1:.4f}"
        )
        print(
            f"MRR         : {mrr:.4f}"
        )
        print(
            f"NDCG@3      : {ndcg:.4f}"
        )
        print(
            f"Response    : "
            f"{response_time:.6f} seconds"
        )

    count = len(dataset)

    macro_precision = (
        total_precision / count
    )

    macro_recall = (
        total_recall / count
    )

    macro_f1 = (
        total_f1 / count
    )

    mean_mrr = (
        total_mrr / count
    )

    mean_ndcg = (
        total_ndcg / count
    )

    average_response_time = (
        total_response_time / count
    )

    print("\n" + "=" * 70)
    print("BASELINE OVERALL RESULTS")
    print("=" * 70)

    print(
        f"\nMacro Precision@3 : "
        f"{macro_precision:.4f}"
    )

    print(
        f"Macro Recall@3    : "
        f"{macro_recall:.4f}"
    )

    print(
        f"Macro F1          : "
        f"{macro_f1:.4f}"
    )

    print(
        f"Mean MRR          : "
        f"{mean_mrr:.4f}"
    )

    print(
        f"Mean NDCG@3       : "
        f"{mean_ndcg:.4f}"
    )

    print(
        f"Average response  : "
        f"{average_response_time:.6f} seconds"
    )

    print(
        f"Unique items used  : "
        f"{len(all_recommendations)}"
    )

    output = {
        "method": "baseline_keyword_matching",
        "test_cases": count,
        "k": K,
        "macro_precision_at_3": round(
            macro_precision,
            4,
        ),
        "macro_recall_at_3": round(
            macro_recall,
            4,
        ),
        "macro_f1": round(
            macro_f1,
            4,
        ),
        "mean_mrr": round(
            mean_mrr,
            4,
        ),
        "mean_ndcg_at_3": round(
            mean_ndcg,
            4,
        ),
        "average_response_time_seconds": round(
            average_response_time,
            6,
        ),
        "unique_recommendations_used": len(
            all_recommendations
        ),
        "per_test_case": results,
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
        )

    print(
        f"\nBaseline results saved to: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()