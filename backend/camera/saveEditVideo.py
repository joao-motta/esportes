import os
import json
import requests
import time
import subprocess
import signal
import logging
import numpy as np
import cv2
import argparse
from datetime import datetime, timezone, timedelta
from requests.auth import HTTPDigestAuth


CONFIG_FILE = "config_cameras.json"
VIDEOS_DIR = "videos"
VIDEOS_BAIXADOS_FILE = "videos_baixados.json"
API_BASE_URL = "http://3.141.32.43:5000"
VIDEOS_DIR = "videos"


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

def marcar_video_baixado(video_original, video_final):
    """Marca um vídeo como baixado, registrando tanto o nome original quanto o processado."""
    videos_baixados = carregar_videos_baixados()
    videos_baixados.add(video_original)
    videos_baixados.add(video_final)
    salvar_videos_baixados(videos_baixados)


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
    API_LISTAR_URL = "http://3.141.32.43:5000/listavideos"

    try:
        response = requests.get(API_LISTAR_URL)
        print(f"🔍 Resposta bruta da API: {response.text}")  # Debug da resposta
        if response.status_code == 200:
            try:
                videos_api = response.json()
                print(f"📄 JSON recebido: {videos_api}")  # Debug do JSON

                if isinstance(videos_api, list):  # API retorna uma lista de dicionários
                    return {
                        video["video_url"].split("/")[-1]  # Obtém apenas o nome do arquivo
                        for video in videos_api
                        if "video_url" in video and video["video_url"].endswith(".mp4")
                    }
                else:
                    print("⚠ Estrutura do JSON inesperada. Esperado uma lista de vídeos.")
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

#SEGUNDA PARTE

def baixar_video_rtsp_ffmpeg(url_rtsp, nome_arquivo, usuario, senha):
    """Baixa um vídeo via RTSP usando ffmpeg, garantindo que o arquivo cresça corretamente."""
    url_rtsp_autenticada = url_rtsp.replace("rtsp://", f"rtsp://{usuario}:{senha}@")
    comando = [
        "ffmpeg", "-rtsp_transport", "tcp",
        "-i", url_rtsp_autenticada,
        "-fflags", "+genpts",
        "-c", "copy",
        "-t", "30",
        nome_arquivo
    ]

    processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    tamanho_anterior = -1
    tempo_sem_mudanca = 0

    while True:
        time.sleep(3)  # Checa a cada 3 segundos
        if os.path.exists(nome_arquivo):
            tamanho_atual = os.path.getsize(nome_arquivo)
            if tamanho_atual > 300_000:  # Só começa a verificar se o arquivo tem pelo menos 300 KB
                if tamanho_atual == tamanho_anterior:
                    tempo_sem_mudanca += 3
                    print(f"⏳ Tamanho do arquivo {nome_arquivo} não mudou por {tempo_sem_mudanca}s ({tamanho_atual} bytes)")
                    if tempo_sem_mudanca >= 12:  # Se por 12 segundos o tamanho não mudar, finaliza o ffmpeg
                        print(f"⚠ Nenhuma mudança no arquivo {nome_arquivo} por 12s. Finalizando ffmpeg...")
                        processo.terminate()
                        time.sleep(2)
                        break
                else:
                    tempo_sem_mudanca = 0  # Reset se o tamanho mudar
                tamanho_anterior = tamanho_atual
        if processo.poll() is not None:  # Processo finalizou
            break
    time.sleep(2)  # Garante que o processo finalizou completamente

    if os.path.exists(nome_arquivo):
        tamanho_final = os.path.getsize(nome_arquivo)
        print(f"✅ Download concluído: {nome_arquivo} ({tamanho_final} bytes)")

        if tamanho_final > 3_145_728:  # Pelo menos 3MB
            return True
        else:
            print(f"❌ Erro: O vídeo {nome_arquivo} está corrompido ou muito pequeno ({tamanho_final} bytes).")
            os.remove(nome_arquivo)  # Apaga o arquivo corrompido
    else:
        print(f"❌ Erro: O arquivo {nome_arquivo} não foi encontrado.")

    return False

