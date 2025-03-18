import json
import os
import requests
from datetime import datetime

def criar_configuracao_cameras(arquivo_json="config_cameras.json"):
    """
    Cria um arquivo JSON com as configurações das câmeras a serem processadas e faz upload para a API.
    """
    cameras = [
        {
            "cliente": "Academia XYZ",
            "nome": "QuadraTenis1",
            "ip": "10.0.0.25",
            "porta": "80",
            "usuario": "admin",
            "senha": "Loja2010@",
            "logos": [],
            "data_adicao": datetime.now().strftime("%d-%m-%Y")
        },
                {
            "cliente": "Academia XYZ",
            "nome": "QuadraFutebol1",
            "ip": "10.0.0.25",
            "porta": "80",
            "usuario": "admin",
            "senha": "Loja2010@",
            "logos": [],
            "data_adicao": datetime.now().strftime("%d-%m-%Y")
        }

    ]
    
    # Gerar automaticamente o caminho da pasta_destino
    for camera in cameras:
        camera["pasta_destino"] = f"videos/{camera['cliente']}/{camera['nome']}/{camera['ip']}"
    
    config = {"cameras": cameras}
    
    # Salva o JSON no arquivo
    with open(arquivo_json, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    
    print(f"✅ Arquivo de configuração '{arquivo_json}' criado com sucesso!")
    
    # Enviar para a API
    try:
        with open(arquivo_json, "rb") as f:
            response = requests.post(
                "http://18.219.146.25:5000/upload",
                files={"file": (arquivo_json, f, "application/json")},
                data={
                    "cameraIP": "config_file",
                    "dia": datetime.now().strftime("%Y-%m-%d"),
                    "horario": datetime.now().strftime("%H:%M")
                }
            )
        
        if response.status_code == 200:
            print("✅ Configuração enviada com sucesso para a API!")
        else:
            print(f"❌ Erro ao enviar configuração. Código: {response.status_code}, Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao tentar enviar a configuração: {e}")

if __name__ == "__main__":
    criar_configuracao_cameras()
