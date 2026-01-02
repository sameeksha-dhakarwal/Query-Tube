import subprocess
from pathlib import Path
import pandas as pd
from faster_whisper import WhisperModel
from utils import ensure_dir, save_csv, load_csv
import math
import tempfile
import time

# Paths
VIDEO_CSV = Path(r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\Tech_with_Tim.csv")
AUDIO_DIR = Path(r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\audio_downloads")
OUTPUT_CSV = Path(r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\twt_transcripts.csv")

# Ensure directories exist
ensure_dir(AUDIO_DIR)

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def download_audio(video_id: str) -> Path:
    """Download audio from YouTube with retries"""
    out_path = AUDIO_DIR / f"{video_id}.mp3"
    if out_path.exists():
        print(f"🎵 Already downloaded: {video_id}")
        return out_path

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"⬇️ Downloading {video_id} (Attempt {attempt})...")
            cmd = (
                f'yt-dlp -x --audio-format mp3 '
                f'-o "{out_path}" '
                f'"https://www.youtube.com/watch?v={video_id}" '
                f'--ignore-errors --no-check-certificate'
            )
            subprocess.run(cmd, shell=True, check=True)
            if out_path.exists():
                print(f"✅ Download successful: {video_id}")
                return out_path
        except Exception as e:
            print(f"❌ Download failed for {video_id}: {e}")
            time.sleep(RETRY_DELAY)

    print(f"⚠️ Could not download audio for {video_id} after {MAX_RETRIES} attempts")
    return None

def transcribe_audio_chunks_ffmpeg(model, audio_path: Path) -> str:
    """Split audio into chunks using ffmpeg and transcribe each chunk"""
    # Get audio duration
    result = subprocess.run(
        ['ffprobe', '-i', str(audio_path), '-show_entries', 'format=duration',
         '-v', 'quiet', '-of', 'csv=p=0'],
        capture_output=True, text=True
    )
    duration_sec = float(result.stdout.strip())
    full_text = ""

    chunk_length_sec = 300  # 5 minutes per chunk
    num_chunks = math.ceil(duration_sec / chunk_length_sec)
    print(f"⏱ Audio length: {duration_sec:.1f}s, splitting into {num_chunks} chunks")

    for i in range(num_chunks):
        start = i * chunk_length_sec
        end = min((i + 1) * chunk_length_sec, duration_sec)

        # Create temporary chunk
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
            chunk_path = Path(tmpfile.name)

        # Extract chunk with ffmpeg
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i", str(audio_path),
            "-ss", str(start),
            "-to", str(end),
            "-c", "copy",
            str(chunk_path)
        ]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"▶️ Transcribing chunk {i+1}/{num_chunks} ({start:.1f}s - {end:.1f}s)...")
        segments, _ = model.transcribe(str(chunk_path))
        chunk_text = " ".join([s.text for s in segments])
        full_text += chunk_text + " "

        # Remove temporary chunk
        chunk_path.unlink()

    return full_text.strip()

def main():
    print("📌 Loading video list...")
    df = load_csv(VIDEO_CSV)
    video_ids = df["id"].tolist()
    print(f"Found {len(video_ids)} videos")

    # Load model on CPU
    model = WhisperModel("base", device="cpu")

    transcripts = []

    for idx, vid in enumerate(video_ids, start=1):
        print(f"\n[{idx}/{len(video_ids)}] Processing video: {vid}")

        audio_path = download_audio(vid)
        if not audio_path:
            print(f"⛔ Skipping transcription — audio missing: {vid}")
            transcripts.append({"id": vid, "transcript": ""})
            continue

        try:
            text = transcribe_audio_chunks_ffmpeg(model, audio_path)
            transcripts.append({"id": vid, "transcript": text})
            print(f"📝 Transcription completed for: {vid}")
        except Exception as e:
            print(f"❌ Error transcribing {vid}: {e}")
            transcripts.append({"id": vid, "transcript": ""})

    # Save all transcripts
    save_csv(transcripts, OUTPUT_CSV)
    print(f"\n🎉 All transcriptions completed. Saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
