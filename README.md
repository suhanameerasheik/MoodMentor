# MoodMentor

MoodMentor is a reusable emotion-analysis package with a command-line interface.

## Installation

Install the package without the optional machine-learning dependencies:

    python -m pip install .

Install the package with emotion-analysis support:

    python -m pip install ".[analysis]"

## CLI usage

Show help:

    moodmentor --help

Show version:

    moodmentor --version

Analyze text:

    moodmentor analyze "I feel happy and excited today."

The first analysis may download the pretrained emotion model from Hugging Face.
