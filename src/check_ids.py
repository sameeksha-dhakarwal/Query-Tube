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
COOKIES_FILE = r"E:\Internship\Infosys Springboard\Infosys TASK1\INFOSYS TASK1\cookies.txt"  # Exported from Firefox

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
failed_downloads = []
failed_transcripts = []

# ===============================
# Audio Download Function
# ===============================
def download_audio(vid, retry=False):
    """
    Download audio using yt-dlp with cookies.
    Detects 0-byte files and retries.
    """
    out = AUDIO_DIR / f"{vid}.mp3"

    # Skip valid existing audio
    if out.exists() and out.stat().st_size > 1024:
        print(f"🎵 Already downloaded: {vid}")
        return str(out)

    print(f"⬇️ Downloading audio for {vid}...")

    try:
        cmd = (
            f'yt-dlp -x --audio-format mp3 '
            f'--cookies "{COOKIES_FILE}" '
            f'--ignore-errors --no-check-certificate '
            f'-o "{out}" "https://www.youtube.com/watch?v={vid}"'
        )

        subprocess.run(cmd, shell=True, check=True)

        # Validate file size
        if not out.exists() or out.stat().st_size < 1024:
            raise Exception("0-byte / incomplete audio file")

        print(f"✅ Download successful: {vid}")
        return str(out)

    except Exception as e:
        print(f"❌ Failed to download {vid}: {e}")
        if not retry:
            failed_downloads.append(vid)
        return None

# ===============================
# Transcription Function
# ===============================
def transcribe_audio(vid):
    """
    Transcribe a video audio file using Whisper.
    """
    audio_file = download_audio(vid)

    if audio_file is None:
        print(f"⛔ Skipping transcription — audio missing for: {vid}")
        failed_transcripts.append(vid)
        return {"id": vid, "transcript": ""}

    try:
        print(f"📝 Transcribing {vid} ...")
        result = model.transcribe(audio_file)
        return {"id": vid, "transcript": result["text"]}

    except Exception as e:
        print(f"❌ Whisper transcription failed for {vid}: {e}")
        failed_transcripts.append(vid)
        return {"id": vid, "transcript": ""}

# ===============================
# Main Function
# ===============================
def main():
    df = load_csv(VIDEO_CSV)
    video_ids = df["id"].tolist()

    print(f"📌 Total videos: {len(video_ids)}")
    print("🚀 Starting full download + transcription pipeline...\n")

    # -------------------------
    # STEP 1 — PARALLEL AUDIO DOWNLOADS
    # -------------------------
    print("🎧 Downloading all audio files (parallel)...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(download_audio, vid): vid for vid in video_ids}
        for fut in as_completed(futures):
            fut.result()  # errors logged inside function

    # Retry failed downloads once
    if failed_downloads:
        print(f"\n🔁 Retrying {len(failed_downloads)} failed downloads...\n")
        for vid in failed_downloads[:]:
            audio_file = download_audio(vid, retry=True)
            if audio_file:
                failed_downloads.remove(vid)

    print("\n🎵 Audio download stage complete!")
    if failed_downloads:
        print(f"❗ Still failed downloads: {failed_downloads}")

    # -------------------------
    # STEP 2 — Transcription
    # -------------------------
    print("\n✍ Transcribing videos...\n")
    results = []

    for vid in video_ids:
        print("\n------------------------------------------------------------")
        print(f"▶️ Processing video: {vid}")
        res = transcribe_audio(vid)
        results.append(res)

    # -------------------------
    # STEP 3 — Save Output
    # -------------------------
    save_csv(results, OUTPUT_CSV)
    print("\n💾 Transcripts saved!")

    # -------------------------
    # STEP 4 — Summary
    # -------------------------
    print("\n================ SUMMARY ================")
    print(f"Total videos: {len(video_ids)}")
    print(f"Failed downloads: {failed_downloads}")
    print(f"Failed transcriptions: {failed_transcripts}")
    print("=========================================")
    print("\n🎉 DONE — all videos processed!\n")


if __name__ == "__main__":
    main()
