import { useEffect, useState } from "react";
import "./App.css";

type AnalysisResult = {
  sentiment?: {
    sentiment?: string;
    positive?: number;
    negative?: number;
    neutral?: number;
    compound?: number;
  };

  emotion?: {
    emotion?: string;
    confidence?: number;
  };

  multilabel_emotion?: {
    primary_emotion?: string;
    detected_emotions?: string[];
    emotion_scores?: {
      joy?: number;
      sadness?: number;
      anger?: number;
      fear?: number;
      surprise?: number;
      disgust?: number;
    };
  };

  emotional_state?: {
    dominant_emotion?: string;
    primary_emotion?: string;
    intensity?: number;
    emotional_intensity?: number;
    polarity?: string;
    severity?: string;
    mixed_emotion?: boolean;
    mixed_emotional_state?: boolean;
    detected_emotions?: string[];
    emotion_scores?: {
      joy?: number;
      sadness?: number;
      anger?: number;
      fear?: number;
      surprise?: number;
      disgust?: number;
    };
  };

  wellness?: {
    risk_level?: string;
    insight?: string;
  };

  original_text?: string;
  preprocessed_text?: string;
};

type Recommendation = {
  id?: string;
  title?: string;
  type?: string;
  description?: string;
  tags?: string[];

  rule_score?: number;
  content_score?: number;
  preference_score?: number;
  collaborative_score?: number;
  emotion_similarity_score?: number;
  historical_behavior_score?: number;
  personalization_score?: number;
  semantic_score?: number;

  base_score?: number;
  score?: number;
  feedback_score?: number;
  learned_score?: number;

  rank?: number;
  ranking_reason?: string | string[];

  explanation?: {
    summary?: string;
    reasons?: string[];
    factors?: string[] | Record<string, number>;
  };
};

type HybridWeights = {
  rule_based?: number;
  content_based?: number;
  preference_matching?: number;
  collaborative_filtering?: number;
  emotion_similarity?: number;
  historical_behavior?: number;
  semantic_similarity?: number;
};

type RecommendationResult = {
  recommendations?: Recommendation[];
  top_recommendation?: Recommendation | null;
  ranking_order?: string[];
  method?: string;
  components?: string[];

  hybrid_weights?: HybridWeights;
  user_id?: string;
  collaborative_users_available?: number;

  count?: number;
  duplicate_filtered?: number;
  low_relevance_filtered?: number;

  personalization?: {
    collaborative_history_used?: boolean;
  };
};

type PreviousInteraction = {
  id?: number;
  text?: string;
  preferences?: string[];
  emotional_state?: Record<string, unknown>;
  recommendations?: Recommendation[];
  top_recommendation?: Recommendation | null;
  created_at?: string;
};