def baixar_video_rtsp_opencv(url_rtsp, nome_arquivo, usuario, senha, max_tentativas=3):
    """Baixa um vídeo via RTSP usando OpenCV e suporta autenticação."""
    url_rtsp_autenticada = url_rtsp.replace("rtsp://", f"rtsp://{usuario}:{senha}@")
    
    for tentativa in range(1, max_tentativas + 1):
        print(f"🎥 Tentativa {tentativa}/{max_tentativas} de baixar com OpenCV: {nome_arquivo}")

        cap = cv2.VideoCapture(url_rtsp_autenticada)
        if not cap.isOpened():
            print("❌ Erro ao abrir o stream RTSP. Verifique usuário/senha e permissões da câmera.")
            time.sleep(3)
            continue  # Tenta novamente
        
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 20  # Assume 20 FPS se não for detectado
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(nome_arquivo, fourcc, fps, (width, height))

        frame_count = 0
        while cap.isOpened() and frame_count < fps * 30:  # Captura até 30 segundos
            ret, frame = cap.read()
            if not ret:
                print("⚠ Stream interrompido inesperadamente. Tentando novamente...")
                break  # Sai do loop para tentar novamente
            
            out.write(frame)
            frame_count += 1
        
        cap.release()
        out.release()

        # Verifica se o vídeo tem pelo menos 5MB para ser considerado válido
        if os.path.exists(nome_arquivo):
            tamanho_final = os.path.getsize(nome_arquivo)
            if tamanho_final > 5_242_880:  # 5MB
                print(f"✅ Download com OpenCV concluído: {nome_arquivo} ({tamanho_final} bytes)")
                return True
            else:
                print(f"❌ Erro: O vídeo {nome_arquivo} é muito pequeno ({tamanho_final} bytes). Tentando novamente...")
                os.remove(nome_arquivo)

    print(f"❌ Falha ao baixar {nome_arquivo} com OpenCV após {max_tentativas} tentativas.")
    return False

def baixar_video_rtsp(url_rtsp, nome_arquivo, usuario, senha):
    """Tenta primeiro baixar o vídeo com OpenCV, e se falhar, tenta com ffmpeg."""
    
    print(f"📡 Tentando baixar primeiro com OpenCV: {nome_arquivo}...")
    
    if baixar_video_rtsp_opencv(url_rtsp, nome_arquivo, usuario, senha):
        print(f"✅ Sucesso: {nome_arquivo} baixado com OpenCV!")
        return True
    print(f"⚠ Falha com OpenCV. Tentando método alternativo com ffmpeg...")
    
    for tentativa in range(2):
        print(f"🔄 Tentativa {tentativa + 1} com ffmpeg para baixar {nome_arquivo}...")
        if baixar_video_rtsp_ffmpeg(url_rtsp, nome_arquivo, usuario, senha):
            print(f"✅ Sucesso: {nome_arquivo} baixado com ffmpeg!")
            return True
        time.sleep(2)

    print(f"❌ Erro: Nenhum método conseguiu baixar {nome_arquivo}. Excluindo arquivo corrompido...")
    
    if os.path.exists(nome_arquivo):
        os.remove(nome_arquivo)
        
    return False



