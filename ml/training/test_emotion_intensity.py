import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from ml.emotion_intensity import analyze_emotional_state


tests = {

    "fear": {
        "fear": 0.91,
        "sadness": 0.42,
        "joy": 0.05,
        "anger": 0.12
    },

    "joy": {
        "joy": 0.95,
        "love": 0.31,
        "fear": 0.04
    },

    "mixed": {
        "joy": 0.72,
        "fear": 0.61,
        "sadness": 0.35
    }
}


for name, scores in tests.items():

    print("\nTEST:", name)

    result = analyze_emotional_state(scores)

    print(result)