"""
Task 9.9 - Baseline vs Advanced Recommendation Comparison
"""

import json


BASELINE_PATH = "ml/evaluation/baseline_results.json"
ADVANCED_METRICS_PATH = "ml/evaluation/advanced_metrics.json"
RANKING_PATH = "ml/evaluation/ranking_metrics.json"
DIVERSITY_PATH = "ml/evaluation/diversity_metrics.json"

OUTPUT_PATH = "ml/evaluation/comparison_metrics.json"


def main():

    print("=" * 70)
    print("TASK 9.9 - BASELINE VS ADVANCED COMPARISON")
    print("=" * 70)

    with open(
        BASELINE_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        baseline = json.load(file)

    with open(
        ADVANCED_METRICS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        advanced = json.load(file)

    with open(
        RANKING_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        advanced_ranking = json.load(file)

    with open(
        DIVERSITY_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        advanced_diversity = json.load(file)

    comparison = {
        "precision_at_3": {
            "baseline": baseline["macro_precision_at_3"],
            "advanced": advanced["macro_precision_at_3"],
        },
        "recall_at_3": {
            "baseline": baseline["macro_recall_at_3"],
            "advanced": advanced["macro_recall_at_3"],
        },
        "f1": {
            "baseline": baseline["macro_f1"],
            "advanced": advanced["macro_f1_score"],
        },
        "mrr": {
            "baseline": baseline["mean_mrr"],
            "advanced": advanced_ranking[
                "mean_reciprocal_rank"
            ],
        },
        "ndcg_at_3": {
            "baseline": baseline["mean_ndcg_at_3"],
            "advanced": advanced_ranking[
                "mean_ndcg_at_3"
            ],
        },
        "diversity": {
            "baseline_unique_items": baseline[
                "unique_recommendations_used"
            ],
            "advanced_unique_items": advanced_diversity[
                "unique_recommendations_used"
            ],
            "advanced_catalog_coverage_percent":
                advanced_diversity[
                    "catalog_coverage_percent"
                ],
        },
    }

    print("\n" + "-" * 70)
    print(
        f"{'Metric':<20}"
        f"{'Baseline':>15}"
        f"{'Advanced':>15}"
        f"{'Winner':>15}"
    )
    print("-" * 70)

    metrics = [
        (
            "Precision@3",
            comparison["precision_at_3"],
        ),
        (
            "Recall@3",
            comparison["recall_at_3"],
        ),
        (
            "F1",
            comparison["f1"],
        ),
        (
            "MRR",
            comparison["mrr"],
        ),
        (
            "NDCG@3",
            comparison["ndcg_at_3"],
        ),
    ]

    advanced_wins = 0
    baseline_wins = 0

    for metric_name, values in metrics:

        baseline_value = values["baseline"]
        advanced_value = values["advanced"]

        if advanced_value > baseline_value:
            winner = "Advanced"
            advanced_wins += 1

        elif baseline_value > advanced_value:
            winner = "Baseline"
            baseline_wins += 1

        else:
            winner = "Tie"

        print(
            f"{metric_name:<20}"
            f"{baseline_value:>15.4f}"
            f"{advanced_value:>15.4f}"
            f"{winner:>15}"
        )

    print("-" * 70)

    print(
        f"\nAdvanced wins : {advanced_wins}"
    )

    print(
        f"Baseline wins : {baseline_wins}"
    )

    print(
        "\nAdvanced system currently improves "
        "ranking quality (NDCG@3) and diversity, "
        "but requires improvement in precision, "
        "recall, F1 and MRR."
    )

    comparison["advanced_wins"] = advanced_wins
    comparison["baseline_wins"] = baseline_wins

    comparison["current_conclusion"] = (
        "Advanced ML improves ranking quality and "
        "recommendation diversity, but does not yet "
        "outperform the baseline on all recommendation "
        "quality metrics. Poor-performing cases should "
        "be improved and retested in Task 9.10."
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            comparison,
            file,
            indent=2,
        )

    print(
        f"\nComparison saved to: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()