import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


# Load English stop words
STOP_WORDS = set(stopwords.words("english"))

# Keep important negation words
NEGATION_WORDS = {"no", "not", "never"}

STOP_WORDS = STOP_WORDS - NEGATION_WORDS

# Create lemmatizer
lemmatizer = WordNetLemmatizer()


def preprocess_text(text: str) -> str:
    """
    Preprocess employee feedback.
    """

    # 1. Check for empty input
    if not text or not text.strip():
        return ""

    # 2. Convert text to lowercase
    text = text.lower()

    # 3. Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # 4. Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    # 5. Normalize repeated spaces
    text = " ".join(text.split())

    # 6. Tokenization
    tokens = word_tokenize(text)

    # 7. Remove stop words
    tokens = [
        token
        for token in tokens
        if token not in STOP_WORDS
    ]

    # 8. Lemmatization
    tokens = [
        lemmatizer.lemmatize(token)
        for token in tokens
    ]

    # 9. Create processed text
    processed_text = " ".join(tokens)

    return processed_text