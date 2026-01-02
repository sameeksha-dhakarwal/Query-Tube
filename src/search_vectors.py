import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# Load index
index = faiss.read_index("vector.index")

# Load metadata
with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Accept user query
query = input("\nEnter your search query: ")

# Convert query to embedding
query_embedding = model.encode(query).astype("float32").reshape(1, -1)

# Search
k = 5
distances, indices = index.search(query_embedding, k)

# Convert distance → similarity
def similarity(dist):
    return 1 / (1 + dist)

# Output
print("\n🔍 Top 5 Relevant Videos:\n")

for rank, (idx, dist) in enumerate(zip(indices[0], distances[0]), start=1):
    item = metadata[idx]
    print(f"{rank}. Video ID       : {item['video_id']}")
    print(f"   Title          : {item['title']}")
    print(f"   Channel Name   : {item['channel_title']}")
    print(f"   Similarity     : {similarity(dist):.4f}")
    print("-" * 60)
