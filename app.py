from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, uuid

app = Flask(__name__)
CORS(app)

VOICE_DIR = "voices"
OUTPUT_DIR = "outputs"
os.makedirs(VOICE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/train-voice', methods=['POST'])
def train_voice():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400
    voice_id = "zsd_voice_" + str(uuid.uuid4())[:8]
    return jsonify({"success": True, "voice_id": voice_id, "message": "Voice trained - Demo Mode"})

@app.route('/generate-song', methods=['POST'])
def generate_song():
    data = request.get_json()
    song_id = str(uuid.uuid4())[:8]
    return jsonify({"success": True, "download_url": f"/download/{song_id}.mp3", "message": "Song generated - Demo Mode"})

@app.route('/download/<filename>')
def download(filename):
    return "Demo MP3 File"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
