from sys import stderr
from flask import Flask, jsonify, request, Response
from infer_utils import tts_split
from io import BytesIO
import soundfile
from typing import Dict
import json
import numpy as np
import sox
import subprocess
import os


app = Flask(__name__)

mapping: Dict[str, str] = (
    json.load(open("mapping.json", "r")) if os.path.exists("mapping.json") else {}
)


def encode_wav(audio: np.ndarray) -> bytes:
    f = BytesIO()
    soundfile.write(f, audio, 44100, format="WAV")
    return f.getvalue()


def encode_mp3(audio: np.ndarray) -> bytes:
    # https://superkogito.github.io/blog/2020/03/19/ffmpeg_pipe.html
    ffmpeg_command = [
        "ffmpeg",
        "-i",
        "-",
        "-f",
        "mp3",
        "-acodec",
        "libmp3lame",
        "-b:a",
        "320k",
        "-",
    ]
    process = subprocess.Popen(
        ffmpeg_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    mp3_data, err = process.communicate(input=encode_wav(audio))
    if process.returncode != 0:
        raise Exception(f"ffmpeg error: {err.decode()}")
    return mp3_data


@app.get("/tts")
def tts():
    try:
        text = request.args.get("text", type=str)
        if not text:
            return jsonify({"status": 400, "message": "No text provided"})
        length_scale = request.args.get("length_scale", 1.0, type=float)
        if not 0.1 <= length_scale <= 2:
            return jsonify(
                {
                    "status": 400,
                    "message": "length_scale must be between 0.1 and 2",
                }
            )
        for src, dst in mapping.items():
            text = text.replace(src, dst)

        audio = tts_split(text, length_scale=length_scale)

        target_fs = request.args.get("fs", default=44100, type=int)
        format = request.args.get("format", default="mp3", type=str)

        if target_fs != 44100:
            audio = (
                sox.Transformer()
                .rate(target_fs)
                .build_array(input_array=audio, sample_rate_in=44100)
            )

        match format:
            case "mp3":
                return Response(encode_mp3(audio), mimetype="audio/mpeg")
            case "wav":
                return Response(encode_wav(audio), mimetype="audio/wav")
            case _:
                return jsonify({"status": 400, "message": "Unrecognized format"})
    except Exception as e:
        print(e)
        return jsonify({"status": 400, "message": str(e)})


if __name__ == "__main__":
    app.run(host="localhost", port=47867)
