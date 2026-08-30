import json
from pathlib import Path

from ml.preprocessing import preprocess_text
from ml.sentiment import analyze_sentiment


# Sample corpus for Milestone 1 validation
samples = [
    {
        "text": "I love my job and I am very happy with my team.",
        "expected": "positive"
    },
    {
        "text": "I am extremely stressed and unhappy with my workload.",
        "expected": "negative"
    },
    {
        "text": "My workday was normal and nothing unusual happened.",
        "expected": "neutral"
    },
    {
        "text": "I really enjoy working with my manager.",
        "expected": "positive"
    },
    {
        "text": "I feel tired, frustrated and overwhelmed by work.",
        "expected": "negative"
    },
]


def validate_sentiment():

    results = []
    correct_predictions = 0

    print("\n======================================")
    print(" MILESTONE 1 SENTIMENT VALIDATION")
    print("======================================\n")

    for index, sample in enumerate(samples, start=1):

        original_text = sample["text"]
        expected = sample["expected"]

        # Preprocess input
        processed_text = preprocess_text(original_text)

        # Analyze sentiment
        sentiment_result = analyze_sentiment(processed_text)

        predicted = sentiment_result["sentiment"]

        # Compare expected and predicted sentiment
        is_correct = predicted == expected

        if is_correct:
            correct_predictions += 1

        result = {
            "sample_number": index,
            "input_text": original_text,
            "processed_text": processed_text,
            "expected_sentiment": expected,
            "predicted_sentiment": predicted,
            "compound": sentiment_result["compound"],
            "positive": sentiment_result["positive"],
            "negative": sentiment_result["negative"],
            "neutral": sentiment_result["neutral"],
            "correct": is_correct
        }

        results.append(result)

        print(f"Sample {index}")
        print("------------------------------")
        print("Input:", original_text)
        print("Processed:", processed_text)
        print("Expected:", expected)
        print("Predicted:", predicted)
        print("Compound:", sentiment_result["compound"])
        print("Positive:", sentiment_result["positive"])
        print("Negative:", sentiment_result["negative"])
        print("Neutral:", sentiment_result["neutral"])
        print("Correct:", is_correct)
        print()

    total_samples = len(samples)
    incorrect_predictions = total_samples - correct_predictions

    accuracy = correct_predictions / total_samples if total_samples > 0 else 0

    # Create final validation report
    report = {
        "report_name": "Milestone 1 Sentiment Validation Report",
        "total_samples": total_samples,
        "correct_predictions": correct_predictions,
        "incorrect_predictions": incorrect_predictions,
        "accuracy": round(accuracy, 4),
        "results": results
    }

    # Save report in the validation folder
    report_path = Path(__file__).resolve().parent / "sentiment_validation_report.json"

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("======================================")
    print(" VALIDATION SUMMARY")
    print("======================================")
    print("Total samples:", total_samples)
    print("Correct predictions:", correct_predictions)
    print("Incorrect predictions:", incorrect_predictions)
    print("Validation accuracy:", round(accuracy, 4))
    print("======================================")

    print("\nValidation report saved to:")
    print(report_path)


if __name__ == "__main__":
    validate_sentiment()