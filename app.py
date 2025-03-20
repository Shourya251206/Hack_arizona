from flask import Flask, request, jsonify
import os
import whisper
import sqlite3
from werkzeug.utils import secure_filename
from pydub import AudioSegment
import json
import numpy as np

app = Flask(__name__)

# Set up upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a"}

# Initialize database
def init_db():
    """Creates a SQLite database for storing transcriptions if it doesn't exist."""
    conn = sqlite3.connect("transcriptions.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            transcription TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()  # Initialize database on startup

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_wav(input_path):
    """Convert M4A/MP3 file to WAV format for Whisper."""
    output_path = input_path.rsplit(".", 1)[0] + ".wav"
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="wav")
    return output_path

def transcribe_audio(file_path):
    """Transcribes an audio file using Whisper AI and returns formatted output."""
    model = whisper.load_model("medium")  # Load Whisper AI model
    result = model.transcribe(file_path, word_timestamps=True)  # Enable timestamps

    # Format transcript neatly
    formatted_transcription = []
    for segment in result["segments"]:
        formatted_transcription.append(
            f"[{round(segment['start'], 2)}s - {round(segment['end'], 2)}s]: {segment['text']}"
        )

    return formatted_transcription


@app.route("/", methods=["GET"])
def home():
    """Test route to verify Flask is running."""
    return jsonify({"message": "Flask API is running!"})

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles audio file uploads and transcribes the audio."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: MP3, WAV, M4A"}), 400

    # Save the uploaded file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Convert to WAV if necessary
    if filename.lower().endswith(("m4a", "mp3")):
        filepath = convert_to_wav(filepath)  # Convert M4A/MP3 to WAV

    # Transcribe the audio file
    transcription = transcribe_audio(filepath)

    # Store transcription in database
    conn = sqlite3.connect("transcriptions.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transcriptions (file_name, transcription) VALUES (?, ?)", 
                   (filename, str(transcription)))
    conn.commit()
    conn.close()

    return jsonify({
        "message": "File uploaded and transcribed successfully",
        "file_path": filepath,
        "transcription": transcription
    })

@app.route("/transcriptions", methods=["GET"])
def get_transcriptions():
    """Returns all stored transcriptions from the database with correctly formatted timestamps."""
    conn = sqlite3.connect("transcriptions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_name, transcription, timestamp FROM transcriptions ORDER BY timestamp DESC")

    transcriptions = []
    for row in cursor.fetchall():
        try:
            transcription_data = json.loads(row[2])  # Convert JSON string to dict
            # Convert np.float64 to regular float for JSON compatibility
            for segment in transcription_data:
                segment["start_time"] = float(segment["start_time"])
                segment["end_time"] = float(segment["end_time"])
        except json.JSONDecodeError:
            transcription_data = row[2]  # If parsing fails, return raw text

        transcriptions.append({
            "id": row[0],
            "file_name": row[1],
            "transcription": transcription_data,
            "timestamp": row[3]
        })

    conn.close()
    return jsonify({"transcriptions": transcriptions})



if __name__ == "__main__":
    app.run(debug=True)
