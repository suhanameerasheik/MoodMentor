from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Create VADER analyzer
analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment using VADER.

    Returns:
        compound score
        positive score
        negative score
        neutral score
        sentiment label
    """

    # Get VADER sentiment scores
    scores = analyzer.polarity_scores(text)

    # Get compound score
    compound = scores["compound"]

    # Determine sentiment dynamically
    if compound >= 0.05:
        sentiment = "positive"
    elif compound <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "compound": compound,
        "positive": scores["pos"],
        "negative": scores["neg"],
        "neutral": scores["neu"]
    }