import whisper
import os
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

# Load Whisper model globally (use 'base' for speed in a hackathon)
model = whisper.load_model("base")

def convert_audio(input_path: str) -> str:
    """
    Converts audio to WAV (16-bit PCM, mono, 16kHz) for Whisper compatibility.
    Returns path to converted file.
    """
    try:
        output_path = "converted_audio.wav"
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000)  # Whisper expects 16kHz mono
        audio.export(output_path, format="wav", codec="pcm_s16le")
        return output_path
    except CouldntDecodeError:
        raise Exception(f"Failed to decode audio file: {input_path}")
    except Exception as e:
        raise Exception(f"Audio conversion error: {str(e)}")

def transcribe_audio(file_path: str) -> str:
    """
    Transcribes audio file using Whisper and returns the text.
    """
    try:
        print("Transcribing audio...")
        converted_path = convert_audio(file_path)
        result = model.transcribe(converted_path)
        transcript = result["text"].strip()
        
        print(f"Transcription complete: {transcript}")
        # Optionally save transcript (remove if not needed for hackathon)
        with open("transcript.txt", "w") as f:
            f.write(transcript)
        
        # Clean up temporary file
        if os.path.exists(converted_path):
            os.remove(converted_path)
        
        return transcript
    except Exception as e:
        raise Exception(f"Transcription error: {str(e)}")