def enviar_para_api(video_path, camera_ip, cliente, quadra):
    """Faz upload do vídeo processado para a nova API no formato correto."""
    API_UPLOAD_URL = "http://3.141.32.43:5000/upload"

    try:
        with open(video_path, "rb") as f:
            response = requests.post(
                API_UPLOAD_URL,
                files={"file": f},
                data={
                    "cliente": cliente,
                    "quadra": quadra,
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

# TERCEIRA PARTE

def buscar_url_logo(nome_arquivo):
    """Busca a URL do arquivo diretamente da listagem da API."""
    API_LISTAR_URL = f"{API_BASE_URL}/listavideos"
    try:
        response = requests.get(API_LISTAR_URL)
        if response.status_code == 200:
            arquivos = response.json()
            for item in arquivos:
                if "video_url" in item and item["video_url"].endswith(nome_arquivo):
                    return item["video_url"]
        else:
            print(f"❌ Erro ao consultar API. Código: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao consultar API: {e}")
    
    return None

def baixar_logo(nome_arquivo):
    """Baixa a logo usando a URL correta da listagem da API."""
    logo_path = f"logos/{nome_arquivo}"
    if os.path.exists(logo_path):
        return logo_path  # Já existe localmente

    url_logo = buscar_url_logo(nome_arquivo)
    if not url_logo:
        print(f"⚠ Logo '{nome_arquivo}' não encontrada na listagem da API.")
        return None

    print(f"🌐 Baixando logo via: {url_logo}")
    response = requests.get(url_logo, stream=True)
    if response.status_code == 200:
        os.makedirs("logos", exist_ok=True)
        with open(logo_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"✅ Logo '{nome_arquivo}' baixada com sucesso!")
        return logo_path
    else:
        print(f"❌ Falha ao baixar logo '{nome_arquivo}'. Código: {response.status_code}")
        return None

def adicionar_logos(video_path, logos):
    """
    Adiciona logos ao vídeo.
    - FastPlay.png deve ficar exatamente sobre a logo HIKVISION no canto superior direito.
    - Até 6 logos adicionais, posicionadas dinamicamente.
    """
    if not os.path.exists(video_path):
        print(f"❌ Erro: O vídeo {video_path} não foi encontrado.")
        return False

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Erro ao abrir vídeo para adicionar logos.")
        return False

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_output = video_path.replace(".mp4", "_temp.mp4")  # Arquivo temporário
    out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))

    logos_para_adicionar = []

    # 🔹 Ajuste para posicionar FastPlay exatamente sobre Hikvision
    fastplay_path = baixar_logo("FastPlay.png")
    if fastplay_path:
        logo = cv2.imread(fastplay_path, cv2.IMREAD_UNCHANGED)
        
        # 🔹 Aumentar a largura (esticar horizontalmente)
        logo = cv2.resize(logo, (270, 60), interpolation=cv2.INTER_LINEAR)  # Esticando mais
        
        fastplay_x = max(10, width - 375)  # Move mais para a esquerda
        fastplay_y = 25  # Pequeno ajuste para baixo

        print(f"FastPlay X final: {fastplay_x} (largura total do vídeo: {width})")  # Debug

        logos_para_adicionar.append((logo, (fastplay_x, fastplay_y)))

    else:
        print("⚠ FastPlay.png não encontrada.")

    # 🔹 Baixar e posicionar outras logos dinamicamente
    posicoes = [
        ("top_left", (10, 10)),
        ("top_center", (width // 2 - 75, 10)),
        ("bottom_left", (10, height - 80)),
        ("bottom_center", (width // 2 - 75, height - 80)),
        ("bottom_right", (width - 150, height - 80)),
        ("center", (width // 2 - 75, height // 2 - 40)),
    ]

    for idx, logo_nome in enumerate(logos[:6]):  # Máximo 6 logos
        logo_path = baixar_logo(logo_nome)
        if logo_path:
            logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
            logo = cv2.resize(logo, (200, 100), interpolation=cv2.INTER_AREA)  # Redimensiona
            _, pos = posicoes[idx]
            logos_para_adicionar.append((logo, pos))

    # 🔹 Processar os frames do vídeo e adicionar as logos
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        for logo, (x, y) in logos_para_adicionar:
            if logo is None:
                continue

            h, w = logo.shape[:2]
            if y + h > frame.shape[0] or x + w > frame.shape[1]:
                continue  # Evita erro de sobreposição fora da imagem

            if logo.shape[2] == 4:  # PNG com transparência
                overlay = frame[y:y+h, x:x+w]
                alpha = logo[:, :, 3] / 255.0
                for c in range(3):
                    overlay[:, :, c] = overlay[:, :, c] * (1 - alpha) + logo[:, :, c] * alpha
                frame[y:y+h, x:x+w] = overlay
            else:
                frame[y:y+h, x:x+w] = logo

        out.write(frame)

    cap.release()
    out.release()

    # Substituir o vídeo original pelo novo processado
    os.replace(temp_output, video_path)
    print(f"✅ Vídeo processado com sucesso: {video_path}")
    return True


def monitorar_cameras():
    """Loop contínuo para processar as câmeras e listar vídeos pendentes."""
    config = carregar_configuracoes()

    while True:
        videos_na_api = listar_videos_na_api()  # Obtém os vídeos já enviados para a API

        for camera in config["cameras"]:
            pasta_destino = os.path.join(VIDEOS_DIR, camera['cliente'], camera['nome'], camera['ip'])
            os.makedirs(pasta_destino, exist_ok=True)

            videos_camera_na_api = {video for video in videos_na_api if video.startswith(camera["nome"])}

            data_inicio = (datetime.now(timezone.utc) - timedelta(days=5).strftime("%Y-%m-%dT00:00:00Z"))
            data_fim = datetime.now(timezone.utc).strftime("%Y-%m-%dT23:59:59Z")

            videos_disponiveis = listar_videos_disponiveis(camera["ip"], camera["porta"], camera["usuario"], camera["senha"], data_inicio, data_fim)

            novos_videos = []
            for timestamp, url_video in videos_disponiveis:
                video_nome = f"{camera['nome']}_{timestamp}.mp4"

                if video_nome in videos_camera_na_api:
                    continue

                novos_videos.append((timestamp, url_video))

            if novos_videos:
                print(f"📌 {len(novos_videos)} novos vídeos para {camera['nome']}. Baixando...")

            for timestamp, url_video in novos_videos:
                video_nome = f"{camera['nome']}_{timestamp}.mp4"
                video_path = os.path.join(pasta_destino, video_nome)

                print(f"📡 Baixando {video_nome}...")
                sucesso = baixar_video_rtsp(url_video, video_path, camera["usuario"], camera["senha"])

                if sucesso:
                    if esperar_liberacao_arquivo(video_path):
                        if os.path.exists(video_path):
                            tamanho_final = os.path.getsize(video_path)
                            if tamanho_final > 3_145_728:  # Verifica se o vídeo tem pelo menos 3MB
                                print(f"🖼️ Adicionando logos ao vídeo {video_nome}...")
                                if adicionar_logos(video_path, camera.get("logos", [])):  # Passa a lista de logos corretamente
                                    print(f"✅ Vídeo processado com logos: {video_path}")
                                    # 🔹 **Marca o vídeo original como baixado, já que ele não muda de nome**
                                    marcar_video_baixado(video_nome, video_nome)
                                    print(f"📤 Enviando {video_path} para a API...")
                                    enviar_para_api(video_path, camera["ip"], camera["cliente"], camera["quadra"])
                                else:
                                    print(f"⚠ Erro ao processar logos para {video_nome}. Enviando vídeo original...")
                                    # 🔹 **Mesmo que a logo falhe, marcamos o vídeo original como baixado**
                                    marcar_video_baixado(video_nome, video_nome)
                                    enviar_para_api(video_path, camera["ip"], camera["cliente"], camera["quadra"])
                            else:
                                print(f"⚠ Vídeo {video_nome} inválido ou corrompido ({tamanho_final} bytes). Não será enviado.")
                        else:
                            print(f"⚠ Erro: {video_nome} não encontrado após download. Ignorando...")

        print("⏳ Aguardando 20 segundos antes da próxima verificação...")
        time.sleep(20)
        
if __name__ == "__main__":
    monitorar_cameras()
