import openai
from werkzeug.datastructures import FileStorage
import tempfile

def transcript_audio(audio_file: FileStorage) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        audio_file.save(temp_audio)
        temp_audio_path = temp_audio.name

    print(temp_audio_path)

    with open(temp_audio_path, 'rb') as audio:
        try:
            resposta = openai.Audio.transcribe("whisper-1", audio, language="pt")
            return resposta['text']
        except Exception as ex:
            return f"Erro ao transcrever áudio: {ex}"
