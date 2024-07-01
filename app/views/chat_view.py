from typing import Optional
from flask import Blueprint, jsonify, render_template, request

from app.database import database
from app.models.chat import Chat, ChatMessage
from app.repositories.chat_repository import ChatRepository
from app.usecases.transcript_audio import build_command_by_text, transcript_audio

chat_bp = Blueprint("chat_bp", __name__)

class ChatManager:
    def __init__(self, chat: Optional[Chat] = None):
        self.repository = ChatRepository(database=database)
        self.chat = chat or self.repository.find_one_by({})
        if not self.chat:
            self.chat = Chat(messages=[])
            self.repository.save(self.chat)

    def send_message(self, message: str) -> Chat:
        self.chat.messages.append(ChatMessage(role="user", content=message))
        self.repository.save(self.chat)
        response, command = build_command_by_text(message)
        self.chat.messages.append(ChatMessage(role="assistant", content=response))
        self.repository.save(self.chat)

        print({
            "command": command,
            "response": response
        })

        # TODO: Executar o comando

        return self.chat


    def get_messages(self):
        return self.chat.messages

chat_manager = ChatManager()

@chat_bp.route("/", methods=["GET"])
def chat():
    return render_template("chat/chat_page.html", messages=chat_manager.get_messages())


@chat_bp.route("/chat/upload_audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400

    audio_file = request.files["audio"]

    command, transcription = transcript_audio(audio_file)

    chat_manager.send_message(transcription)

    return jsonify({"command": command, "transcription": transcription}), 200


@chat_bp.route("/chat/send_message", methods=["POST"])
def send_message():
    message = request.json["message"]

    if not message:
        return jsonify({"error": "Mensagem não informada"}), 400

    chat_manager.send_message(message)

    return jsonify({"message": message}), 201
