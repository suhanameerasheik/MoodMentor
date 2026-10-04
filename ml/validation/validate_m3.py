import json
import time
from pathlib import Path

from ml.preprocessing import preprocess_text
from ml.sentiment import analyze_sentiment
from ml.emotion import analyze_emotion
from ml.multilabel_emotion import analyze_multilabel_emotion
from ml.emotion_intensity import analyze_emotional_state
from ml.recommendation import generate_hybrid_recommendations


# ============================================================
# M3 VALIDATION TEST CASES
# ============================================================

TEST_CASES = [
    {
        "name": "High Stress",
        "text": "I am extremely stressed and overwhelmed by my workload.",
        "preferences": ["stress", "calm", "focus"]
    },
    {
        "name": "Low Stress",
        "text": "I feel calm and my work is manageable today.",
        "preferences": ["calm", "relaxation"]
    },
    {
        "name": "Work Concentration",
        "text": "I have too much work and cannot concentrate properly.",
        "preferences": ["focus", "productivity"]
    },
    {
        "name": "Positive State",
        "text": "I am happy with my work and proud of what I achieved today.",
        "preferences": ["motivation", "positive"]
    },
    {
        "name": "Mixed Emotion",
        "text": "I am happy about my progress but worried about tomorrow's workload.",
        "preferences": ["calm", "focus"]
    }
]


# ============================================================
# VALIDATE SINGLE TEST CASE
# ============================================================

def validate_case(case):

    start_time = time.perf_counter()

    text = case["text"]
    preferences = case["preferences"]

    # --------------------------------------------------------
    # Preprocessing
    # --------------------------------------------------------

    processed_text = preprocess_text(text)

    # --------------------------------------------------------
    # Sentiment
    # --------------------------------------------------------

    sentiment_result = analyze_sentiment(
        processed_text
    )

    # --------------------------------------------------------
    # Single-label emotion
    # --------------------------------------------------------

    emotion_result = analyze_emotion(
        text
    )

    # --------------------------------------------------------
    # Multi-label emotion
    # --------------------------------------------------------

    multilabel_result = analyze_multilabel_emotion(
        text
    )

    # --------------------------------------------------------
    # Emotional state
    # --------------------------------------------------------

    emotional_state = analyze_emotional_state(
        multilabel_result["emotion_scores"]
    )

    # --------------------------------------------------------
    # Recommendation engine
    # --------------------------------------------------------

    recommendation_result = generate_hybrid_recommendations(
        emotional_state=emotional_state,
        preferences=preferences,
        recommendation_history=[],
        top_k=5,
        text=text
    )

    # --------------------------------------------------------
    # Performance measurement
    # --------------------------------------------------------

    processing_time = (
        time.perf_counter()
        - start_time
    )

    recommendations = (
        recommendation_result.get(
            "recommendations",
            []
        )
    )

    # --------------------------------------------------------
    # Validation checks
    # --------------------------------------------------------

    checks = {
        "preprocessing_success":
            bool(processed_text.strip()),

        "sentiment_success":
            "sentiment" in sentiment_result,

        "emotion_success":
            "emotion" in emotion_result,

        "multilabel_success":
            "emotion_scores" in multilabel_result,

        "emotional_state_success":
            "dominant_emotion" in emotional_state,

        "recommendation_success":
            len(recommendations) > 0,

        "ranking_success":
            all(
                "rank" in recommendation
                for recommendation in recommendations
            ),

        "explainability_success":
            all(
                "explanation" in recommendation
                for recommendation in recommendations
            ),

        "semantic_matching_success":
            all(
                "semantic_score" in recommendation
                for recommendation in recommendations
            )
    }

    passed_checks = sum(
        checks.values()
    )

    total_checks = len(checks)

    return {
        "test_name": case["name"],
        "input_text": text,
        "processed_text": processed_text,

        "sentiment": sentiment_result,

        "emotion": emotion_result,

        "multilabel_emotion":
            multilabel_result,

        "emotional_state":
            emotional_state,

        "recommendation_count":
            len(recommendations),

        "top_recommendation":
            recommendation_result.get(
                "top_recommendation"
            ),

        "recommendations":
            recommendations,

        "checks":
            checks,

        "passed_checks":
            passed_checks,

        "total_checks":
            total_checks,

        "all_checks_passed":
            passed_checks == total_checks,

        "processing_time_seconds":
            round(
                processing_time,
                4
            )
    }


