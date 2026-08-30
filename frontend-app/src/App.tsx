
import { useState } from "react";
import "./App.css";

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<any>(null);
  const [message, setMessage] = useState("");

  async function handleAnalyze() {
    if (text.trim() === "") {
      setMessage("Please enter some workplace feedback.");
      setResult(null);
      return;
    }

    setMessage("");

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.detail || "Analysis failed.");
        setResult(null);
        return;
      }

      setResult(data);
    } catch (error) {
      setMessage("Could not connect to the backend.");
      setResult(null);
    }
  }

  function handleFileUpload(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];

    if (!file) return;

    const allowedTypes = [".txt", ".csv"];
    const fileName = file.name.toLowerCase();

    if (!allowedTypes.some((type) => fileName.endsWith(type))) {
      setMessage("Please upload a .txt or .csv file.");
      setResult(null);
      return;
    }

    const reader = new FileReader();

    reader.onload = (event) => {
      const fileContent = event.target?.result;

      if (typeof fileContent !== "string") {
        setMessage("Could not read the file.");
        return;
      }

      if (fileContent.trim() === "") {
        setMessage("The uploaded file is empty.");
        setResult(null);
        return;
      }

      if (fileName.endsWith(".txt")) {
        setText(fileContent);
        setMessage("✓ TXT file loaded successfully.");
        setResult(null);
        return;
      }

      if (fileName.endsWith(".csv")) {
        const lines = fileContent
          .split(/\r?\n/)
          .map((line) => line.trim())
          .filter((line) => line !== "");

        if (lines.length < 2) {
          setMessage(
            "CSV file must contain a header and at least one row."
          );
          setResult(null);
          return;
        }

        const header = lines[0]
          .split(",")[0]
          .trim()
          .toLowerCase();

        if (header !== "text") {
          setMessage("CSV must contain a 'text' column.");
          setResult(null);
          return;
        }

        const csvTexts = lines
          .slice(1)
          .map((line) => line.split(",")[0].trim())
          .filter((line) => line !== "");

        if (csvTexts.length === 0) {
          setMessage("CSV does not contain valid text.");
          setResult(null);
          return;
        }

        setText(csvTexts.join("\n"));
        setMessage("✓ CSV file loaded successfully.");
        setResult(null);
      }
    };

    reader.onerror = () => {
      setMessage("Error while reading the file.");
      setResult(null);
    };

    reader.readAsText(file);
  }

  return (
    <div className="app">

      {/* Header */}
      <header className="header">
        <div className="brand">
          <div className="brand-icon">🧠</div>

          <div>
            <h1>WellMind AI</h1>
            <p>Employee Wellness Intelligence</p>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          AI System Online
        </div>
      </header>

      {/* Hero */}
      <section className="hero">
        <div>
          <p className="eyebrow">EMPLOYEE WELLNESS PLATFORM</p>

          <h2>
            Understand how your
            <span> workplace feels.</span>
          </h2>

          <p className="hero-text">
            Share employee feedback and let our AI analyze
            workplace sentiment instantly.
          </p>
        </div>

        <div className="hero-icon">
          💬
        </div>
      </section>

      {/* Main Content */}
      <main className="dashboard">

        {/* Input Card */}
        <section className="card input-card">

          <div className="card-header">
            <div>
              <h3>Employee Feedback</h3>
              <p>Enter feedback or upload a file for analysis.</p>
            </div>

            <span className="badge">AI Analysis</span>
          </div>

          <textarea
            placeholder="Example: I really enjoy working with my team, but the workload has been stressful recently..."
            value={text}
            onChange={(event) => setText(event.target.value)}
          />

          <div className="input-footer">

            <label className="upload-button">
              📁 Upload TXT / CSV

              <input
                type="file"
                accept=".txt,.csv"
                onChange={handleFileUpload}
              />
            </label>

            <button
              className="analyze-button"
              onClick={handleAnalyze}
            >
              Analyze Feedback
              <span>→</span>
            </button>

          </div>

          {message && (
            <div className="message">
              {message}
            </div>
          )}

        </section>

        {/* Results */}
        <section className="card results-card">

          <div className="card-header">
            <div>
              <h3>Sentiment Analysis</h3>
              <p>AI-generated workplace sentiment insights.</p>
            </div>

            <span className="live-badge">
              ● LIVE
            </span>
          </div>

          {!result ? (

            <div className="empty-state">

              <div className="empty-icon">
                ✨
              </div>

              <h4>Waiting for feedback</h4>

              <p>
                Enter employee feedback above and click
                <strong> Analyze Feedback</strong>.
              </p>

            </div>

          ) : (

            <div className="results">

              <div className="sentiment-main">

                <div className="sentiment-circle">
                  {result.sentiment.sentiment === "positive"
                    ? "😊"
                    : result.sentiment.sentiment === "negative"
                    ? "😟"
                    : "😐"}
                </div>

                <div>
                  <p className="small-label">
                    DETECTED SENTIMENT
                  </p>

                  <h4 className="sentiment-title">
                    {result.sentiment.sentiment.toUpperCase()}
                  </h4>
                </div>

              </div>

              <div className="score-grid">

                <div className="score positive">
                  <span>Positive</span>
                  <strong>
                    {result.sentiment.positive}
                  </strong>
                </div>

                <div className="score negative">
                  <span>Negative</span>
                  <strong>
                    {result.sentiment.negative}
                  </strong>
                </div>

                <div className="score neutral">
                  <span>Neutral</span>
                  <strong>
                    {result.sentiment.neutral}
                  </strong>
                </div>

                <div className="score compound">
                  <span>Compound</span>
                  <strong>
                    {result.sentiment.compound}
                  </strong>
                </div>

              </div>

              <div className="processed">

                <div className="processed-title">
                  <span>⚙</span>
                  Preprocessed Text
                </div>

                <p>
                  {result.preprocessed_text}
                </p>

              </div>

              <div className="original">

                <div className="processed-title">
                  <span>📝</span>
                  Original Feedback
                </div>

                <p>
                  {result.original_text}
                </p>

              </div>

            </div>

          )}

        </section>

      </main>

      {/* Footer */}
      <footer>
        <span>WellMind AI</span>
        <span>•</span>
        <span>Baseline Sentiment Engine</span>
        <span>•</span>
        <span>Milestone 1</span>
      </footer>

    </div>
  );
}

export default App;