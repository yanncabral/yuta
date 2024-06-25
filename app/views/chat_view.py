from flask import Blueprint, jsonify, render_template, request

from app.database import database
from app.models.chat import Chat, ChatMessage
from app.repositories.chat_repository import ChatRepository
from app.usecases.transcript_audio import transcript_audio

chat_bp = Blueprint("chat_bp", __name__)


@chat_bp.route("/", methods=["GET"])
def chat():
    chat_repository: ChatRepository = ChatRepository(database=database)
    chat = chat_repository.find_one_by({})
    if not chat:
        chat = Chat(messages=[])
        chat_repository.save(chat)

    print({"chat": chat})

    return render_template("chat/chat_page.html", messages=chat.messages)


@chat_bp.route("/chat/upload_audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400

    audio_file = request.files["audio"]

    command, transcription = transcript_audio(audio_file)

    repository = ChatRepository(database=database)
    chat = repository.find_one_by({})
    chat.messages.append(ChatMessage(role="user", content=transcription))
    repository.save(chat)

    return jsonify({"command": command, "transcription": transcription}), 200


@chat_bp.route("/chat/send_message", methods=["POST"])
def send_message():
    message = request.json["message"]

    if not message:
        return jsonify({"error": "Mensagem não informada"}), 400

    repository = ChatRepository(database=database)
    chat = repository.find_one_by({})
    chat.messages.append(ChatMessage(role="user", content=message))
    repository.save(chat)

    return jsonify({"message": message}), 201
