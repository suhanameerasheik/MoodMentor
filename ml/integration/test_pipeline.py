from ml.preprocessing import preprocess_text
from ml.sentiment import analyze_sentiment


# Multiple test inputs representing different workplace situations
test_samples = [
    "I am very happy with my team and I love my job.",
    "I am extremely stressed because of my workload.",
    "My workday was normal and nothing unusual happened.",
    "My manager is supportive and I really enjoy working here.",
    "I feel frustrated, tired and overwhelmed by work.",
]


def test_complete_pipeline():

    print("\n======================================")
    print(" MILESTONE 1 INTEGRATION TEST")
    print("======================================\n")

    successful_tests = 0

    for index, text in enumerate(test_samples, start=1):

        print(f"Test {index}")
        print("--------------------------------------")

        try:
            # STEP 1: Original input
            print("1. Original input:")
            print(text)

            # STEP 2: Preprocessing
            processed_text = preprocess_text(text)

            print("\n2. Preprocessed output:")
            print(processed_text)

            # Verify preprocessing produced output
            if not processed_text.strip():
                raise ValueError("Preprocessing returned empty output")

            # STEP 3: Sentiment analysis
            sentiment_result = analyze_sentiment(processed_text)

            print("\n3. Sentiment result:")
            print(sentiment_result)

            # STEP 4: Verify sentiment output
            required_fields = [
                "sentiment",
                "compound",
                "positive",
                "negative",
                "neutral"
            ]

            for field in required_fields:
                if field not in sentiment_result:
                    raise ValueError(
                        f"Missing sentiment field: {field}"
                    )

            # STEP 5: Verify sentiment classification
            if sentiment_result["sentiment"] not in [
                "positive",
                "negative",
                "neutral"
            ]:
                raise ValueError("Invalid sentiment classification")

            print("\n4. Data flow:")
            print("Original text")
            print("      ↓")
            print("Preprocessing")
            print("      ↓")
            print("Processed text")
            print("      ↓")
            print("VADER sentiment analysis")
            print("      ↓")
            print("Sentiment result")

            print("\nSTATUS: PASS\n")

            successful_tests += 1

        except Exception as error:

            print("\nSTATUS: FAIL")
            print("Error:", error)
            print()

    total_tests = len(test_samples)

    print("======================================")
    print(" INTEGRATION TEST SUMMARY")
    print("======================================")

    print("Total tests:", total_tests)
    print("Successful tests:", successful_tests)
    print("Failed tests:", total_tests - successful_tests)

    if successful_tests == total_tests:
        print("\nRESULT: ALL INTEGRATION TESTS PASSED")
    else:
        print("\nRESULT: SOME INTEGRATION TESTS FAILED")

    print("======================================\n")


if __name__ == "__main__":
    test_complete_pipeline()