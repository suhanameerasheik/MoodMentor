"""Command-line interface for MoodMentor."""

import argparse
import json
import sys

from moodmentor import __version__


def analyze_text(text: str) -> dict:
    """Analyze the emotion expressed in text."""
    try:
        # Import only when analysis is requested.
        from ml.emotion import analyze_emotion
    except ImportError as exc:
        raise RuntimeError(
            'Analysis dependencies are missing. Install them with: '
            'python -m pip install "moodmentor[analysis]"'
        ) from exc

    return analyze_emotion(text)


def main() -> None:
    """Run the MoodMentor CLI."""
    parser = argparse.ArgumentParser(
        prog="moodmentor",
        description="Analyze emotions in text using MoodMentor.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    commands = parser.add_subparsers(dest="command", required=True)

    analyze_parser = commands.add_parser(
        "analyze",
        help="Analyze the emotion expressed in text.",
    )
    analyze_parser.add_argument(
        "text",
        help="Text to analyze, enclosed in quotation marks.",
    )

    args = parser.parse_args()

    if args.command == "analyze":
        if not args.text.strip():
            parser.error("Text cannot be empty.")

        try:
            result = analyze_text(args.text)
        except RuntimeError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc

        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
