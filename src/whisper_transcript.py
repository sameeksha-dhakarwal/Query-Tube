import subprocess
import whisper
import torch
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import ensure_dir, load_csv, save_csv
import time

# ===============================
# Paths
# ===============================
VIDEO_CSV = r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\Tech_with_Tim.csv"
AUDIO_DIR = Path(r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\audio_downloads")
OUTPUT_CSV = r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\twt_transcripts.csv"

ensure_dir(AUDIO_DIR)

# ===============================
# Device Setup
# ===============================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🔧 Using device: {device}")

# Load Whisper model
model_name = "tiny"  # tiny = fastest, base = more accurate
model = whisper.load_model(model_name).to(device)

# ===============================
# Globals
# ===============================
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
failed_downloads = []
failed_transcripts = []

# ===============================
# Audio Download Function
# ===============================
def download_audio(vid):
    """
    Download audio using yt-dlp.
    Retries automatically if download fails or file is 0-byte.
    """
    out = AUDIO_DIR / f"{vid}.mp3"

    # Skip existing valid audio
    if out.exists() and out.stat().st_size > 1024:
        print(f"🎵 Already downloaded: {vid}")
        return str(out)

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"⬇️ Downloading {vid} (attempt {attempt})...")
        cmd = f'yt-dlp -x --audio-format mp3 -o "{out}" "https://www.youtube.com/watch?v={vid}"'
        try:
            subprocess.run(cmd, shell=True, check=True)
            if out.exists() and out.stat().st_size > 1024:
                print(f"✅ Download successful: {vid}")
                return str(out)
        except Exception as e:
            print(f"❌ Download attempt {attempt} failed for {vid}: {e}")
        time.sleep(RETRY_DELAY)

    print(f"⚠️ Failed to download {vid} after {MAX_RETRIES} attempts")
    failed_downloads.append(vid)
    return None

# ===============================
# Transcription Function
# ===============================
def transcribe_audio(vid):
    audio_file = download_audio(vid)
    if audio_file is None:
        failed_transcripts.append(vid)
        return {"id": vid, "transcript": ""}

    try:
        print(f"📝 Transcribing {vid} ...")
        result = model.transcribe(audio_file)
        return {"id": vid, "transcript": result["text"]}
    except Exception as e:
        print(f"❌ Whisper failed for {vid}: {e}")
        failed_transcripts.append(vid)
        return {"id": vid, "transcript": ""}

# ===============================
# Main Function
# ===============================
def main():
    df = load_csv(VIDEO_CSV)
    video_ids = df["id"].tolist()
    print(f"📌 Total videos to process: {len(video_ids)}\n")

    results = []

    # -------------------------
    # STEP 1 — Parallel Downloads & Transcriptions
    # -------------------------
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(transcribe_audio, vid): vid for vid in video_ids}
        for future in as_completed(futures):
            vid = futures[future]
            try:
                res = future.result()
                results.append(res)
                print(f"✅ Completed: {vid}")
            except Exception as e:
                print(f"❌ Failed: {vid}, error: {e}")
                failed_transcripts.append(vid)

    # -------------------------
    # STEP 2 — Retry failed downloads/transcriptions once
    # -------------------------
    if failed_downloads or failed_transcripts:
        print(f"\n🔁 Retrying failed downloads/transcriptions...")
        retry_ids = list(set(failed_downloads + failed_transcripts))
        failed_downloads.clear()
        failed_transcripts.clear()
        for vid in retry_ids:
            res = transcribe_audio(vid)
            results.append(res)

    # -------------------------
    # STEP 3 — Save transcripts
    # -------------------------
    save_csv(results, OUTPUT_CSV)
    print("\n💾 Transcripts saved!")
    if failed_downloads or failed_transcripts:
        print(f"⚠️ Some videos still failed:")
        print(f"Failed downloads: {failed_downloads}")
        print(f"Failed transcripts: {failed_transcripts}")
    else:
        print("🎉 All videos processed successfully!")

# ===============================
if __name__ == "__main__":
    main()
