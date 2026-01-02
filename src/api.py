from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import pickle
import pandas as pd
import faiss
import requests
from sentence_transformers import SentenceTransformer

# ===============================
# APP INIT
# ===============================
app = FastAPI(
    title="Infosys Task 1 - VectorDB API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# CONFIG
# ===============================
INDEX_PATH = "vector.index"
METADATA_PATH = "metadata.pkl"
EMBEDDING_DIM = 384

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
else:
    index = faiss.IndexFlatIP(EMBEDDING_DIM)

# ===============================
# MODELS
# ===============================
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# ===============================
# HEALTH
# ===============================
@app.get("/")
def health_check():
    return {"status": "API running"}

# ===============================
# CSV INGEST
# ===============================
@app.post("/ingest-csv")
def ingest_csv(file: UploadFile = File(...)):

    global index

    df = pd.read_csv(file.file)
    df.columns = df.columns.str.strip()

    df["transcript"] = df.get("transcript", "").fillna("").astype(str)
    df["title"] = df.get("title", "").fillna("").astype(str)
    df["channel_title"] = df.get("channel_title", "").fillna("").astype(str)

    df["viewCount"] = pd.to_numeric(df.get("viewCount", 0), errors="coerce").fillna(0)
    df["duration_seconds"] = pd.to_numeric(df.get("duration_seconds", 0), errors="coerce").fillna(0)

    original_rows = len(df)

    # Lenient filtering
    df = df[
        (df["transcript"].str.len() > 20) |
        (df["title"].str.len() > 10)
    ].reset_index(drop=True)

    if df.empty:
        return {"error": "No valid rows found after filtering"}

    texts = df["transcript"].tolist()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)

    metadata = []
    for _, row in df.iterrows():
        metadata.append({
            "video_id": str(row["id"]),
            "title": row["title"],
            "channel_title": row["channel_title"],
            "view_count": int(row["viewCount"]),
            "duration": str(row["duration_seconds"]),
            "transcript": row["transcript"],
        })

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    return {
        "message": "CSV ingested successfully",
        "original_rows": original_rows,
        "rows_after_filtering": len(df),
        "vectors_stored": index.ntotal
    }

# ===============================
# SEARCH
# ===============================
@app.post("/search")
def search_videos(data: SearchRequest):

    if not os.path.exists(METADATA_PATH):
        return {"error": "No metadata found"}

    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)

    query_embedding = model.encode(
        [data.query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    distances, indices = index.search(query_embedding, data.top_k)

    results = []
    for idx, score in zip(indices[0], distances[0]):
        if idx < len(metadata):
            item = metadata[idx].copy()
            item["similarity"] = round(float(score), 4)
            results.append(item)

    return {"query": data.query, "results": results}

# ===============================
# SUMMARIZE (USING OLLAMA)
# ===============================
@app.post("/summarize")
def summarize_video(video_id: str):

    if not os.path.exists(METADATA_PATH):
        return {"error": "No metadata found"}

    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)

    video = next((v for v in metadata if v["video_id"] == video_id), None)

    if not video or not video["transcript"]:
        return {"error": "Video not found or transcript empty"}

    prompt = f"""
    Summarize the following video transcript in 5-6 concise bullet points:

    Transcript:
    {video['transcript']}
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code != 200:
        return {"error": "Failed to generate summary from Ollama"}

    summary = response.json().get("response", "").strip()

    return {
        "video_id": video_id,
        "title": video["title"],
        "summary": summary
    }
