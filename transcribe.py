import whisper
import os
from pydub import AudioSegment

# Load Whisper Model (Use 'base' for faster results, 'large' for best accuracy)
model = whisper.load_model("base")

def convert_audio(input_path):
    """
    Converts audio to WAV (16-bit PCM) if it's not already in the correct format.
    """
    output_path = "converted_audio.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # Ensure compatibility
    audio.export(output_path, format="wav")
    return output_path

def transcribe_audio(file_path):
    """
    Transcribes the given audio file using OpenAI Whisper.
    """
    print("Lyrics are COOKING!!!")
    converted_path = convert_audio(file_path)  # Ensure correct format
    result = model.transcribe(converted_path)
    
    print("AND ITS DONE!")
    print(result["text"])  # Display transcript
    
    # Save transcript
    with open("transcript.txt", "w") as f:
        f.write(result["text"])

    return result["text"]

if __name__ == "__main__":
    input_file = input("Enter path to audio file: ")
    if os.path.exists(input_file):
        transcribe_audio(input_file)
    else:
        print("File not found!")
