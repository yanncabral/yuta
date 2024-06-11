from openai import OpenAI
from werkzeug.datastructures import FileStorage
import tempfile

client = OpenAI()

def transcript_audio(audio_file: FileStorage) -> str:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
        audio_file.save(temp_audio)
        temp_audio_path = temp_audio.name

    with open(temp_audio_path, 'rb') as audio:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
            language="pt"
        )

    return transcription.text
