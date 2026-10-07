"""
Task 9.7 - Response Time Evaluation

Evaluates recommendation API response times
using the controlled Task 9 test results.

Reports:
- Average response time
- Minimum response time
- Maximum response time
- Cold-start response time
- Warm response average
- P95 response time
"""

import json
import math


RESULTS_PATH = "ml/evaluation/advanced_results.json"


def percentile(values, percentile_value):
    """
    Calculate percentile using linear interpolation.
    """

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
        + (upper_value - lower_value) * fraction
    )


def main():

    print("=" * 70)
    print("TASK 9.7 - RESPONSE TIME EVALUATION")
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
        and result.get("response_time") is not None
    ]

    if not successful_results:
        print("\nNo response-time data found.")
        return

    response_times = [
        float(result["response_time"])
        for result in successful_results
    ]

    # First request is treated as the cold-start request.
    cold_start = response_times[0]

    warm_times = response_times[1:]

    average_time = (
        sum(response_times)
        / len(response_times)
    )

    minimum_time = min(response_times)
    maximum_time = max(response_times)

    warm_average = (
        sum(warm_times) / len(warm_times)
        if warm_times
        else 0.0
    )

    p95_time = percentile(
        response_times,
        0.95,
    )

    print(
        f"\nEvaluating "
        f"{len(successful_results)} test cases\n"
    )

    print("-" * 70)

    for result in successful_results:

        print(
            f"{result['test_id']}: "
            f"{result['response_time']:.4f} seconds"
        )

    print("\n" + "=" * 70)
    print("OVERALL RESPONSE TIME RESULTS")
    print("=" * 70)

    print(
        f"\nAverage response time : "
        f"{average_time:.4f} seconds"
    )

    print(
        f"Minimum response time : "
        f"{minimum_time:.4f} seconds"
    )

    print(
        f"Maximum response time : "
        f"{maximum_time:.4f} seconds"
    )

    print(
        f"Cold-start response   : "
        f"{cold_start:.4f} seconds"
    )

    print(
        f"Warm average response : "
        f"{warm_average:.4f} seconds"
    )

    print(
        f"P95 response time     : "
        f"{p95_time:.4f} seconds"
    )

    output = {
        "metric": "recommendation_response_time",
        "test_cases": len(successful_results),
        "average_seconds": round(
            average_time,
            4,
        ),
        "minimum_seconds": round(
            minimum_time,
            4,
        ),
        "maximum_seconds": round(
            maximum_time,
            4,
        ),
        "cold_start_seconds": round(
            cold_start,
            4,
        ),
        "warm_average_seconds": round(
            warm_average,
            4,
        ),
        "p95_seconds": round(
            p95_time,
            4,
        ),
        "per_test_case": [
            {
                "test_id": result["test_id"],
                "response_time_seconds": round(
                    float(result["response_time"]),
                    4,
                ),
            }
            for result in successful_results
        ],
    }

    output_path = (
        "ml/evaluation/response_time_metrics.json"
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
        f"\nResponse time metrics saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()