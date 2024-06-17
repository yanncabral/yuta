import openai
import pyaudio
import wave
from pymongo import MongoClient
#from micro import acao_rgb, acao_led, acao_porta, acao_ventilador

openai.api_key = ''
client = MongoClient("localhost",27017)
db = client['dispositivos']
dispositivos_collection = db['dispositivos']

def testes(numPrompt):
    lTestes = []
    lResults = []
    teste1 = ["ligar luz do banheiro", 'acao_led("luz do banheiro", "ligar")']
    teste2 = ["ligar ventilador do quarto na velocidade 2", 'acao_ventilador("ventilador do quarto", "ligar", 2)']
    teste3 = ["ligar quarto e a luz da sala na cor vermelha", 'acao_led("luz do quarto","ligar")\nacao_rgb("luz da sala","ligar",[255,0,0)]']
    teste4 = ["ligar ventilador forte", 'acao_ventilador("ventilador do quarto", "ligar", 5)']
    teste5 = ["abrir porta da frente", 'acao_porta("porta da frente","abrir")']
    lTestes.append(teste1)
    lTestes.append(teste2)
    lTestes.append(teste3)
    lTestes.append(teste4)
    lTestes.append(teste5)


    if numPrompt == None:
        for teste in lTestes:
            resposta = gpt(teste[0])
            resposta = resposta.split("$")[1]   
            lResults.append(resposta)
    else:
        resposta = gpt(lTestes[numPrompt][0])
        resposta = resposta.split("$")[1]   
        lResults.append(resposta)


    for i, resultado in enumerate(lResults):
        print("Teste %d\nInput: %s\nOutput: %sEsperado:\n%s\n-----" %(i, lTestes[i][0], resultado, lTestes[i][1]))

    return

def gpt(pergunta):
    contexto =  """
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

    dispositivos = dispositivos_collection.find()
    for d in dispositivos:
        contexto += "\nnome: %s, tipo: %s" %(d['name'], d['type'])

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
                {"role": "user", "content": pergunta},
            ],
            max_tokens=200, 
            n=1,  
            stop=None, 
            temperature=0.8  
        )
        return resposta.choices[0].message['content']
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"

def gravarAudio(nomeArquivo, duracao=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = duracao
    WAVE_OUTPUT_FILENAME = nomeArquivo

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("--- Gravando áudio ---")

    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* Gravação finalizada")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcreverAudio(nomeArquivo):
    audio_file = open(nomeArquivo, "rb")
    try:
        resposta = openai.Audio.transcribe("whisper-1", audio_file)
        return resposta['text']
    except Exception as ex:
        return f"Erro ao transcrever áudio: {ex}"


gravarAudio("entrada_voz.wav")
pergunta = transcreverAudio("entrada_voz.wav")
if pergunta:
    print(f"Foi dito: {pergunta}")
    resposta = gpt(pergunta)
    resposta = resposta.split("$")[1]    
    print(resposta)
    print('-------------------------------------------------')
    #exec(resposta) #descomentar pra rodar o codigo dado pelo gpt
   