# ============================================================
# PERFORMANCE TEST
# ============================================================

def run_performance_test():

    print("\n======================================")
    print(" PERFORMANCE TEST")
    print("======================================\n")

    times = []

    for case in TEST_CASES:

        start_time = time.perf_counter()

        processed_text = preprocess_text(
            case["text"]
        )

        sentiment_result = analyze_sentiment(
            processed_text
        )

        emotion_result = analyze_emotion(
            case["text"]
        )

        multilabel_result = (
            analyze_multilabel_emotion(
                case["text"]
            )
        )

        emotional_state = (
            analyze_emotional_state(
                multilabel_result[
                    "emotion_scores"
                ]
            )
        )

        generate_hybrid_recommendations(
            emotional_state=emotional_state,
            preferences=case["preferences"],
            recommendation_history=[],
            top_k=5,
            text=case["text"]
        )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        times.append(elapsed)

        print(
            f"{case['name']}: "
            f"{elapsed:.4f} seconds"
        )

    average_time = (
        sum(times) / len(times)
        if times
        else 0
    )

    maximum_time = (
        max(times)
        if times
        else 0
    )

    return {
        "average_processing_time_seconds":
            round(average_time, 4),

        "maximum_processing_time_seconds":
            round(maximum_time, 4),

        "tests_measured":
            len(times)
    }


# ============================================================
# MAIN VALIDATION
# ============================================================

def run_validation():

    print("\n======================================")
    print(" M3-T9 ADVANCED ML VALIDATION")
    print("======================================\n")

    results = []

    for case in TEST_CASES:

        print(
            f"Running test: {case['name']}"
        )

        try:

            result = validate_case(
                case
            )

            results.append(
                result
            )

            print(
                f"Checks passed: "
                f"{result['passed_checks']}/"
                f"{result['total_checks']}"
            )

            print(
                "Processing time:",
                result[
                    "processing_time_seconds"
                ],
                "seconds"
            )

            print(
                "Status:",
                "PASS"
                if result["all_checks_passed"]
                else "FAIL"
            )

            print()

        except Exception as error:

            results.append(
                {
                    "test_name":
                        case["name"],

                    "status":
                        "ERROR",

                    "error":
                        str(error)
                }
            )

            print(
                "Status: ERROR"
            )

            print(
                "Error:",
                error
            )

            print()

    # --------------------------------------------------------
    # Performance
    # --------------------------------------------------------

    performance = run_performance_test()

    # --------------------------------------------------------
    # Overall statistics
    # --------------------------------------------------------

    successful_tests = [
        result
        for result in results
        if result.get(
            "all_checks_passed",
            False
        )
    ]

    total_tests = len(
        TEST_CASES
    )

    passed_tests = len(
        successful_tests
    )

    validation_rate = (
        passed_tests / total_tests
        if total_tests > 0
        else 0
    )

    report = {
        "report_name":
            "M3 Advanced ML Validation Report",

        "milestone":
            "M3-T9",

        "total_tests":
            total_tests,

        "passed_tests":
            passed_tests,

        "failed_tests":
            total_tests - passed_tests,

        "validation_rate":
            round(
                validation_rate,
                4
            ),

        "performance":
            performance,

        "results":
            results
    }

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    report_path = (
        Path(__file__).resolve().parent
        / "m3_validation_report.json"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n======================================")
    print(" M3-T9 VALIDATION SUMMARY")
    print("======================================")

    print(
        "Total tests:",
        total_tests
    )

    print(
        "Passed tests:",
        passed_tests
    )

    print(
        "Failed tests:",
        total_tests - passed_tests
    )

    print(
        "Validation rate:",
        round(
            validation_rate * 100,
            2
        ),
        "%"
    )

    print(
        "Average processing time:",
        performance[
            "average_processing_time_seconds"
        ],
        "seconds"
    )

    print(
        "Maximum processing time:",
        performance[
            "maximum_processing_time_seconds"
        ],
        "seconds"
    )

    print("\nReport saved to:")
    print(report_path)

    print("======================================")


if __name__ == "__main__":
    run_validation()