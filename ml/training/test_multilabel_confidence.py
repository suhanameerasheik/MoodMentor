import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from ml.multilabel_emotion import analyze_multilabel_emotion


test_cases = [
    "I am extremely happy and excited about my promotion.",
    "I feel very sad and lonely because my team ignores me.",
    "I am extremely angry about the unfair treatment at work.",
    "I am scared and worried about losing my job.",
    "I am shocked and surprised by the sudden promotion.",
    "I am disgusted by the unfair and horrible treatment.",
    "I am happy about the promotion but afraid of the new responsibilities."
]


print("======================================")
print("MULTI-LABEL CONFIDENCE TEST")
print("======================================")


for number, text in enumerate(test_cases, start=1):

    print(f"\nTest {number}")
    print("Input:", text)

    result = analyze_multilabel_emotion(text)

    print("Detected emotions:")
    print(result["detected_emotions"])

    print("Primary emotion:")
    print(result["primary_emotion"])

    print("Emotion scores:")

    for emotion, score in result["emotion_scores"].items():
        print(f"  {emotion}: {score}")