import os
import json
import requests
import time
import subprocess
import signal
from datetime import datetime, timezone, timedelta
from requests.auth import HTTPDigestAuth
import cv2

CONFIG_FILE = "config_cameras.json"
API_UPLOAD_URL = "https://esportes-x2p0.onrender.com/upload"
VIDEOS_DIR = "videos"


VIDEOS_BAIXADOS_FILE = "videos_baixados.json"

def carregar_videos_baixados():
    """Carrega a lista de vídeos já baixados do JSON."""
    if os.path.exists(VIDEOS_BAIXADOS_FILE):
        with open(VIDEOS_BAIXADOS_FILE, "r", encoding="utf-8") as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                print("⚠ Erro ao carregar vídeos baixados. Criando um novo arquivo...")
                return set()
    return set()

def salvar_videos_baixados(videos_baixados):
    """Salva a lista de vídeos baixados no JSON."""
    with open(VIDEOS_BAIXADOS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(videos_baixados), f, indent=4)


def carregar_configuracoes():
    """Carrega as configurações das câmeras do arquivo JSON."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"⚠ Arquivo de configuração '{CONFIG_FILE}' não encontrado!")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def listar_videos_existentes(pasta_camera):
    """Lista os vídeos já baixados na pasta da câmera."""
    if not os.path.exists(pasta_camera):
        return set()
    return {arquivo for arquivo in os.listdir(pasta_camera) if arquivo.endswith(".mp4")}

def listar_videos_na_api():
    """Consulta a API para obter a lista de vídeos já enviados e retorna apenas os nomes dos vídeos."""
    API_LISTAR_URL = "http://18.219.146.25:5000/list_videos"

    try:
        response = requests.get(API_LISTAR_URL)

        if response.status_code == 200:
            try:
                videos_api = response.json()
                if "videos" in videos_api and isinstance(videos_api["videos"], list):
                    return {video for video in videos_api["videos"] if video.endswith(".mp4")}  # Retorna um conjunto de nomes de vídeos
                else:
                    print("⚠ Estrutura do JSON inesperada. Esperado {'videos': [lista_de_videos]}")
                    return set()
            except json.JSONDecodeError:
                print("❌ Erro ao converter resposta para JSON.")
                return set()
        else:
            print(f"❌ Erro ao consultar API. Código: {response.status_code}")
            return set()
    
    except Exception as e:
        print(f"❌ Erro ao consultar API: {e}")
        return set()





def esperar_liberacao_arquivo(caminho_arquivo, tentativas=5, intervalo=4):
    """Aguarda o arquivo ser liberado antes de movê-lo."""
    for _ in range(tentativas):
        try:
            if os.path.exists(caminho_arquivo):
                os.rename(caminho_arquivo, caminho_arquivo)
                return True
        except PermissionError:
            time.sleep(intervalo)
    return False



def baixar_video_rtsp(url_rtsp, nome_arquivo, usuario, senha, max_tentativas=5):
    """Baixa um vídeo via RTSP, monitorando o progresso e tentando novamente se falhar."""
    url_rtsp_autenticada = url_rtsp.replace("rtsp://", f"rtsp://{usuario}:{senha}@")

    tentativas = 0
    sucesso = False

    while tentativas < max_tentativas and not sucesso:
        tentativas += 1
        print(f"🔄 Tentativa {tentativas}/{max_tentativas} para baixar {nome_arquivo}...")

        comando = [
            "ffmpeg", "-rtsp_transport", "tcp",
            "-i", url_rtsp_autenticada,
            "-fflags", "+genpts",
            "-c", "copy",
            "-t", "30",  # Tempo máximo de 30 segundos
            nome_arquivo
        ]

        # Inicia o processo do ffmpeg
        processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        tamanho_anterior = -1
        tempo_sem_mudanca = 0

        while True:
            time.sleep(3)  # Aumentei para 3s para dar mais tempo ao ffmpeg

            if os.path.exists(nome_arquivo):
                tamanho_atual = os.path.getsize(nome_arquivo)
                
                time.sleep(5)
                # Se o arquivo ainda for pequeno, aguarda mais um pouco antes de verificar mudanças
                if tamanho_atual < 30_000:
                    print(f"⚠ O arquivo {nome_arquivo} ainda está muito pequeno ({tamanho_atual} bytes). Esperando crescimento...")
                    continue

                # Se o tamanho não mudou, aumenta o tempo sem mudança
                if tamanho_atual == tamanho_anterior:
                    tempo_sem_mudanca += 3
                    print(f"⏳ O tamanho do arquivo {nome_arquivo} não mudou por {tempo_sem_mudanca}s... ({tamanho_atual} bytes)")

                    # **Mudança aqui**: Só encerra o ffmpeg se ele ainda estiver rodando após 12s sem mudanças.
                    if tempo_sem_mudanca >= 12 and processo.poll() is None:
                        print(f"⚠ Nenhuma mudança no arquivo {nome_arquivo} por 12s. Finalizando ffmpeg...")
                        processo.terminate()
                        time.sleep(3)  # Pequena pausa antes de recomeçar
                        break
                else:
                    tempo_sem_mudanca = 0  # Resetar a contagem se o tamanho mudar

                tamanho_anterior = tamanho_atual  # Atualiza o tamanho

            if processo.poll() is not None:  # Se ffmpeg terminar sozinho, não há necessidade de forçar o encerramento
                break

        # Espera um pouco para garantir que o processo realmente finalizou
        time.sleep(2)

        # Verifica se o arquivo foi baixado corretamente
        if os.path.exists(nome_arquivo):
            tamanho_final = os.path.getsize(nome_arquivo)
            print(f"✅ Download concluído: {nome_arquivo} ({tamanho_final} bytes)")

            if tamanho_final > 10_000:  # Se o arquivo for maior que 10 KB, considera sucesso
                sucesso = True
            else:
                print(f"❌ Erro: O vídeo {nome_arquivo} parece estar corrompido ou incompleto ({tamanho_final} bytes). Tentando novamente...")
        else:
            print(f"❌ Erro: O arquivo {nome_arquivo} não foi encontrado. Tentando novamente...")

    if not sucesso:
        print(f"❌ Falha ao baixar {nome_arquivo} após {max_tentativas} tentativas.")


def enviar_para_api(video_path, camera_ip):
    """Faz upload do vídeo processado para a API no formato correto."""
    try:
        with open(video_path, "rb") as f:
            response = requests.post(
                API_UPLOAD_URL,
                files={"file": f},
                data={
                    "cameraIP": camera_ip,
                    "dia": datetime.now().strftime("%Y-%m-%d"),
                    "horario": datetime.now().strftime("%H:%M")
                }
            )
        if response.status_code == 200:
            print(f"✅ Vídeo {video_path} enviado com sucesso!")
        else:
            print(f"❌ Erro ao enviar vídeo {video_path}. Código: {response.status_code}, Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao tentar enviar vídeo: {e}")


def listar_videos_disponiveis(ip, porta, usuario, senha, data_inicio, data_fim):
    """Consulta a câmera e retorna uma lista de vídeos disponíveis."""
    url_lista_videos = f"http://{ip}:{porta}/ISAPI/ContentMgmt/search"

    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
    <CMSearchDescription>
        <searchID>1</searchID>
        <trackList><trackID>101</trackID></trackList>
        <timeSpanList>
            <timeSpan>
                <startTime>{data_inicio}</startTime>
                <endTime>{data_fim}</endTime>
            </timeSpan>
        </timeSpanList>
        <maxResults>50</maxResults>
        <searchResultPostion>0</searchResultPostion>
        <metadataList>
            <metadataDescriptor>/recordType.meta.std-cgi.com</metadataDescriptor>
        </metadataList>
    </CMSearchDescription>"""

    headers = {
        "Content-Type": "application/xml",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.post(url_lista_videos, auth=HTTPDigestAuth(usuario, senha), headers=headers, data=xml_payload)

        if response.status_code == 200:
            videos = []
            for linha in response.text.splitlines():
                if "<playbackURI>" in linha:
                    url_video = linha.replace("<playbackURI>", "").replace("</playbackURI>", "").strip()
                    timestamp = url_video.split("starttime=")[1].split("&")[0]
                    videos.append((timestamp, url_video))

            return sorted(videos, key=lambda x: x[0])

        else:
            print(f"❌ Erro ao buscar vídeos na câmera {ip}. Código: {response.status_code}")
            return []

    except Exception as e:
        print(f"❌ Erro na requisição para a câmera {ip}: {e}")
        return []




def monitorar_cameras():
    """Loop contínuo para processar as câmeras e listar vídeos pendentes."""
    config = carregar_configuracoes()

    while True:
        videos_na_api = listar_videos_na_api()  # Obtemos os vídeos já enviados para a API

        for camera in config["cameras"]:
            pasta_destino = os.path.join(VIDEOS_DIR, camera['cliente'], camera['nome'], camera['ip'])
            os.makedirs(pasta_destino, exist_ok=True)

            # 🔍 Filtrar apenas os vídeos da câmera atual
            videos_camera_na_api = {video for video in videos_na_api if video.startswith(camera["nome"])}

            # Buscar vídeos disponíveis até 1 dia atrás
            data_inicio = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
            data_fim = datetime.now(timezone.utc).strftime("%Y-%m-%dT23:59:59Z")

            # Buscar vídeos na câmera
            videos_disponiveis = listar_videos_disponiveis(camera["ip"], camera["porta"], camera["usuario"], camera["senha"], data_inicio, data_fim)

            # 🔍 Filtrar vídeos que ainda não foram enviados
            novos_videos = []
            for timestamp, url_video in videos_disponiveis:
                video_nome = f"{camera['nome']}_{timestamp}.mp4"

                # Se o vídeo já está na API, ignoramos
                if video_nome in videos_camera_na_api:
                    continue

                novos_videos.append((timestamp, url_video))

            if novos_videos:
                print(f"📌 {len(novos_videos)} novos vídeos para {camera['nome']}. Baixando...")

            for timestamp, url_video in novos_videos:
                video_nome = f"{camera['nome']}_{timestamp}.mp4"
                video_path = os.path.join(pasta_destino, video_nome)

                print(f"📡 Baixando {video_nome}...")
                baixar_video_rtsp(url_video, video_path, camera["usuario"], camera["senha"])

                if esperar_liberacao_arquivo(video_path):
                    if os.path.exists(video_path) and os.path.getsize(video_path) > 10_000:
                        print(f"📤 Enviando {video_nome} para a API...")
                        enviar_para_api(video_path, camera["ip"])
                    else:
                        print(f"⚠ Vídeo {video_nome} inválido ou corrompido, ignorando...")

        print("⏳ Aguardando 20 segundos antes da próxima verificação...")
        time.sleep(20)






if __name__ == "__main__":
    monitorar_cameras()
