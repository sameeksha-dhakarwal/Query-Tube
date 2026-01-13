import { useState, useRef, useEffect } from "react";
import "./App.css";

export default function App() {
  const [activeTab, setActiveTab] = useState("search");

  /* SEARCH */
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  /* 🎤 SPEECH TO TEXT */
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  /* INGEST */
  const [csvFile, setCsvFile] = useState(null);
  const [ingestStats, setIngestStats] = useState(null);
  const [ingestError, setIngestError] = useState("");

  /* SUMMARY */
  const [videoId, setVideoId] = useState("");
  const [summary, setSummary] = useState("");

  /* SPEECH (TEXT TO SPEECH) */
  const speechRef = useRef(null);

  const API_BASE = "http://127.0.0.1:8000";

  const demoVideos = [
    { video_id: "aircAruvnKk", title: "Machine Learning Roadmap", channel_title: "Simplilearn" },
    { video_id: "ukzFI9rgwfU", title: "Data Structures Explained", channel_title: "CS Dojo" },
    { video_id: "Gv9_4yMHFhI", title: "History of Machine Learning", channel_title: "CodeBasics" },
  ];

  /* =====================
     🎤 INIT SPEECH RECOGNITION
  ===================== */
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      setQuery(transcript);
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognitionRef.current = recognition;
  }, []);

  const toggleMic = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition not supported in this browser");
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  /* =====================
     SPEECH CONTROL
  ===================== */
  const stopSpeech = () => {
    window.speechSynthesis.cancel();
    speechRef.current = null;
  };

  const handleSpeak = () => {
    if (!summary || summary === "loading") return;

    if (speechRef.current) {
      stopSpeech();
      return;
    }

    const utterance = new SpeechSynthesisUtterance(summary);
    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.onend = () => {
      speechRef.current = null;
    };

    speechRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  /* ✅ BACK */
  const goHome = () => {
    stopSpeech();
    try {
      if (recognitionRef.current) recognitionRef.current.stop();
    } catch {}
    setIsListening(false);
    setActiveTab("search");
  };

  /* =====================
     SEARCH
  ===================== */
  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 6 }),
      });

      const data = await res.json();
      setResults(data.results || []);
    } catch {
      setResults([]);
    }
  };

  /* =====================
     INGEST
  ===================== */
  const handleCsvUpload = async () => {
    if (!csvFile) {
      setIngestError("Please select a CSV file");
      return;
    }

    setIngestError("");
    setIngestStats(null);

    const formData = new FormData();
    formData.append("file", csvFile);

    try {
      const res = await fetch(`${API_BASE}/ingest-csv`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      data.error ? setIngestError(data.error) : setIngestStats(data);
    } catch {
      setIngestError("Upload failed");
    }
  };

  /* =====================
     SUMMARY
  ===================== */
  const handleSummarize = async () => {
    if (!videoId) return;

    setSummary("loading");

    try {
      const res = await fetch(
        `${API_BASE}/summarize?video_id=${videoId}`,
        { method: "POST" }
      );
      const data = await res.json();
      setSummary(data.summary || "No summary available");
    } catch {
      setSummary("Failed to generate summary");
    }
  };

  const videos = results.length > 0 ? results : demoVideos;

  /* ✅ OPEN YOUTUBE (RESTORED) */
  const openYouTube = (id) => {
    window.open(`https://www.youtube.com/watch?v=${id}`, "_blank", "noopener,noreferrer");
  };

  return (
    <>
      {/* TOP NAV */}
      <header className="top-nav">
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          {activeTab !== "search" && (
            <button className="back-btn-search" onClick={goHome} title="Back to Home">
              ←
            </button>
          )}
          <div className="logo">QueryTube</div>
        </div>

        <div className="nav-actions">
          <button onClick={() => { stopSpeech(); setActiveTab("ingest"); }}>
            Ingest
          </button>
          <button onClick={() => { stopSpeech(); setActiveTab("summarize"); }}>
            Summarize
          </button>
        </div>
      </header>

      <main className="main-container">
        {/* SEARCH */}
        {activeTab === "search" && (
          <>
            <section className="search-section">
              <div className="search-bar">
                {/* Back beside search (optional; you are already home) */}
                <button className="back-btn-search" onClick={goHome} title="Back to Home">
                  ←
                </button>

                <input
                  placeholder="Search query (e.g. python)"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />

                <button
                  className={`mic-btn ${isListening ? "listening" : ""}`}
                  onClick={toggleMic}
                  title="Voice search"
                >
                  🎙️
                </button>

                <button onClick={handleSearch}>Search</button>
              </div>
            </section>

            <section className="video-section">
              <div className="video-grid">
                {videos.map((v, i) => (
                  <div
                    className="video-card"
                    key={i}
                    role="button"
                    tabIndex={0}
                    onClick={() => openYouTube(v.video_id)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") openYouTube(v.video_id);
                    }}
                    style={{ cursor: "pointer" }}
                    title="Open on YouTube"
                  >
                    <img
                      src={`https://img.youtube.com/vi/${v.video_id}/hqdefault.jpg`}
                      alt={v.title}
                    />
                    <h4>{v.title}</h4>
                    <p>{v.channel_title}</p>

                    <button
                      onClick={(e) => {
                        e.stopPropagation(); // ✅ prevent opening youtube
                        stopSpeech();
                        setVideoId(v.video_id);
                        setSummary("");
                        setActiveTab("summarize");
                      }}
                    >
                      Summarize
                    </button>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}

        {/* INGEST */}
        {activeTab === "ingest" && (
          <section className="center-box">
            <h2>📥 Ingest CSV</h2>

            <input
              type="file"
              accept=".csv"
              onChange={(e) => setCsvFile(e.target.files[0])}
            />

            <button onClick={handleCsvUpload}>Upload CSV</button>

            {ingestStats && (
              <div className="summary-content">
                <pre>{JSON.stringify(ingestStats, null, 2)}</pre>
              </div>
            )}

            {ingestError && <p className="error">{ingestError}</p>}
          </section>
        )}
      </main>

      {/* SUMMARY WINDOW */}
      {activeTab === "summarize" && (
        <>
          <div className="summary-backdrop" onClick={goHome} />

          <div className="summary-window">
            <div className="summary-titlebar">
              <span className="summary-title">
                Summary: {videoId || "YouTube Video"}
              </span>

              <div className="window-controls">
                <span
                  className="win-btn"
                  onClick={handleSpeak}
                  style={{
                    opacity: summary && summary !== "loading" ? 1 : 0.4,
                    cursor: summary && summary !== "loading" ? "pointer" : "not-allowed",
                  }}
                  title={
                    summary && summary !== "loading"
                      ? "Read summary"
                      : "Generate summary first"
                  }
                >
                  🔊
                </span>

                <span className="win-btn close" onClick={goHome} title="Close">
                  ✕
                </span>
              </div>
            </div>

            <div className="summary-body">
              <input
                value={videoId}
                onChange={(e) => setVideoId(e.target.value)}
                placeholder="Enter video ID"
              />

              <button className="summary-btn" onClick={handleSummarize}>
                Get Summary
              </button>

              {summary === "loading" && (
                <div className="summary-loading">
                  <div className="spinner" />
                  <h4>Generating AI summary...</h4>
                  <p>This can take 15–60 seconds for long videos</p>
                </div>
              )}

              {summary && summary !== "loading" && (
                <div className="summary-content">{summary}</div>
              )}
            </div>
          </div>
        </>
      )}
    </>
  );
}
