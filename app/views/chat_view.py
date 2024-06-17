from flask import Blueprint, render_template
from flask import request, jsonify

from app.usecases.transcript_audio import transcript_audio


chat_bp = Blueprint("chat_bp", __name__)

@chat_bp.route("/", methods=["GET"])
def chat():
    return render_template("chat/chat_page.html")



@chat_bp.route("/chat/upload_audio", methods=["POST"])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400

    audio_file = request.files['audio']

    transcription = transcript_audio(audio_file)

    print('transcrição:', transcription)

    return jsonify({"transcription": transcription}), 200

