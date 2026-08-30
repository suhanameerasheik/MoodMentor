import requests


BASE_URL = "http://127.0.0.1:8000"


def test_analyze_endpoint():

    print("\n======================================")
    print(" API INTEGRATION TEST")
    print("======================================\n")

    test_inputs = [
        "I am very happy with my team.",
        "I feel extremely stressed about my workload.",
        "My workday was normal today.",
    ]

    successful_tests = 0

    for index, text in enumerate(test_inputs, start=1):

        print(f"Test {index}")
        print("--------------------------------------")
        print("Input:", text)

        try:

            response = requests.post(
                f"{BASE_URL}/analyze",
                json={"text": text},
                timeout=10
            )

            print("HTTP Status:", response.status_code)

            if response.status_code != 200:
                raise Exception(
                    f"API returned status {response.status_code}"
                )

            data = response.json()

            # Verify main response fields
            required_fields = [
                "status",
                "original_text",
                "preprocessed_text",
                "sentiment"
            ]

            for field in required_fields:
                if field not in data:
                    raise Exception(
                        f"Missing response field: {field}"
                    )

            # Verify sentiment fields
            sentiment_fields = [
                "sentiment",
                "compound",
                "positive",
                "negative",
                "neutral"
            ]

            for field in sentiment_fields:
                if field not in data["sentiment"]:
                    raise Exception(
                        f"Missing sentiment field: {field}"
                    )

            print("Predicted sentiment:",
                  data["sentiment"]["sentiment"])

            print("Compound score:",
                  data["sentiment"]["compound"])

            print("Preprocessed text:",
                  data["preprocessed_text"])

            print("STATUS: PASS\n")

            successful_tests += 1

        except Exception as error:

            print("STATUS: FAIL")
            print("Error:", error)
            print()

    print("======================================")
    print(" API TEST SUMMARY")
    print("======================================")

    print("Total tests:", len(test_inputs))
    print("Successful tests:", successful_tests)
    print("Failed tests:",
          len(test_inputs) - successful_tests)

    if successful_tests == len(test_inputs):
        print("\nRESULT: ALL API TESTS PASSED")
    else:
        print("\nRESULT: SOME API TESTS FAILED")

    print("======================================\n")


if __name__ == "__main__":
    test_analyze_endpoint()