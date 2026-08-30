import requests


BASE_URL = "http://127.0.0.1:8000"


def test_file_upload():

    print("\n======================================")
    print(" FILE UPLOAD INTEGRATION TEST")
    print("======================================\n")

    files_to_test = [
        "employee_feedback.txt",
        "employee_feedback.csv"
    ]

    successful_tests = 0

    for filename in files_to_test:

        print("Testing:", filename)
        print("--------------------------------------")

        try:

            with open(filename, "rb") as file:

                response = requests.post(
                    f"{BASE_URL}/analyze-file",
                    files={"file": file},
                    timeout=10
                )

            print("HTTP Status:", response.status_code)

            if response.status_code != 200:
                raise Exception(
                    f"API returned status {response.status_code}"
                )

            data = response.json()

            required_fields = [
                "status",
                "filename",
                "original_text",
                "preprocessed_text",
                "sentiment"
            ]

            for field in required_fields:
                if field not in data:
                    raise Exception(
                        f"Missing response field: {field}"
                    )

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

            print("Filename:", data["filename"])
            print("Preprocessed text:",
                  data["preprocessed_text"])
            print("Sentiment:",
                  data["sentiment"]["sentiment"])
            print("Compound:",
                  data["sentiment"]["compound"])

            print("STATUS: PASS\n")

            successful_tests += 1

        except Exception as error:

            print("STATUS: FAIL")
            print("Error:", error)
            print()

    print("======================================")
    print(" FILE API TEST SUMMARY")
    print("======================================")

    print("Total tests:", len(files_to_test))
    print("Successful tests:", successful_tests)
    print(
        "Failed tests:",
        len(files_to_test) - successful_tests
    )

    if successful_tests == len(files_to_test):
        print("\nRESULT: ALL FILE API TESTS PASSED")
    else:
        print("\nRESULT: SOME FILE API TESTS FAILED")

    print("======================================\n")


if __name__ == "__main__":
    test_file_upload()