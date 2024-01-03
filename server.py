from flask import Flask, jsonify, request, Response
from infer_utils import tts_split
from io import BytesIO
import soundfile


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
        return Response(f.getvalue(), mimetype="audio/wav")
    except Exception as e:
        print(e)
        return jsonify({"status": 40000000, "message": str(e)})


if __name__ == "__main__":
    app.run(host="localhost", port=47867)
