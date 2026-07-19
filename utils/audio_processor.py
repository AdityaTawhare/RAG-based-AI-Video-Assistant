import re
import yt_dlp
from pydub import AudioSegment 
import os
    
DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def extract_youtube_video_id(url: str) -> str:
    """Extract 11-character video ID from various YouTube URL formats."""
    pattern = r"(?:v=|\/|be\/|embed\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def fetch_youtube_transcript_direct(video_id: str) -> str:
    """Attempt instant transcript retrieval via youtube_transcript_api (bypasses cloud IP audio blocks)."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'hi', 'en-IN'])
        text = " ".join([item.get('text', '') for item in transcript_list])
        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"Direct YouTube transcript API unavailable for {video_id}: {e}")
    return None

def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    # Try different player clients to bypass YouTube cloud datacenter IP blocks
    client_configs = [
        ["mweb", "ios"],
        ["tv_embedded", "android"],
        ["web_embedded", "web"]
    ]
    
    last_error = None
    for clients in client_configs:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "extractor_args": {
                "youtube": {
                    "player_client": clients
                }
            },
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav").replace(".mp4", ".wav")
            return filename
        except Exception as e:
            last_error = e

    raise RuntimeError(
        "YouTube blocked automated audio download from Streamlit Cloud's IP address. "
        "Please use the '📁 Upload File' tab to upload your video/audio file directly!"
    ) from last_error



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
        print("Detected YouTube URL.")
        video_id = extract_youtube_video_id(source)
        if video_id:
            direct_text = fetch_youtube_transcript_direct(video_id)
            if direct_text:
                print("Direct YouTube transcript retrieved successfully! Skipping audio download.")
                txt_path = os.path.join(DOWNLOAD_DIR, f"yt_{video_id}_transcript.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(direct_text)
                return [txt_path]

        print("Direct transcript unavailable. Downloading audio via yt-dlp...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks