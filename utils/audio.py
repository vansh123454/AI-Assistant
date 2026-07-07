import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)

def download_youtube_audio(url :str) ->str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename



def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path



def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
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