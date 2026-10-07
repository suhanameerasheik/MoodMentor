"""
Task 9.6 - User Acceptance Rate Evaluation

Controlled acceptance proxy:
A test case is considered accepted when the
top-ranked recommendation is present in the
expected recommendation list.

This is an offline evaluation proxy, not real
user feedback.
"""

import json


RESULTS_PATH = "ml/evaluation/advanced_results.json"


def main():

    print("=" * 70)
    print("TASK 9.6 - USER ACCEPTANCE RATE")
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

    accepted_count = 0
    acceptance_results = []

    print(
        "\nAcceptance rule:"
        "\nTop-ranked recommendation must be in expected recommendations.\n"
    )

    for result in successful_results:

        expected = result["expected"]
        recommended = result["recommended"]

        top_recommendation = (
            recommended[0]
            if recommended
            else None
        )

        accepted = (
            top_recommendation in expected
            if top_recommendation
            else False
        )

        if accepted:
            accepted_count += 1

        acceptance_results.append(
            {
                "test_id": result["test_id"],
                "expected": expected,
                "recommended": recommended,
                "top_recommendation": top_recommendation,
                "accepted": accepted,
            }
        )

        print("-" * 70)
        print(f"Test: {result['test_id']}")
        print(f"Expected       : {expected}")
        print(f"Recommended    : {recommended}")
        print(f"Top            : {top_recommendation}")
        print(
            f"Acceptance     : "
            f"{'ACCEPTED' if accepted else 'NOT ACCEPTED'}"
        )

    total_tests = len(successful_results)

    acceptance_rate = (
        accepted_count / total_tests
    ) * 100

    print("\n" + "=" * 70)
    print("OVERALL ACCEPTANCE RESULTS")
    print("=" * 70)

    print(f"\nAccepted cases : {accepted_count}")
    print(f"Total cases    : {total_tests}")
    print(
        f"Acceptance Rate: "
        f"{acceptance_rate:.2f}%"
    )

    output = {
        "metric": "controlled_acceptance_proxy",
        "definition": (
            "Accepted when the top-ranked recommendation "
            "is present in the expected recommendation list."
        ),
        "accepted_cases": accepted_count,
        "total_cases": total_tests,
        "acceptance_rate_percent": round(
            acceptance_rate,
            2,
        ),
        "per_test_case": acceptance_results,
    }

    output_path = "ml/evaluation/acceptance_metrics.json"

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
        f"\nAcceptance metrics saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()