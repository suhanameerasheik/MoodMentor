"""
Task 9.8 - Recommendation Diversity Evaluation

Measures:
- Unique recommendations across the evaluation set
- Catalog coverage
- Average unique recommendations per test case
- Per-test-case Top-K diversity
"""

import json


RESULTS_PATH = "ml/evaluation/advanced_results.json"


# Current wellness recommendation catalog.
CATALOG = {
    "breathing_01",
    "mindfulness_01",
    "walk_01",
    "break_01",
    "music_01",
    "journaling_01",
    "gratitude_01",
    "social_01",
    "focus_01",
    "celebrate_01",
    "relax_01",
    "planning_01",
}


def main():

    print("=" * 70)
    print("TASK 9.8 - RECOMMENDATION DIVERSITY EVALUATION")
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

    all_recommendations = set()
    total_unique_per_case = 0

    diversity_results = []

    print(
        f"\nEvaluating {len(successful_results)} test cases"
    )

    for result in successful_results:

        recommended = result["recommended"]

        unique_recommendations = set(
            recommended
        )

        all_recommendations.update(
            unique_recommendations
        )

        unique_count = len(
            unique_recommendations
        )

        total_unique_per_case += unique_count

        diversity_results.append(
            {
                "test_id": result["test_id"],
                "recommended": recommended,
                "unique_recommendations": unique_count,
                "top_k": len(recommended),
                "diversity_ratio": round(
                    unique_count / len(recommended),
                    4,
                )
                if recommended
                else 0.0,
            }
        )

        print("-" * 70)
        print(f"Test: {result['test_id']}")
        print(f"Recommended : {recommended}")
        print(
            f"Unique      : {unique_count}/{len(recommended)}"
        )
        print(
            f"Diversity   : "
            f"{unique_count / len(recommended) * 100:.2f}%"
            if recommended
            else "Diversity   : 0.00%"
        )

    total_catalog_items = len(CATALOG)

    unique_recommendation_count = len(
        all_recommendations
    )

    catalog_coverage = (
        unique_recommendation_count
        / total_catalog_items
    ) * 100

    average_unique_per_case = (
        total_unique_per_case
        / len(successful_results)
    )

    average_diversity_ratio = (
        sum(
            result["diversity_ratio"]
            for result in diversity_results
        )
        / len(diversity_results)
    )

    unused_items = sorted(
        CATALOG - all_recommendations
    )

    print("\n" + "=" * 70)
    print("OVERALL DIVERSITY RESULTS")
    print("=" * 70)

    print(
        f"\nUnique recommendations used : "
        f"{unique_recommendation_count}"
    )

    print(
        f"Total catalog size           : "
        f"{total_catalog_items}"
    )

    print(
        f"Catalog coverage             : "
        f"{catalog_coverage:.2f}%"
    )

    print(
        f"Average unique per test      : "
        f"{average_unique_per_case:.2f}"
    )

    print(
        f"Average Top-K diversity      : "
        f"{average_diversity_ratio * 100:.2f}%"
    )

    print(
        f"Unused catalog items         : "
        f"{unused_items}"
    )

    print(
        f"\nRecommendations used         : "
        f"{sorted(all_recommendations)}"
    )

    output = {
        "metric": "recommendation_diversity",
        "test_cases": len(successful_results),
        "top_k": 3,
        "catalog_size": total_catalog_items,
        "unique_recommendations_used": unique_recommendation_count,
        "catalog_coverage_percent": round(
            catalog_coverage,
            2,
        ),
        "average_unique_per_test": round(
            average_unique_per_case,
            2,
        ),
        "average_top_k_diversity_percent": round(
            average_diversity_ratio * 100,
            2,
        ),
        "unused_catalog_items": unused_items,
        "recommendations_used": sorted(
            all_recommendations
        ),
        "per_test_case": diversity_results,
    }

    output_path = (
        "ml/evaluation/diversity_metrics.json"
    )

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
        f"\nDiversity metrics saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()