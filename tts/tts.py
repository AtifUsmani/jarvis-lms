import requests
import io
import requests
import io
import simpleaudio as sa
import time
import os
import yaml

from pydub import AudioSegment
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import threading
import sounddevice as sd
import soundfile as sf

# Load the YAML config
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

API_URL = config["TTS"]["API_URL"]
TTS_OUTPUT_DIR = "tts_outputs"
prompt_text = config["TTS"]["prompt_text"]

# ensure folder exists
os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)

# Setup session with retries
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[502, 503, 504])
session.mount("http://", HTTPAdapter(max_retries=retries))

def tts_generate(text, ref_wav="your_ref.wav", prompt_text=prompt_text, prompt_lang="en", text_lang="en"):
    payload = {
        "refer_wav_path": ref_wav,
        "prompt_text": prompt_text,
        "prompt_language": prompt_lang,
        "text": text,
        "text_language": text_lang,
        "speed": 1.0
    }

    # Retry logic for robust TTS request
    for attempt in range(3):
        try:
            response = session.post(API_URL, json=payload, timeout=30)
            response.raise_for_status()
            break
        except (requests.exceptions.ChunkedEncodingError, requests.exceptions.RequestException) as e:
            print(f"TTS request failed (attempt {attempt+1}/3): {e}")
            time.sleep(1)
    else:
        raise RuntimeError("TTS request failed after 3 attempts.")

    audio_bytes = io.BytesIO(response.content)
    audio = AudioSegment.from_file(audio_bytes, format="wav")

    play_obj = sa.play_buffer(
        audio.raw_data,
        num_channels=audio.channels,
        bytes_per_sample=audio.sample_width,
        sample_rate=audio.frame_rate
    )
    play_obj.wait_done()

def play_audio_bytes(audio_bytes: bytes):
    data, sr = sf.read(io.BytesIO(audio_bytes))
    sd.play(data, sr)
    sd.wait()

def tts_chunk(text_chunk, ref_wav="your_ref.wav", prompt_text=prompt_text, prompt_lang="en", text_lang="en"):
    payload = {
        "refer_wav_path": ref_wav,
        "prompt_text": prompt_text,
        "prompt_language": prompt_lang,
        "text": text_chunk,
        "text_language": text_lang,
        "speed": 1.0
    }

    # Retry logic
    for attempt in range(3):
        try:
            r = session.post(API_URL, json=payload, timeout=30)
            r.raise_for_status()
            return r.content
        except (requests.exceptions.ChunkedEncodingError, requests.exceptions.RequestException) as e:
            print(f"TTS chunk request failed (attempt {attempt+1}/3): {e}")
            time.sleep(1)
    raise RuntimeError("TTS chunk request failed after 3 attempts.")

def speak_async(text_chunk, **kwargs):
    """Non-blocking playback with retries"""
    threading.Thread(target=lambda: play_audio_bytes(tts_chunk(text_chunk, **kwargs))).start()

def tts_request(text, ref_wav="your_ref.wav", filename="output.wav", prompt_text=prompt_text,
                prompt_lang="en", text_lang="en"):
    payload = {
        "refer_wav_path": ref_wav,
        "prompt_text": prompt_text,
        "prompt_language": prompt_lang,
        "text": text,
        "text_language": text_lang,
        "speed": 1.0
    }

    for attempt in range(3):
        try:
            r = session.post(API_URL, json=payload, timeout=60)
            r.raise_for_status()
            file_path = os.path.join(TTS_OUTPUT_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(r.content)
            return file_path
        except (requests.exceptions.RequestException) as e:
            print(f"TTS request failed (attempt {attempt+1}/3): {e}")
            time.sleep(1)
    raise RuntimeError("TTS request failed after 3 attempts.")

def speak(text, ref_wav="your_ref.wav", filename="output.wav"):
    file_path = tts_request(text, ref_wav=ref_wav, filename=filename)
    data, sr = sf.read(file_path, dtype='float32')
    sd.play(data, sr)
    sd.wait()