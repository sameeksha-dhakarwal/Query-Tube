import { useState } from "react";
import "./App.css";

function App() {
  // ===============================
  // STATE
  // ===============================
  const [activeTab, setActiveTab] = useState("ingest");

  const [csvFile, setCsvFile] = useState(null);
  const [ingestMsg, setIngestMsg] = useState("");

  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const [videoId, setVideoId] = useState("");
  const [summary, setSummary] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const API_BASE = "http://127.0.0.1:8000";

  // ===============================
  // INGEST CSV
  // ===============================
  const handleCsvUpload = async () => {
    if (!csvFile) {
      setError("Please select a CSV file");
      return;
    }

    setLoading(true);
    setError("");
    setIngestMsg("");

    const formData = new FormData();
    formData.append("file", csvFile);

    try {
      const res = await fetch(`${API_BASE}/ingest-csv`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (data.error) {
        setError(data.error);
      } else {
        setIngestMsg(
          `✅ Ingestion completed successfully

Total Inserted rows: ${data.original_rows}`
        );
      }
    } catch {
      setError("Failed to upload CSV");
    } finally {
      setLoading(false);
    }
  };

  // ===============================
  // SEARCH
  // ===============================
  const handleSearch = async () => {
    if (!query.trim()) {
      setError("Enter a search query");
      return;
    }

    setLoading(true);
    setError("");
    setResults([]);
    setSummary("");

    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 5 }),
      });

      const data = await res.json();

      if (data.error) {
        setError(data.error);
      } else {
        setResults(data.results || []);
        if (data.results.length === 0) {
          setError("No results found");
        }
      }
    } catch {
      setError("Search failed");
    } finally {
      setLoading(false);
    }
  };

  // ===============================
  // SUMMARIZE (OLLAMA)
  // ===============================
  const handleSummarize = async () => {
    if (!videoId.trim()) {
      setError("Enter a video ID");
      return;
    }

    setLoading(true);
    setError("");
    setSummary("⏳ Generating summary using LLM...");

    try {
      const res = await fetch(
        `${API_BASE}/summarize?video_id=${videoId}`,
        { method: "POST" }
      );

      const data = await res.json();

      if (data.error) {
        setError(data.error);
        setSummary("");
      } else {
        setSummary(data.summary);
      }
    } catch {
      setError("Summarization failed");
      setSummary("");
    } finally {
      setLoading(false);
    }
  };

  // ===============================
  // UI
  // ===============================
  return (
  <div className="app-container">
    <h1>🎥 QueryTube</h1>
    <p>Semantic Video Search & LLM-based Summarization</p>

      {/* TAB BAR */}
      <div className="tab-bar">
        <button
          className={activeTab === "ingest" ? "active-tab" : ""}
          onClick={() => setActiveTab("ingest")}
        >
          INGEST
        </button>
        <button
          className={activeTab === "search" ? "active-tab" : ""}
          onClick={() => setActiveTab("search")}
        >
          SEARCH
        </button>
        <button
          className={activeTab === "summarize" ? "active-tab" : ""}
          onClick={() => setActiveTab("summarize")}
        >
          SUMMARIZE
        </button>
      </div>

      {/* INGEST TAB */}
      {activeTab === "ingest" && (
        <>
          <h2>📥 Ingest Videos (CSV)</h2>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setCsvFile(e.target.files[0])}
          />
          <button onClick={handleCsvUpload} disabled={loading}>
            Upload CSV
          </button>

          {ingestMsg && (
            <pre style={{ color: "green", whiteSpace: "pre-wrap" }}>
              {ingestMsg}
            </pre>
          )}
        </>
      )}

      {/* SEARCH TAB */}
      {activeTab === "search" && (
        <>
          <h2>🔍 Search Videos</h2>
          <input
            placeholder="Search query (e.g. python decorators)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button onClick={handleSearch} disabled={loading}>
            Search
          </button>

          <ul>
            {results.map((r, i) => (
              <li key={i}>
                <strong>{r.title}</strong><br />
                Channel: {r.channel_title}<br />
                Video ID: <b>{r.video_id}</b><br />
                🔗 Similarity: {r.similarity}
                <br />
                <button
                  onClick={() => {
                    setVideoId(r.video_id);
                    setActiveTab("summarize");
                  }}
                >
                  Summarize this video
                </button>
              </li>
            ))}
          </ul>
        </>
      )}

      {/* SUMMARIZE TAB */}
      {activeTab === "summarize" && (
        <>
          <h2>📝 Summarize Video (LLM)</h2>
          <input
            placeholder="Enter Video ID"
            value={videoId}
            onChange={(e) => setVideoId(e.target.value)}
          />
          <button onClick={handleSummarize} disabled={loading}>
            Generate Summary
          </button>

          {summary && (
            <div className="summary-box">
              <h3>Summary</h3>
              <p>{summary}</p>
            </div>
          )}
        </>
      )}

      {loading && <p className="loading">⏳ Processing...</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default App;
