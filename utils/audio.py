import os
import shutil
import glob
from pathlib import Path

import yt_dlp
import ffmpeg

# ==================== DIRECTORIES ====================
DOWNLOAD_YT_DIR = "downloads"
LOCAL_INPUT_DIR = "local_inputs"

os.makedirs(DOWNLOAD_YT_DIR, exist_ok=True)
os.makedirs(LOCAL_INPUT_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """
    Download YouTube audio directly as WAV.
    """

    output_template = os.path.join(DOWNLOAD_YT_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "downloaded_audio")
        wav_path = os.path.join(DOWNLOAD_YT_DIR, f"{title}.wav")

    return wav_path


def copy_to_local_dir(source: str) -> str:
    """
    Copy uploaded/local file into project folder.
    """
    source_path = Path(source)

    if not source_path.exists():
        raise FileNotFoundError(f"File not found: {source}")

    destination = Path(LOCAL_INPUT_DIR) / source_path.name
    counter = 1

    while destination.exists():
        destination = (
            Path(LOCAL_INPUT_DIR)
            / f"{source_path.stem}_{counter}{source_path.suffix}"
        )
        counter += 1
    shutil.copy2(source_path, destination)
    return str(destination)


def convert_to_wav(input_path: str) -> str:
    """
    Convert any audio/video into:
        - WAV
        - Mono
        - 16kHz
    """

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    (
        ffmpeg
        .input(input_path)
        .output(
            output_path,
            ac=1,
            ar=16000,
            format="wav",
        )
        .overwrite_output()
        .run(quiet=True)
    )

    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10):
    """
    Split WAV into fixed-length chunks using FFmpeg.
    """

    output_pattern = (
        os.path.splitext(wav_path)[0]
        + "_chunk_%03d.wav"
    )

    (
        ffmpeg
        .input(wav_path)
        .output(
            output_pattern,
            f="segment",
            segment_time=chunk_minutes * 60,
            c="copy",
        )
        .overwrite_output()
        .run(quiet=True)
    )

    chunks = sorted(
        glob.glob(
            os.path.splitext(wav_path)[0]
            + "_chunk_*.wav"
        )
    )

    return chunks


def process_input(source: str):
    """
    Accepts either:
        - YouTube URL
        - Local audio/video file

    Returns:
        List of WAV chunk paths.
    """

    if source.startswith(("http://", "https://")):

        print("Detected YouTube URL...")
        wav_path = download_youtube_audio(source)
        print("Downloaded:", wav_path)

    else:

        print("Detected local file...")
        local_copy = copy_to_local_dir(source)
        print("Copied:", local_copy)
        wav_path = convert_to_wav(local_copy)
        print("Converted:", wav_path)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Created {len(chunks)} chunks.")
    return chunks







# import yt_dlp
# from pydub import AudioSegment
# import os
# import shutil
# from pathlib import Path

# # ==================== DIRECTORIES ====================
# DOWNLOAD_YT_DIR = 'downloads'           # YouTube downloads
# LOCAL_INPUT_DIR = 'local_inputs'        # Local files (mp4, mp3, wav, etc.)
# os.makedirs(DOWNLOAD_YT_DIR, exist_ok=True)
# os.makedirs(LOCAL_INPUT_DIR, exist_ok=True)

# def download_youtube_audio(url: str) -> str:
#     """Download YouTube audio and convert to WAV."""
#     output_path = os.path.join(DOWNLOAD_YT_DIR, "%(title)s.%(ext)s")
    
#     ydl_opts = {
#         "format": "bestaudio/best",
#         "outtmpl": output_path,
#         "postprocessors": [{
#             "key": "FFmpegExtractAudio",
#             "preferredcodec": "wav",
#             "preferredquality": "192",
#         }],
#         "quiet": True,
#     }
    
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=True)
        
#         # Get the actual filename
#         try:
#             raw_fname = ydl.prepare_filename(info)
#         except Exception:
#             raw_fname = None

#         if isinstance(raw_fname, dict):
#             filename = raw_fname.get("filename") or raw_fname.get("filepath") or str(raw_fname)
#         elif isinstance(raw_fname, str):
#             filename = raw_fname
#         else:
#             title = info.get("title", "downloaded_audio") if isinstance(info, dict) else "downloaded_audio"
#             filename = os.path.join(DOWNLOAD_YT_DIR, f"{title}.wav")

#         # Ensure .wav extension after post-processing
#         base, _ = os.path.splitext(filename)
#         wav_path = base + ".wav"
        
#     return wav_path


# def copy_to_local_dir(source: str) -> str:
#     """Copy local file to local_inputs folder to keep original safe."""
#     source_path = Path(source)
#     if not source_path.exists():
#         raise FileNotFoundError(f"File not found: {source}")
    
#     dest_path = Path(LOCAL_INPUT_DIR) / source_path.name
    
#     # Avoid overwriting if same name already exists
#     counter = 1
#     original_stem = dest_path.stem
#     while dest_path.exists():
#         dest_path = Path(LOCAL_INPUT_DIR) / f"{original_stem}_{counter}{dest_path.suffix}"
#         counter += 1
    
#     shutil.copy2(source, dest_path)
#     return str(dest_path)


# def convert_to_wav(input_path: str) -> str:
#     """Convert any audio/video file to standardized WAV (16kHz, mono)."""
#     output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    
#     audio = AudioSegment.from_file(input_path)
#     # Standardize for speech models: mono + 16kHz
#     audio = audio.set_channels(1).set_frame_rate(16000)
#     audio.export(output_path, format="wav")
    
#     return output_path


# def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
#     """Split audio into chunks."""
#     audio = AudioSegment.from_wav(wav_path)
#     chunk_ms = chunk_minutes * 60 * 1000

#     chunks = []
#     for i, start in enumerate(range(0, len(audio), chunk_ms)):
#         chunk = audio[start : start + chunk_ms]
#         chunk_path = f"{os.path.splitext(wav_path)[0]}_chunk_{i:03d}.wav"
#         chunk.export(chunk_path, format="wav")
#         chunks.append(chunk_path)
    
#     return chunks


# def process_input(source: str) -> list:
#     """
#     Main function to process either YouTube URL or local file.
#     Returns list of chunked WAV paths.
#     """
#     if source.startswith(("http://", "https://")):
#         print("Detected YouTube URL. Downloading audio...")
#         wav_path = download_youtube_audio(source)
#         print(f"YouTube audio downloaded: {wav_path}")
#     else:
#         print("Detected local file. Processing...")
#         # Copy to local folder first
#         local_copy = copy_to_local_dir(source)
#         print(f"File copied to local directory: {local_copy}")
        
#         # Convert to standardized WAV
#         wav_path = convert_to_wav(local_copy)
#         print(f"Converted to WAV: {wav_path}")

#     print("Chunking audio...")
#     chunks = chunk_audio(wav_path)
#     print(f"✅ Audio ready — {len(chunks)} chunk(s) created.")

#     return chunks