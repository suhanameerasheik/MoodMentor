"""
Task 9.5 - Ranking Quality Evaluation

Calculates:
- MRR
- NDCG@3

using the controlled recommendation evaluation dataset.
"""

import json
import math


RESULTS_PATH = "ml/evaluation/advanced_results.json"

K = 3


def reciprocal_rank(expected, recommended):
    """
    Calculate Reciprocal Rank.

    Returns 1/rank of the first relevant recommendation.
    Returns 0 if no relevant recommendation is found.
    """

    expected_set = set(expected)

    for rank, recommendation_id in enumerate(
        recommended[:K],
        start=1,
    ):
        if recommendation_id in expected_set:
            return 1.0 / rank

    return 0.0


def dcg_at_k(expected, recommended):
    """
    Calculate Discounted Cumulative Gain.

    Expected ranking order is used to give higher relevance
    to recommendations appearing earlier in the expected list.
    """

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

        dcg += relevance / math.log2(rank + 1)

    return dcg


def ideal_dcg_at_k(expected):
    """
    Calculate the ideal DCG for the expected ranking.
    """

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

        ideal_dcg += relevance / math.log2(rank + 1)

    return ideal_dcg


def ndcg_at_k(expected, recommended):
    """
    Calculate NDCG@K.
    """

    ideal_dcg = ideal_dcg_at_k(expected)

    if ideal_dcg == 0:
        return 0.0

    dcg = dcg_at_k(
        expected,
        recommended,
    )

    return dcg / ideal_dcg


def main():

    print("=" * 70)
    print("TASK 9.5 - RANKING QUALITY EVALUATION")
    print("=" * 70)

    with open(
        RESULTS_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        results = json.load(file)

    successful_results = [
        result
        for result in results
        if result.get("status") == "SUCCESS"
    ]

    if not successful_results:
        print("\nNo successful evaluation results found.")
        return

    total_mrr = 0.0
    total_ndcg = 0.0

    ranking_results = []

    print(f"\nEvaluating {len(successful_results)} test cases")
    print(f"K = {K}\n")

    for result in successful_results:

        expected = result["expected"]
        recommended = result["recommended"]

        mrr = reciprocal_rank(
            expected,
            recommended,
        )

        ndcg = ndcg_at_k(
            expected,
            recommended,
        )

        ranking_results.append(
            {
                "test_id": result["test_id"],
                "expected": expected,
                "recommended": recommended,
                "mrr": round(mrr, 4),
                "ndcg_at_3": round(ndcg, 4),
            }
        )

        total_mrr += mrr
        total_ndcg += ndcg

        print("-" * 70)
        print(f"Test: {result['test_id']}")
        print(f"Expected    : {expected}")
        print(f"Recommended : {recommended}")
        print(f"MRR         : {mrr:.4f}")
        print(f"NDCG@3      : {ndcg:.4f}")

    count = len(successful_results)

    mean_mrr = total_mrr / count
    mean_ndcg = total_ndcg / count

    print("\n" + "=" * 70)
    print("OVERALL RANKING RESULTS")
    print("=" * 70)

    print(f"\nMean Reciprocal Rank : {mean_mrr:.4f}")
    print(f"Mean NDCG@3         : {mean_ndcg:.4f}")

    output = {
        "k": K,
        "test_cases": count,
        "mean_reciprocal_rank": round(
            mean_mrr,
            4,
        ),
        "mean_ndcg_at_3": round(
            mean_ndcg,
            4,
        ),
        "per_test_case": ranking_results,
    }

    output_path = "ml/evaluation/ranking_metrics.json"

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

    print(
        f"\nRanking metrics saved to: {output_path}"
    )


if __name__ == "__main__":
    main()