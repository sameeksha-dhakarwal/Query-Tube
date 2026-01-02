import pickle
import subprocess

# Load metadata
with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

video_id = input("Enter video ID to summarize: ").strip()

# Find video
video = next((v for v in metadata if v["video_id"] == video_id), None)

if not video:
    print("❌ Video ID not found in metadata.")
    exit()

# ✅ USE THE CORRECT KEY
transcript = video.get("transcript")

if not transcript or transcript.strip() == "":
    print("❌ Transcript not found for this video.")
    exit()

prompt = f"""
Summarize the following YouTube video clearly and concisely.
Focus on key ideas and main takeaways.

Transcript:
{transcript}
"""

# Call Ollama (llama3)
result = subprocess.run(
    ["ollama", "run", "llama3"],
    input=prompt.encode("utf-8"),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

summary = result.stdout.decode("utf-8", errors="ignore")

print("\n📝 Video Summary:\n")
print(summary)
