import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json

def wait_for_wake_word_vosk(model_path="model", wake_word="jarvis", sample_rate=16000, block_size=8000):
    """
    Listens for a specific wake word using Vosk and returns when detected.

    Args:
        model_path (str): Path to your Vosk model folder.
        wake_word (str): Wake word to detect.
        sample_rate (int): Audio sample rate.
        block_size (int): Audio block size for processing.

    Returns:
        None: Function returns after wake word is detected.
    """
    q = queue.Queue()
    model = Model(model_path)
    # Grammar: only recognize the wake word
    rec = KaldiRecognizer(model, sample_rate, f'["{wake_word}"]')

    def callback(indata, frames, time, status):
        if status:
            print(status)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=sample_rate, blocksize=block_size, dtype='int16',
                           channels=1, callback=callback):
        print(f"Listening for wake word '{wake_word}'...")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if 'text' in result and result['text'] == wake_word:
                    print(f"Wake word '{wake_word}' detected!")
                    break
