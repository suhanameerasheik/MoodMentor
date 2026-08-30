import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# 1. Load the dataset
data = pd.read_csv("data/sentiment.csv")

# 2. Separate text and labels
X = data["text"]
y = data["label"]

# 3. Split the dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 4. Convert text into numerical features
vectorizer = TfidfVectorizer()

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# 5. Create the ML model
model = LogisticRegression(max_iter=1000)

# 6. Train the model
model.fit(X_train_tfidf, y_train)

# 7. Make predictions
predictions = model.predict(X_test_tfidf)

# 8. Evaluate the model
accuracy = accuracy_score(y_test, predictions)

print("Model Accuracy:", accuracy)
print("\nClassification Report:")
print(classification_report(y_test, predictions))