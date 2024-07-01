import os
import subprocess
import tempfile
from typing import Optional

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


def build_command_by_text(transcription) -> tuple[str, Optional[str]]:
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

    contexto += """
        Sempre use alguma das seguintes funções (de acordo com o tipo do dispositivo):
            def acao_rgb(nome_dispositivo,acao,cores) [cores em uma lista no rgb, exemplo: [0,255,127], se nao informado pelo usuário, passe None]
            def acao_led(nome_dispositivo,acao)
            def acao_ventilador(nome_dispositivo,acao,velocidade) [velocidade um inteiro entre 1 e 3, se nao informado pelo usuário, passe None]
            def acao_porta(nome_dispositivo,acao)

        Além disso, retorne uma mensagem que possa ser usada como mensagem para o usuário, caso não tenha entendido o comando, ou tenha executado com sucesso, sem aspas e separado por ### entre o comando e a mensagem. Por exemplo:

        entrada do usuário: "Ligue o ventilador do meu quarto"
        resposta: "Entendi, ligando o ventilador do quarto. ### acao_ventilador('ventilador do quarto', 'LIGAR', 2)"

        Caso não seja um comando, apenas responda a pergunta, passando o comando como uma string vazia. Por exemplo:

        entrada do usuário: "quais dispositivos existem cadastrados?"
        resposta: "Dispositivos cadastrados: ventilador do quarto, porta do meu quarto. ###"
        """

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

        response: str = resposta.choices[0].message["content"]
        response = response.replace("$", "").strip()
        response = response.split("###")
        command = response[0].strip()
        message = response[1].strip() if len(response) > 1 else None
        return command, message
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"


def transcript_audio(audio_file: FileStorage) -> (str, str):
    temp_audio_path = convert_to_wav(audio_file)

    with open(temp_audio_path, "rb") as audio:
        transcription = openai.Audio.transcribe("whisper-1", audio, language="pt")["text"]
        command, _ = build_command_by_text(transcription)
        return command, transcription
