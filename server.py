from flask import Flask, jsonify, request, Response
from infer_utils import tts_split
from io import BytesIO
import soundfile
from pydub import AudioSegment


app = Flask(__name__)


@app.get("/tts")
def tts():
    try:
        text = request.args.get("text")
        if not text:
            return jsonify({"status": 40000000, "message": "No text provided"})
        audio = tts_split(text)
        f = BytesIO()
        soundfile.write(f, audio, 44100, format="WAV")
        f.seek(0)
        audio_segment = AudioSegment.from_file(f, format="wav")
        # Convert to MP3
        mp3_buffer = BytesIO()
        audio_segment.export(mp3_buffer, format="mp3", bitrate="320k")
        return Response(mp3_buffer.getvalue(), mimetype="audio/mpeg")
    except Exception as e:
        print(e)
        return jsonify({"status": 40000000, "message": str(e)})


if __name__ == "__main__":
    app.run(host="localhost", port=47867)
