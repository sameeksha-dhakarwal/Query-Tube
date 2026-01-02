from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import os

app = FastAPI(title="VectorDB Ingestion API")

# File paths
VECTOR_DB_PATH = "vector_db"
METADATA_PATH = "metadata.pkl"

# Request schema
class IngestRequest(BaseModel):
    video_id: str
    transcript: str


@app.post("/ingest")
def ingest_data(request: IngestRequest):
    """
    Ingest transcript data into vector DB (metadata for now).
    """
    # Load existing metadata
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "rb") as f:
            metadata = pickle.load(f)
    else:
        metadata = []

    # Check duplicate video_id
    for item in metadata:
        if item["video_id"] == request.video_id:
            return {
                "status": "failed",
                "message": "Video ID already exists"
            }

    # Add new record
    metadata.append({
        "video_id": request.video_id,
        "transcript": request.transcript
    })

    # Save metadata
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    return {
        "status": "success",
        "message": "Transcript ingested successfully",
        "video_id": request.video_id
    }
