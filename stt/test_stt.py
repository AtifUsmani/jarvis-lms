import os
import sounddevice as sd
import soundfile as sf
# from faster_whisper import WhisperModel

def push_to_talk(model, output_file="recording.wav", samplerate=44100):
    """
    Simple push-to-talk recorder: record -> save -> transcribe -> return text
    """

    # Remove existing file
    if os.path.exists(output_file):
        os.remove(output_file)

    print("Press ENTER to start recording...")
    input()

    print("🔴 Recording... Press ENTER to stop")

    # Record audio directly
    recording = sd.rec(int(60 * samplerate), samplerate=samplerate, channels=1, dtype='float64')
    input()  # Wait for stop
    sd.stop()

    print("⏹️  Saving audio...")

    # Write the file
    sf.write(output_file, recording, samplerate)

    print("🎯 Transcribing...")

    # Transcribe
    segments, _ = model.transcribe(output_file)
    transcription = " ".join([segment.text for segment in segments])

    print(f"Transcription: {transcription}")
    return transcription.strip()

def record_and_transcribe(model, duration=5, samplerate=16000):
    """
    Record audio for a short duration and transcribe with Whisper.
    Designed to be called after wake word detection.

    Args:
        model: WhisperModel instance.
        duration (float): Recording duration in seconds.
        samplerate (int): Audio sample rate.

    Returns:
        str: Transcribed text.
    """
    # Prepare temporary file
    output_file = "command.wav"
    if os.path.exists(output_file):
        os.remove(output_file)

    print(f"🎤 Recording for {duration} seconds...")

    # Record audio
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()

    print("⏹️ Recording done. Saving audio...")
    sf.write(output_file, recording, samplerate)

    print("🎯 Transcribing...")
    segments, _ = model.transcribe(output_file, beam_size=5)
    transcription = " ".join([segment.text for segment in segments])

    print(f"Transcription: {transcription.strip()}")
    return transcription.strip()

# # Example usage
# if __name__ == "__main__":
#     model = WhisperModel("base.en", device="cpu", compute_type="float32")
#     result = record_and_transcribe(model)
#     print(f"Got: '{result}'")
