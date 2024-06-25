import os
import subprocess
import tempfile

import openai
from werkzeug.datastructures import FileStorage

from app.database import database
from app.repositories.devices_repository import DevicesRepository

openai.api_key = os.getenv("OPENAI_API_KEY")


def convert_to_wav(audio_file: FileStorage) -> str:
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_audio:
        audio_file.save(temp_audio)
        temp_audio_path = temp_audio.name

    temp_wav_path = temp_audio_path.replace(".mp4", ".wav")
    try:
        subprocess.run(
            ["ffmpeg", "-i", temp_audio_path, temp_wav_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        return f"Erro ao converter áudio: {e.stderr.decode()}"

    return temp_wav_path


def build_command_by_transcription(transcription):
    contexto = """
    Você é um assistente especializado em transformar solicitações de usuários em código Python. Sua tarefa é pegar a solicitação do usuário e retornar apenas o código Python correspondente, sempre delimitando o código com '$' no início e no fim. O código deve ser claro e funcional, pronto para ser executado.
    Exemplo:
    Solicitação: "Teste a função soma."
    Resposta:
    $
    resultado = soma(3, 5)
    print(f"Resultado: {resultado}")
    $

    Os dispositivos registrados são os seguintes:
    """

    repository = DevicesRepository(database=database)
    devices = repository.find_by({})

    for device in devices:
        contexto += "\nnome: %s, tipo: %s" % (device.name, device.type)

    contexto2 = """
        Sempre use alguma das seguintes funções (de acordo com o tipo do dispositivo):
            def acao_rgb(nome_dispositivo,acao,cores) [cores em uma lista no rgb, exemplo: [0,255,127], se nao informado pelo usuário, passe None]
            def acao_led(nome_dispositivo,acao)
            def acao_ventilador(nome_dispositivo,acao,velocidade) [velocidade um inteiro entre 1 e 3, se nao informado pelo usuário, passe None]
            def acao_porta(nome_dispositivo,acao)
        """

    contexto += contexto2
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": contexto},
                {"role": "user", "content": transcription},
            ],
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.8,
        )

        message: str = resposta.choices[0].message["content"]
        message = message.replace("$", "").strip()
        return message
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"


def transcript_audio(audio_file: FileStorage) -> (str, str):
    temp_audio_path = convert_to_wav(audio_file)

    with open(temp_audio_path, "rb") as audio:
        transcription = openai.Audio.transcribe("whisper-1", audio, language="pt")["text"]
        command = build_command_by_transcription(transcription)
        return command, transcription