function App() {
  const [text, setText] = useState("");

  const [result, setResult] =
    useState<AnalysisResult | null>(null);

  const [message, setMessage] = useState("");

  // ==========================================================
  // USER PROFILE
  // ==========================================================

  const [selectedUser, setSelectedUser] =
    useState("user_001");

  // ==========================================================
  // PERSONALIZED RECOMMENDATION STATE
  // ==========================================================

  const [selectedPreferences, setSelectedPreferences] =
    useState<string[]>([]);

  const [recommendations, setRecommendations] =
    useState<RecommendationResult | null>(null);

  const [recommendationHistory, setRecommendationHistory] =
    useState<string[]>([]);

  const [recommendationHistoryData, setRecommendationHistoryData] =
    useState<Recommendation[]>([]);

  const [recommendationLoading, setRecommendationLoading] =
    useState(false);

  // ==========================================================
  // HISTORY PANEL STATE
  // ==========================================================

  const [showPreviousInteractions, setShowPreviousInteractions] =
    useState(false);

  const [showRecommendationHistory, setShowRecommendationHistory] =
    useState(false);

  // ==========================================================
  // BACKEND PREVIOUS INTERACTIONS
  // ==========================================================

  const [previousInteractions, setPreviousInteractions] =
    useState<PreviousInteraction[]>([]);

  const [previousInteractionsLoading, setPreviousInteractionsLoading] =
    useState(false);

  const [previousInteractionCount, setPreviousInteractionCount] =
    useState(0);

  const [recommendationHistoryCount, setRecommendationHistoryCount] =
    useState(0);

  const preferenceOptions = [
    "Breathing",
    "Exercise",
    "Meditation",
    "Music",
    "Mindfulness",
    "Walking",
    "Relaxation",
  ];

  // ==========================================================
  // LOAD BACKEND INTERACTION COUNT
  // ==========================================================

  async function loadPreviousInteractionCount() {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/previous-interactions?limit=100"
      );

      const data = await response.json();

      if (!response.ok) {
        return;
      }

      const count =
        typeof data.count === "number"
          ? data.count
          : Array.isArray(data.interactions)
          ? data.interactions.length
          : 0;

      setPreviousInteractionCount(count);
    } catch (error) {
      console.error(
        "Could not load interaction count:",
        error
      );
    }
  }

  useEffect(() => {
    loadPreviousInteractionCount();
  }, []);

  useEffect(() => {
    setRecommendationHistoryCount(
      recommendationHistory.length
    );
  }, [recommendationHistory]);

  // ==========================================================
  // ANALYZE TEXT
  // ==========================================================

  async function handleAnalyze() {
    if (text.trim() === "") {
      setMessage(
        "Please enter some workplace feedback."
      );

      setResult(null);
      setRecommendations(null);

      return;
    }

    setMessage("");
    setRecommendations(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/analyze",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            text: text,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setMessage(
          data.detail ||
            "Analysis failed."
        );

        setResult(null);

        return;
      }

      setResult(data);

      setMessage(
        "✓ Analysis completed successfully."
      );
    } catch (error) {
      console.error(error);

      setMessage(
        "Could not connect to the backend. Make sure FastAPI is running."
      );

      setResult(null);
    }
  }

  // ==========================================================
  // LOAD PREVIOUS INTERACTIONS
  // ==========================================================

  async function handlePreviousInteractions() {
    setShowRecommendationHistory(false);

    if (showPreviousInteractions) {
      setShowPreviousInteractions(false);
      return;
    }

    setPreviousInteractionsLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/previous-interactions?limit=100"
      );

      const data = await response.json();

      if (!response.ok) {
        setMessage(
          data.detail ||
            "Could not load previous interactions."
        );

        return;
      }

      const interactions =
        Array.isArray(data.interactions)
          ? data.interactions
          : [];

      setPreviousInteractions(
        interactions
      );

      const count =
        typeof data.count === "number"
          ? data.count
          : interactions.length;

      setPreviousInteractionCount(
        count
      );

      setShowPreviousInteractions(
        true
      );
    } catch (error) {
      console.error(
        "Previous interactions error:",
        error
      );

      setMessage(
        "Could not connect to the previous interactions service."
      );
    } finally {
      setPreviousInteractionsLoading(
        false
      );
    }
  }

  // ==========================================================
  // SHOW RECOMMENDATION HISTORY
  // ==========================================================

  function handleRecommendationHistory() {
    setShowPreviousInteractions(false);

    setShowRecommendationHistory(
      (previous) => !previous
    );
  }

  // ==========================================================
  // PERSONALIZED RECOMMENDATIONS
  // ==========================================================

  async function handleRecommendations() {
    if (!text.trim()) {
      setMessage(
        "Please enter and analyze workplace feedback first."
      );

      return;
    }

    setRecommendationLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/recommend",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            text: text,
            preferences:
              selectedPreferences,
            recommendation_history:
              recommendationHistory,
            top_k: 5,
            user_id: selectedUser,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setMessage(
          data.detail ||
            "Could not generate recommendations."
        );

        setRecommendations(null);

        return;
      }

      setRecommendations(
        data.recommendations
      );

      const returnedRecommendations =
        data.recommendations
          ?.recommendations || [];

      if (
        returnedRecommendations.length > 0
      ) {
        setRecommendationHistoryData(
          (previous) => {
            const combined = [
              ...previous,
              ...returnedRecommendations,
            ];

            const unique = new Map<
              string,
              Recommendation
            >();

            combined.forEach(
              (item, index) => {
                const key =
                  item.id ||
                  `${item.title || "recommendation"}-${index}`;

                unique.set(
                  key,
                  item
                );
              }
            );

            return Array.from(
              unique.values()
            ).slice(-20);
          }
        );
      }

      const returnedIds =
        returnedRecommendations
          .map(
            (
              item: Recommendation
            ) => item.id
          )
          .filter(
            (
              id: string | undefined
            ): id is string =>
              Boolean(id)
          );

      if (
        returnedIds.length > 0
      ) {
        setRecommendationHistory(
          (previous) => {
            const combined = [
              ...previous,
              ...returnedIds,
            ];

            return Array.from(
              new Set(combined)
            ).slice(-20);
          }
        );
      }

      await loadPreviousInteractionCount();

      setMessage(
        "✓ Personalized recommendations generated successfully."
      );
    } catch (error) {
      console.error(error);

      setMessage(
        "Could not connect to the recommendation service."
      );

      setRecommendations(null);
    } finally {
      setRecommendationLoading(
        false
      );
    }
  }

  // ==========================================================
  // PREFERENCE SELECTION
  // ==========================================================

  function togglePreference(
    preference: string
  ) {
    setSelectedPreferences(
      (previous) => {
        if (
          previous.includes(
            preference
          )
        ) {
          return previous.filter(
            (item) =>
              item !== preference
          );
        }

        return [
          ...previous,
          preference,
        ];
      }
    );
  }

  // ==========================================================
  // FILE UPLOAD
  // ==========================================================

  function handleFileUpload(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file =
      event.target.files?.[0];

    if (!file) return;

    const allowedTypes = [
      ".txt",
      ".csv",
    ];

    const fileName =
      file.name.toLowerCase();

    if (
      !allowedTypes.some(
        (type) =>
          fileName.endsWith(type)
      )
    ) {
      setMessage(
        "Please upload a .txt or .csv file."
      );

      setResult(null);

      return;
    }

    const reader =
      new FileReader();

    reader.onload = (
      event
    ) => {
      const fileContent =
        event.target?.result;

      if (
        typeof fileContent !==
        "string"
      ) {
        setMessage(
          "Could not read the file."
        );

        setResult(null);

        return;
      }

      if (
        fileContent.trim() === ""
      ) {
        setMessage(
          "The uploaded file is empty."
        );

        setResult(null);

        return;
      }

      if (
        fileName.endsWith(".txt")
      ) {
        setText(
          fileContent
        );

        setMessage(
          "✓ TXT file loaded successfully."
        );

        setResult(null);
        setRecommendations(null);

        return;
      }

      if (
        fileName.endsWith(".csv")
      ) {
        const lines =
          fileContent
            .split(/\r?\n/)
            .map(
              (line) =>
                line.trim()
            )
            .filter(
              (line) =>
                line !== ""
            );

        if (
          lines.length < 2
        ) {
          setMessage(
            "CSV file must contain a header and at least one row."
          );

          setResult(null);

          return;
        }

        const header =
          lines[0]
            .split(",")[0]
            .trim()
            .toLowerCase();

        if (
          header !== "feedback"
        ) {
          setMessage(
            "CSV must contain a 'feedback' column."
          );

          setResult(null);

          return;
        }

        const csvTexts =
          lines
            .slice(1)
            .map(
              (line) =>
                line
                  .split(",")[0]
                  .trim()
            )
            .filter(
              (line) =>
                line !== ""
            );

        if (
          csvTexts.length === 0
        ) {
          setMessage(
            "CSV does not contain valid text."
          );

          setResult(null);

          return;
        }

        setText(
          csvTexts.join("\n")
        );

        setMessage(
          "✓ CSV file loaded successfully."
        );

        setResult(null);
        setRecommendations(null);
      }
    };

    reader.onerror = () => {
      setMessage(
        "Error while reading the file."
      );

      setResult(null);
    };

    reader.readAsText(file);
  }

  // ==========================================================
  // HELPER FUNCTIONS
  // ==========================================================

  function percentage(
    value?: number
  ) {
    if (
      value === undefined ||
      value === null
    ) {
      return "0.00%";
    }

    return `${(
      value * 100
    ).toFixed(2)}%`;
  }

  function number(
    value?: number
  ) {
    if (
      value === undefined ||
      value === null
    ) {
      return "0.0000";
    }

    return value.toFixed(4);
  }

  function displayValue(
    value?: string | boolean
  ) {
    if (
      value === undefined ||
      value === null
    ) {
      return "Not available";
    }

    if (
      typeof value === "boolean"
    ) {
      return value
        ? "Yes"
        : "No";
    }

    return value;
  }

  function recommendationType(
    type?: string
  ) {
    if (!type) {
      return "Wellness Activity";
    }

    return type
      .replace(
        /_/g,
        " "
      )
      .replace(
        /\b\w/g,
        (letter) =>
          letter.toUpperCase()
      );
  }

  // ==========================================================
  // HYBRID SCORE LABELS
  // ==========================================================

  const hybridScoreItems = [
    {
      label: "Rule-based",
      key: "rule_score" as const,
    },
    {
      label: "Content-based",
      key: "content_score" as const,
    },
    {
      label: "Preference matching",
      key: "preference_score" as const,
    },
    {
      label: "Collaborative filtering",
      key: "collaborative_score" as const,
    },
    {
      label: "Emotion similarity",
      key: "emotion_similarity_score" as const,
    },
    {
      label: "Historical behavior",
      key: "historical_behavior_score" as const,
    },
    {
      label: "Semantic similarity",
      key: "semantic_score" as const,
    },
  ];

  // ==========================================================
  // UI
  // ==========================================================

  return (
    <div className="app">

      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            🧠
          </div>

          <div>

            <h1>

              <p className="eyebrow">
                EMPLOYEE WELLNESS PLATFORM
              </p>

            </h1>

          </div>

        </div>

      </header>

      <section className="hero">

        <div>

          <h2>

            Understand how your

            <span>
              workplace feels.
            </span>

          </h2>

          <p className="hero-text">

            Share employee feedback and let
            our AI analyze workplace sentiment,
            emotions, and wellness risk
            instantly.

          </p>

        </div>

        <div className="hero-icon">
          💬
        </div>

      </section>

      <main className="dashboard">

        <section className="card input-card">

          <div className="card-header">

            <div>

              <h3>
                Employee Feedback
              </h3>

              <p>
                Enter feedback or upload a
                file for analysis.
              </p>

            </div>

            <span className="badge">
              AI Analysis
            </span>

          </div>

          <textarea
            placeholder="Example: I really enjoy working with my team, but the workload has been stressful recently..."
            value={text}
            onChange={(event) =>
              setText(
                event.target.value
              )
            }
          />

          <div className="input-footer">

            <label className="upload-button">

              📁 Upload TXT / CSV

              <input
                type="file"
                accept=".txt,.csv"
                onChange={
                  handleFileUpload
                }
              />

            </label>

            <button
              className="analyze-button"
              onClick={
                handleAnalyze
              }
            >

              Analyze Feedback

              <span>
                →
              </span>

            </button>

          </div>

          {message && (

            <div className="message">
              {message}
            </div>

          )}

        </section>

        <section className="card results-card">

          <div className="card-header">

            <div>

              <h3>
                AI Analysis Results
              </h3>

              <p>
                Sentiment, emotion, and
                wellness insights from
                feedback.
              </p>

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

              <h4>
                Waiting for feedback
              </h4>

              <p>

                Enter employee feedback
                above and click{" "}

                <strong>
                  Analyze Feedback
                </strong>.

              </p>

            </div>

          ) : (

            <div className="results">

              <div className="sentiment-main">

                <div className="sentiment-circle">

                  {result.sentiment?.sentiment ===
                  "positive"
                    ? "😊"
                    : result.sentiment?.sentiment ===
                      "negative"
                    ? "😟"
                    : "😐"}

                </div>

                <div>

                  <p className="small-label">
                    DETECTED SENTIMENT
                  </p>

                  <h4 className="sentiment-title">

                    {(
                      result.sentiment?.sentiment ||
                      "unknown"
                    ).toUpperCase()}

                  </h4>

                </div>

              </div>

              <div className="score-grid">

                <div className="score positive">

                  <span>
                    Positive
                  </span>

                  <strong>
                    {number(
                      result.sentiment?.positive
                    )}
                  </strong>

                </div>

                <div className="score negative">

                  <span>
                    Negative
                  </span>

                  <strong>
                    {number(
                      result.sentiment?.negative
                    )}
                  </strong>

                </div>

                <div className="score neutral">

                  <span>
                    Neutral
                  </span>

                  <strong>
                    {number(
                      result.sentiment?.neutral
                    )}
                  </strong>

                </div>

                <div className="score compound">

                  <span>
                    Compound
                  </span>

                  <strong>
                    {number(
                      result.sentiment?.compound
                    )}
                  </strong>

                </div>

              </div>

              <div className="emotion-result">

                <div className="emotion-icon">
                  🧠
                </div>

                <div className="emotion-info">

                  <p className="small-label">
                    DETECTED EMOTION
                  </p>

                  <h4 className="emotion-title">

                    {(
                      result.emotion?.emotion ||
                      "unknown"
                    ).toUpperCase()}

                  </h4>

                  <p className="emotion-confidence">

                    Confidence:{" "}

                    {percentage(
                      result.emotion?.confidence
                    )}

                  </p>

                </div>

              </div>

              {result.multilabel_emotion && (

                <>

                  <div className="emotion-result">

                    <div className="emotion-icon">
                      🎭
                    </div>

                    <div className="emotion-info">

                      <p className="small-label">
                        MULTI-LABEL EMOTIONS
                      </p>

                      <h4 className="emotion-title">

                        {(
                          result
                            .multilabel_emotion
                            .primary_emotion ||
                          "unknown"
                        ).toUpperCase()}

                      </h4>

                      <p className="emotion-confidence">

                        Detected:{" "}

                        {result
                          .multilabel_emotion
                          .detected_emotions
                          ?.join(", ") ||
                          "No emotion above threshold"}

                      </p>

                    </div>

                  </div>

                  <div className="score-grid">

                    <div className="score">

                      <span>
                        Joy
                      </span>

                      <strong>
                        {percentage(
                          result
                            .multilabel_emotion
                            .emotion_scores
                            ?.joy
                        )}
                      </strong>

                    </div>

                    <div className="score">

                      <span>
                        Sadness
                      </span>

                      <strong>
                        {percentage(
                          result
                            .multilabel_emotion
                            .emotion_scores
                            ?.sadness
                        )}
                      </strong>

                    </div>

                    <div className="score">

                      <span>
                        Anger
                      </span>

                      <strong>
                        {percentage(
                          result
                            .multilabel_emotion
                            .emotion_scores
                            ?.anger
                        )}
                      </strong>

                    </div>

                    <div className="score">

                      <span>
                        Fear
                      </span>

                      <strong>
                        {percentage(
                          result
                            .multilabel_emotion
                            .emotion_scores
                            ?.fear
                        )}
                      </strong>

                    </div>

                    <div className="score">

                      <span>
                        Surprise
                      </span>

                      <strong>
                        {percentage(
                          result
                            .multilabel_emotion
                            .emotion_scores
                            ?.surprise
                        )}
                      </strong>

                    </div>

                    <div className="score">

                      <span>
                        Disgust
                      </span>

                      <strong>
                        {percentage(
                          result
                            .multilabel_emotion
                            .emotion_scores
                            ?.disgust
                        )}
                      </strong>

                    </div>

                  </div>

                </>

              )}

              {result.emotional_state && (

                <section className="emotional-state-card">

                  <div className="emotional-state-header">

                    <div>

                      <p className="small-label">
                        EMOTIONAL STATE
                      </p>

                      <h4>
                        Emotional State Analysis
                      </h4>

                      <p>
                        Combined emotion probabilities,
                        intensity, polarity, and
                        severity.
                      </p>

                    </div>

                    <div className="state-icon">
                      💭
                    </div>

                  </div>

                  <div className="state-summary">

                    <div className="state-primary">

                      <span>
                        Dominant Emotion
                      </span>

                      <strong>

                        {(
                          result.emotional_state
                            .dominant_emotion ||
                          result.emotional_state
                            .primary_emotion ||
                          result.multilabel_emotion
                            ?.primary_emotion ||
                          "Unknown"
                        ).toUpperCase()}

                      </strong>

                    </div>

                    <div className="state-primary">

                      <span>
                        Emotional Intensity
                      </span>

                      <strong>

                        {percentage(
                          result.emotional_state
                            .intensity ??
                          result.emotional_state
                            .emotional_intensity
                        )}

                      </strong>

                    </div>

                  </div>

                  <div className="state-detail-grid">

                    <div className="state-detail">

                      <span>
                        Polarity
                      </span>

                      <strong
                        className={`polarity ${
                          result.emotional_state
                            .polarity || ""
                        }`}
                      >

                        {(
                          result.emotional_state
                            .polarity ||
                          "Unknown"
                        ).toUpperCase()}

                      </strong>

                    </div>

                    <div className="state-detail">

                      <span>
                        Severity
                      </span>

                      <strong>

                        {(
                          result.emotional_state
                            .severity ||
                          "Unknown"
                        ).toUpperCase()}

                      </strong>

                    </div>

                    <div className="state-detail">

                      <span>
                        Mixed Emotional State
                      </span>

                      <strong>

                        {displayValue(
                          result.emotional_state
                            .mixed_emotion ??
                          result.emotional_state
                            .mixed_emotional_state
                        )}

                      </strong>

                    </div>

                  </div>

                  <div className="detected-emotions">

                    <p className="small-label">
                      EMOTIONS CONTRIBUTING TO STATE
                    </p>

                    <div className="emotion-tags">

                      {(
                        result.emotional_state
                          .detected_emotions ||
                        result.multilabel_emotion
                          ?.detected_emotions ||
                        []
                      ).length > 0 ? (

                        (
                          result.emotional_state
                            .detected_emotions ||
                          result.multilabel_emotion
                            ?.detected_emotions ||
                          []
                        ).map(
                          (
                            emotion,
                            index
                          ) => (

                            <span
                              className="emotion-tag"
                              key={`${emotion}-${index}`}
                            >
                              {emotion}
                            </span>

                          )
                        )

                      ) : (

                        <span className="no-emotions">
                          No additional emotions detected
                        </span>

                      )}

                    </div>

                  </div>

                  <div className="intensity-section">

                    <div className="intensity-header">

                      <span>
                        Emotional Intensity
                      </span>

                      <strong>

                        {number(
                          result.emotional_state
                            .intensity ??
                          result.emotional_state
                            .emotional_intensity
                        )}

                      </strong>

                    </div>

                    <div className="intensity-bar">

                      <div
                        className="intensity-fill"
                        style={{
                          width: `${Math.min(
                            100,
                            Math.max(
                              0,
                              (
                                result
                                  .emotional_state
                                  .intensity ??
                                result
                                  .emotional_state
                                  .emotional_intensity ??
                                0
                              ) * 100
                            )
                          )}%`,
                        }}
                      />

                    </div>

                    <div className="intensity-scale">

                      <span>
                        Low
                      </span>

                      <span>
                        Moderate
                      </span>

                      <span>
                        High
                      </span>

                    </div>

                  </div>

                </section>

              )}

              <section className="recommendation-card">

                <div className="recommendation-header">

                  <div>

                    <p className="small-label">
                      PERSONALIZED WELLNESS
                    </p>

                    <h4>
                      Recommendations for You
                    </h4>

                    <p>
                      Recommendations are generated
                      from your emotional state,
                      preferences, previous interactions,
                      and multiple recommendation strategies.
                    </p>

                  </div>

                  <div className="recommendation-icon">
                    ✨
                  </div>

                </div>

                {/* USER PROFILE */}

                <div className="preference-section">

                  <p className="small-label">
                    USER PROFILE
                  </p>

                  <div className="user-selector-wrapper">

                    <select
                      className="user-selector"
                      value={selectedUser}
                      onChange={(event) =>
                        setSelectedUser(
                          event.target.value
                        )
                      }
                    >

                      <option value="user_001">
                        User 1
                      </option>

                      <option value="user_002">
                        User 2
                      </option>

                      <option value="user_003">
                        User 3
                      </option>

                    </select>

                  </div>

                  <p className="preference-note">

                    Select the employee profile whose
                    recommendation history and collaborative
                    behavior should be used.

                  </p>

                </div>

                {/* USER PREFERENCES */}

                <div className="preference-section">

                  <p className="small-label">
                    YOUR PREFERENCES
                  </p>

                  <div className="preference-options">

                    {preferenceOptions.map(
                      (preference) => {

                        const selected =
                          selectedPreferences.includes(
                            preference
                          );

                        return (

                          <button
                            type="button"
                            key={preference}
                            className={`preference-chip ${
                              selected
                                ? "selected"
                                : ""
                            }`}
                            onClick={() =>
                              togglePreference(
                                preference
                              )
                            }
                          >

                            {selected
                              ? "✓ "
                              : ""}

                            {preference}

                          </button>

                        );
                      }
                    )}

                  </div>

                  <p className="preference-note">

                    Select activities you prefer.
                    These preferences are sent to
                    the recommendation model.

                  </p>

                </div>

                <div className="personalization-grid">

                  <button
                    type="button"
                    className="personalization-item clickable"
                    onClick={
                      handlePreviousInteractions
                    }
                  >

                    <span>
                      Previous Interactions
                    </span>

                    <strong>
                      {previousInteractionCount}
                    </strong>

                    <small>

                      {previousInteractionsLoading
                        ? "Loading..."
                        : "Click to view"}

                    </small>

                  </button>

                  <div className="personalization-item">

                    <span>
                      Detected Emotion
                    </span>

                    <strong>

                      {(
                        result.emotional_state
                          ?.dominant_emotion ||
                        result.emotional_state
                          ?.primary_emotion ||
                        result.multilabel_emotion
                          ?.primary_emotion ||
                        result.emotion
                          ?.emotion ||
                        "Unknown"
                      ).toUpperCase()}

                    </strong>

                  </div>

                  <div className="personalization-item">

                    <span>
                      Emotion Intensity
                    </span>

                    <strong>

                      {percentage(
                        result.emotional_state
                          ?.intensity ??
                        result.emotional_state
                          ?.emotional_intensity
                      )}

                    </strong>

                  </div>

                  <button
                    type="button"
                    className="personalization-item clickable"
                    onClick={
                      handleRecommendationHistory
                    }
                  >

                    <span>
                      Recommendation History
                    </span>

                    <strong>

                      {recommendationHistoryCount > 0
                        ? "Available"
                        : "New user"}

                    </strong>

                    <small>
                      Click to view
                    </small>

                  </button>

                </div>

                {/* PREVIOUS INTERACTIONS */}

                {showPreviousInteractions && (

                  <div className="history-panel">

                    <div className="history-header">

                      <div>

                        <p className="small-label">
                          PREVIOUS INTERACTIONS
                        </p>

                        <h5>
                          Previous Recommendation Interactions
                        </h5>

                        <p>
                          Previously generated recommendation
                          sessions stored by the backend.
                        </p>

                      </div>

                      <button
                        type="button"
                        className="history-close"
                        onClick={() =>
                          setShowPreviousInteractions(
                            false
                          )
                        }
                      >
                        ×
                      </button>

                    </div>

                    {previousInteractionsLoading ? (

                      <div className="history-empty">
                        Loading previous interactions...
                      </div>

                    ) : previousInteractions.length === 0 ? (

                      <div className="history-empty">

                        <h5>
                          No previous interactions found.
                        </h5>

                        <p>
                          Generate a personalized
                          recommendation and it will
                          appear here.
                        </p>

                      </div>

                    ) : (

                      <div className="history-list">

                        {previousInteractions.map(
                          (
                            interaction,
                            index
                          ) => (

                            <article
                              className="history-item"
                              key={
                                interaction.id ||
                                index
                              }
                            >

                              <div className="history-rank">
                                {previousInteractions.length - index}
                              </div>

                              <div className="history-content">

                                <div className="history-item-header">

                                  <h6>
                                    {
                                      interaction
                                        .top_recommendation
                                        ?.title ||
                                      "Recommendation Interaction"
                                    }
                                  </h6>

                                  <div className="history-score">

                                    {interaction.created_at
                                      ? new Date(
                                          interaction.created_at
                                        ).toLocaleString()
                                      : "Date unavailable"}

                                  </div>

                                </div>

                                {interaction.text && (

                                  <p>
                                    <strong>Feedback:</strong>{" "}
                                    {interaction.text}
                                  </p>

                                )}

                                {interaction.preferences &&
                                  interaction.preferences.length > 0 && (

                                  <>

                                    <div className="history-section-label">
                                      Preferences
                                    </div>

                                    <div className="history-preferences">

                                      {interaction.preferences.map(
                                        (
                                          preference,
                                          preferenceIndex
                                        ) => (

                                          <span
                                            key={`${preference}-${preferenceIndex}`}
                                          >
                                            {preference}
                                          </span>

                                        )
                                      )}

                                    </div>

                                  </>

                                )}

                                {interaction.top_recommendation && (

                                  <div className="history-recommendation">

                                    <strong>Top Recommendation:</strong>{" "}

                                    {
                                      interaction
                                        .top_recommendation
                                        .title ||
                                      "Wellness Recommendation"
                                    }

                                  </div>

                                )}

                              </div>

                            </article>

                          )
                        )}

                      </div>

                    )}

                  </div>

                )}

                {/* RECOMMENDATION HISTORY */}

                {showRecommendationHistory && (

                  <div className="history-panel">

                    <div className="history-header">

                      <div>

                        <p className="small-label">
                          RECOMMENDATION HISTORY
                        </p>

                        <h5>
                          Your Recommendation History
                        </h5>

                        <p>
                          Recommendations generated during
                          this session.
                        </p>

                      </div>

                      <button
                        type="button"
                        className="history-close"
                        onClick={() =>
                          setShowRecommendationHistory(
                            false
                          )
                        }
                      >
                        ×
                      </button>

                    </div>

                    {recommendationHistoryData.length === 0 ? (

                      <div className="history-empty">

                        <h5>
                          No recommendation history found.
                        </h5>

                        <p>
                          Generate personalized
                          recommendations to build your
                          recommendation history.
                        </p>

                      </div>

                    ) : (

                      <div className="history-list">

                        {recommendationHistoryData
                          .slice()
                          .reverse()
                          .map(
                            (
                              recommendation,
                              index
                            ) => (

                              <article
                                className="history-item"
                                key={
                                  recommendation.id ||
                                  `${recommendation.title}-${index}`
                                }
                              >

                                <div className="history-rank">

                                  {recommendationHistoryData.length -
                                    index}

                                </div>

                                <div className="history-content">

                                  <div className="history-item-header">

                                    <h6>

                                      {
                                        recommendation
                                          .title ||
                                        "Wellness Recommendation"
                                      }

                                    </h6>

                                    <div className="history-score">

                                      {percentage(
                                        recommendation.score
                                      )}

                                    </div>

                                  </div>

                                  <div className="history-meta">

                                    <span>
                                      <strong>Type:</strong>{" "}
                                      {recommendationType(
                                        recommendation.type
                                      )}
                                    </span>

                                    <span>
                                      <strong>Final score:</strong>{" "}
                                      {percentage(
                                        recommendation.score
                                      )}
                                    </span>

                                    <span>
                                      <strong>Semantic:</strong>{" "}
                                      {percentage(
                                        recommendation.semantic_score
                                      )}
                                    </span>

                                  </div>

                                  <p>

                                    {
                                      recommendation
                                        .description ||
                                      "No description available."
                                    }

                                  </p>

                                  {recommendation.tags &&
                                    recommendation.tags
                                      .length > 0 && (

                                    <div className="history-preferences">

                                      {recommendation.tags.map(
                                        (
                                          tag,
                                          tagIndex
                                        ) => (

                                          <span
                                            key={`${tag}-${tagIndex}`}
                                          >
                                            {tag}
                                          </span>

                                        )
                                      )}

                                    </div>

                                  )}

                                  {recommendation.ranking_reason && (

                                    <div className="history-recommendation">

                                      <strong>
                                        Why recommended:
                                      </strong>{" "}

                                      {Array.isArray(
                                        recommendation.ranking_reason
                                      )
                                        ? recommendation.ranking_reason.join(
                                            ", "
                                          )
                                        : recommendation.ranking_reason}

                                    </div>

                                  )}

                                </div>

                              </article>

                            )
                          )}

                      </div>

                    )}

                  </div>

                )}

                {/* GENERATE RECOMMENDATIONS */}

                <button
                  type="button"
                  className="recommend-button"
                  onClick={
                    handleRecommendations
                  }
                  disabled={
                    recommendationLoading
                  }
                >

                  {recommendationLoading
                    ? "Generating..."
                    : "Generate Personalized Recommendations"}

                  {!recommendationLoading && (

                    <span>
                      →
                    </span>

                  )}

                </button>

                {/* RECOMMENDATION RESULTS */}

                {recommendations && (

                  <div className="recommendation-results">

                    {/* HYBRID ENGINE SUMMARY */}

                    <div className="hybrid-summary">

                      <div className="hybrid-summary-header">

                        <div>

                          <p className="small-label">
                            RECOMMENDATION INTELLIGENCE
                          </p>

                          <h5>
                            Hybrid Recommendation Engine
                          </h5>

                          <p>
                            The final ranking combines multiple
                            recommendation strategies to personalize
                            wellness suggestions.
                          </p>

                        </div>

                        <div className="hybrid-engine-icon">
                          ⚙️
                        </div>

                      </div>

                      <div className="hybrid-summary-stats">

                        <div className="hybrid-stat">

                          <span>
                            Strategy
                          </span>

                          <strong>
                            Hybrid
                          </strong>

                        </div>

                        <div className="hybrid-stat">

                          <span>
                            User
                          </span>

                          <strong>
                            {recommendations.user_id ||
                              selectedUser}
                          </strong>

                        </div>

                        <div className="hybrid-stat">

                          <span>
                            Collaborative Users
                          </span>

                          <strong>
                            {recommendations
                              .collaborative_users_available ??
                              0}
                          </strong>

                        </div>

                        <div className="hybrid-stat">

                          <span>
                            Method
                          </span>

                          <strong>
                            {recommendations.method ||
                              "Hybrid"}
                          </strong>

                        </div>

                      </div>

                      {/* M3-T4 RANKING VALIDATION */}

                      <div className="ranking-validation">

                        <div className="ranking-validation-header">

                          <div>

                            <p className="small-label">
                              RECOMMENDATION RANKING
                            </p>

                            <h6>
                              Dynamic Ranking Validation
                            </h6>

                          </div>

                        </div>

                        <div className="ranking-validation-grid">

                          <div className="ranking-validation-item">

                            <span>
                              Recommendations
                            </span>

                            <strong>
                              {recommendations.count ??
                                recommendations.recommendations
                                  ?.length ??
                                0}
                            </strong>

                          </div>

                          <div className="ranking-validation-item">

                            <span>
                              Duplicates filtered
                            </span>

                            <strong>
                              {recommendations.duplicate_filtered ??
                                0}
                            </strong>

                          </div>

                          <div className="ranking-validation-item">

                            <span>
                              Low relevance filtered
                            </span>

                            <strong>
                              {recommendations.low_relevance_filtered ??
                                0}
                            </strong>

                          </div>

                          <div className="ranking-validation-item">

                            <span>
                              Ranking order
                            </span>

                            <strong>
                              {recommendations.ranking_order &&
                              recommendations.ranking_order.length > 0
                                ? recommendations.ranking_order
                                    .map(
                                      (id, index) =>
                                        `#${index + 1} ${id}`
                                    )
                                    .join(" → ")
                                : "Not available"}
                            </strong>

                          </div>

                        </div>

                      </div>

                      {recommendations.hybrid_weights && (

                        <div className="hybrid-weights">

                          <div className="hybrid-weights-header">

                            <div>

                              <p className="small-label">
                                HYBRID WEIGHTS
                              </p>

                              <h6>
                                Contribution of Each Strategy
                              </h6>

                            </div>

                            <span>
                              100%
                            </span>

                          </div>

                          <div className="weight-list">

                            <div className="weight-row">

                              <span>
                                Rule-based
                              </span>

                              <strong>
                                {percentage(
                                  recommendations
                                    .hybrid_weights
                                    .rule_based
                                )}
                              </strong>

                            </div>

                            <div className="weight-row">

                              <span>
                                Content-based
                              </span>

                              <strong>
                                {percentage(
                                  recommendations
                                    .hybrid_weights
                                    .content_based
                                )}
                              </strong>

                            </div>

                            <div className="weight-row">

                              <span>
                                Preference matching
                              </span>

                              <strong>
                                {percentage(
                                  recommendations
                                    .hybrid_weights
                                    .preference_matching
                                )}
                              </strong>

                            </div>

                            <div className="weight-row">

                              <span>
                                Collaborative filtering
                              </span>

                              <strong>
                                {percentage(
                                  recommendations
                                    .hybrid_weights
                                    .collaborative_filtering
                                )}
                              </strong>

                            </div>

                            <div className="weight-row">

                              <span>
                                Emotion similarity
                              </span>

                              <strong>
                                {percentage(
                                  recommendations
                                    .hybrid_weights
                                    .emotion_similarity
                                )}
                              </strong>

                            </div>

                            <div className="weight-row">

                              <span>
                                Historical behavior
                              </span>

                              <strong>
                                {percentage(
                                  recommendations
                                    .hybrid_weights
                                    .historical_behavior
                                )}
                              </strong>

                            </div>

                            <div className="weight-row">

                              <span>
                                Semantic similarity
                              </span>

                              <strong>
                                {percentage(
                                  recommendations
                                    .hybrid_weights
                                    .semantic_similarity
                                )}
                              </strong>

                            </div>

                          </div>

                        </div>

                      )}

                    </div>

                    {/* TOP RECOMMENDATION */}

                    {recommendations.top_recommendation && (

                      <div className="top-recommendation">

                        <div className="top-recommendation-label">
                          TOP MATCH
                        </div>

                        <div className="top-recommendation-heading">

                          <div>

                            <h5>
                              {
                                recommendations
                                  .top_recommendation
                                  .title
                              }
                            </h5>

                            <span className="top-score">

                              Final ranking score:{" "}
                              {percentage(
                                recommendations
                                  .top_recommendation
                                  .score
                              )}

                            </span>

                          </div>

                        </div>

                        <div className="top-ranking-score-grid">

                          <div>

                            <span>
                              Base hybrid score
                            </span>

                            <strong>
                              {percentage(
                                recommendations
                                  .top_recommendation
                                  .base_score ??
                                recommendations
                                  .top_recommendation
                                  .score
                              )}
                            </strong>

                          </div>

                          <div>

                            <span>
                              Feedback adjustment
                            </span>

                            <strong>
                              {recommendations
                                .top_recommendation
                                .feedback_score !==
                              undefined
                                ? `${
                                    recommendations
                                      .top_recommendation
                                      .feedback_score >=
                                    0
                                      ? "+"
                                      : ""
                                  }${percentage(
                                    recommendations
                                      .top_recommendation
                                      .feedback_score
                                  )}`
                                : "0.00%"}
                            </strong>

                          </div>

                          <div>

                            <span>
                              Final learned score
                            </span>

                            <strong>
                              {percentage(
                                recommendations
                                  .top_recommendation
                                  .learned_score ??
                                recommendations
                                  .top_recommendation
                                  .score
                              )}
                            </strong>

                          </div>

                        </div>

                        <p>

                          {
                            recommendations
                              .top_recommendation
                              .description
                          }

                        </p>

                        {recommendations
                          .top_recommendation
                          .ranking_reason && (

                          <div className="ranking-reason">

                            <strong>
                              Why this was recommended:
                            </strong>{" "}

                            {Array.isArray(
                              recommendations
                                .top_recommendation
                                .ranking_reason
                            )
                              ? recommendations
                                  .top_recommendation
                                  .ranking_reason.join(
                                    ", "
                                  )
                              : recommendations
                                  .top_recommendation
                                  .ranking_reason}

                          </div>

                        )}

                        {recommendations
                          .top_recommendation
                          .explanation
                          ?.summary && (

                          <div className="recommendation-explanation">

                            {
                              recommendations
                                .top_recommendation
                                .explanation
                                .summary
                            }

                          </div>

                        )}

                      </div>

                    )}

                    {/* RECOMMENDATION LIST */}

                    <div className="recommendation-list">

                      {(
                        recommendations
                          .recommendations ||
                        []
                      ).map(
                        (
                          recommendation,
                          index
                        ) => (

                          <article
                            className="recommendation-item"
                            key={
                              recommendation.id ||
                              `${recommendation.title}-${index}`
                            }
                          >

                            <div className="recommendation-rank">

                              {recommendation.rank ||
                                index + 1}

                            </div>

                            <div className="recommendation-content">

                              <div className="recommendation-item-header">

                                <div>

                                  <h5>

                                    {
                                      recommendation
                                        .title ||
                                      "Wellness Recommendation"
                                    }

                                  </h5>

                                  <span className="recommendation-type">

                                    {recommendationType(
                                      recommendation
                                        .type
                                    )}

                                  </span>

                                </div>

                                <div className="recommendation-score">

                                  {percentage(
                                    recommendation.score
                                  )}

                                </div>

                              </div>

                              <p>

                                {
                                  recommendation
                                    .description ||
                                  "No description available."
                                }

                              </p>

                              {recommendation.tags &&
                                recommendation.tags
                                  .length > 0 && (

                                <div className="recommendation-tags">

                                  {recommendation.tags.map(
                                    (
                                      tag,
                                      tagIndex
                                    ) => (

                                      <span
                                        key={`${tag}-${tagIndex}`}
                                      >
                                        {tag}
                                      </span>

                                    )
                                  )}

                                </div>

                              )}

                              {/* M3-T4 FINAL RANKING SCORE */}

                              <div className="final-ranking-section">

                                <div className="final-ranking-header">

                                  <span>
                                    Final ranking score
                                  </span>

                                  <strong>
                                    {percentage(
                                      recommendation.score
                                    )}
                                  </strong>

                                </div>

                                <div className="final-ranking-grid">

                                  <div className="final-ranking-item">

                                    <span>
                                      Base hybrid
                                    </span>

                                    <strong>
                                      {percentage(
                                        recommendation
                                          .base_score ??
                                        recommendation
                                          .score
                                      )}
                                    </strong>

                                  </div>

                                  <div className="final-ranking-item">

                                    <span>
                                      Feedback adjustment
                                    </span>

                                    <strong>
                                      {recommendation
                                        .feedback_score !==
                                      undefined
                                        ? `${
                                            recommendation
                                              .feedback_score >=
                                            0
                                              ? "+"
                                              : ""
                                          }${percentage(
                                            recommendation
                                              .feedback_score
                                          )}`
                                        : "0.00%"}
                                    </strong>

                                  </div>

                                  <div className="final-ranking-item">

                                    <span>
                                      Learned score
                                    </span>

                                    <strong>
                                      {percentage(
                                        recommendation
                                          .learned_score ??
                                        recommendation
                                          .score
                                      )}
                                    </strong>

                                  </div>

                                  <div className="final-ranking-item">

                                    <span>
                                      Rank
                                    </span>

                                    <strong>
                                      #{recommendation.rank ||
                                        index + 1}
                                    </strong>

                                  </div>

                                </div>

                              </div>

                              {/* TASK 3 HYBRID SCORE BREAKDOWN */}

                              <div className="hybrid-score-section">

                                <div className="hybrid-score-heading">

                                  <span>
                                    Hybrid score breakdown
                                  </span>

                                  <strong>
                                    {percentage(
                                      recommendation
                                        .base_score ??
                                      recommendation.score
                                    )}
                                  </strong>

                                </div>

                                <div className="hybrid-score-grid">

                                  {hybridScoreItems.map(
                                    (item) => (

                                      <div
                                        className="hybrid-score-item"
                                        key={item.key}
                                      >

                                        <span>
                                          {item.label}
                                        </span>

                                        <strong>
                                          {percentage(
                                            recommendation[
                                              item.key
                                            ]
                                          )}
                                        </strong>

                                      </div>

                                    )
                                  )}

                                </div>

                              </div>

                              <div className="recommendation-meta">

                                <span>

                                  Final score:{" "}

                                  {percentage(
                                    recommendation.score
                                  )}

                                </span>

                                <span>

                                  Personalization:{" "}

                                  {percentage(
                                    recommendation
                                      .personalization_score
                                  )}

                                </span>

                                <span>

                                  Semantic match:{" "}

                                  {percentage(
                                    recommendation
                                      .semantic_score
                                  )}

                                </span>

                                <span>

                                  Feedback:{" "}

                                  {recommendation
                                    .feedback_score !==
                                  undefined
                                    ? `${
                                        recommendation
                                          .feedback_score >=
                                        0
                                          ? "+"
                                          : ""
                                      }${percentage(
                                        recommendation
                                          .feedback_score
                                      )}`
                                    : "0.00%"}

                                </span>

                              </div>

                              {recommendation.ranking_reason && (

                                <div className="recommendation-ranking-detail">

                                  <strong>
                                    Ranking reason:
                                  </strong>{" "}

                                  {Array.isArray(
                                    recommendation.ranking_reason
                                  )
                                    ? recommendation.ranking_reason.join(
                                        ", "
                                      )
                                    : recommendation.ranking_reason}

                                </div>

                              )}

                            </div>

                          </article>

                        )
                      )}

                    </div>

                  </div>

                )}

              </section>

              {/* WELLNESS RESULT */}

              {result.wellness && (

                <div
                  className={`wellness-result ${
                    result.wellness.risk_level ||
                    "low"
                  }`}
                >

                  <div className="wellness-icon">

                    {result.wellness.risk_level ===
                    "high"
                      ? "⚠️"
                      : result.wellness.risk_level ===
                        "medium"
                      ? "🟠"
                      : "🟢"}

                  </div>

                  <div className="wellness-info">

                    <p className="small-label">
                      WELLNESS RISK LEVEL
                    </p>

                    <h4 className="wellness-title">

                      {(
                        result.wellness.risk_level ||
                        "low"
                      ).toUpperCase()}

                    </h4>

                    <p className="wellness-insight">

                      {result.wellness.insight ||
                        "No wellness insight available."}

                    </p>

                  </div>

                </div>

              )}

            </div>

          )}

        </section>

      </main>

      <footer>

        <span>
          •
        </span>

        <span>
          Wellness Intelligence
        </span>

      </footer>

    </div>
  );
}

export default App;