import pandas as pd
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer

CSV_PATH = r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\embedded_output1.csv"
INDEX_PATH = "vector.index"
METADATA_PATH = "metadata.pkl"

# Load CSV
df = pd.read_csv(CSV_PATH)
df["transcript"] = df["transcript"].fillna("")

texts = df["transcript"].tolist()

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate normalized embeddings (FOR COSINE SIMILARITY)
embeddings = model.encode(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True
).astype("float32")

dimension = embeddings.shape[1]

# COSINE SIMILARITY INDEX
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

faiss.write_index(index, INDEX_PATH)

# Metadata aligned with vectors
metadata = df[[
    "id",
    "title",
    "channel_title",
    "viewCount",
    "duration",
    "transcript"
]].rename(columns={
    "id": "video_id",
    "viewCount": "view_count"
}).to_dict(orient="records")

with open(METADATA_PATH, "wb") as f:
    pickle.dump(metadata, f)

print(f"✅ Stored {index.ntotal} vectors")
print("✅ Index & metadata saved successfully")
