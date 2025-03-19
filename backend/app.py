from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import boto3

app = Flask(__name__)
CORS(app)

# Estrutura de dados simulados corrigida
SALAS = [
    {"id": 1, "nome": "Quadra Futebol", "imagem": "https://via.placeholder.com/150"},
    {"id": 2, "nome": "Ginásio Basquete", "imagem": "https://via.placeholder.com/150"}
]

DIAS = {
    1: ["2025-03-15", "2025-03-16"],
    2: ["2025-03-15"]
}

HORARIOS = {
    (1, "2025-03-15"): ["10:00", "14:00"],
    (2, "2025-03-15"): ["15:00"]
}

VIDEOS = {
    (1, "2025-03-15", "10:00"): [
        {
            "nome": "Treino Futebol",
            "thumbnail": "https://via.placeholder.com/150",
            "url": "https://exemplo.com/video1.mp4"
        }
    ],
    (2, "2025-03-15", "15:00"): [
        {
            "nome": "Treino Basquete",
            "thumbnail": "https://via.placeholder.com/150",
            "url": "https://exemplo.com/video2.mp4"
        }
    ]
}

# Conectar ao banco de dados SQLite e criar tabela se não existir
def init_db():
    conn = sqlite3.connect("uploads.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cameraIP TEXT NOT NULL,
            dia TEXT NOT NULL,
            horario TEXT NOT NULL,
            video_url TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Inicializa o banco de dados


# Configuração da AWS S3
S3_BUCKET = "video-esporte"
S3_REGION = "us-east-2"
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

s3_client = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

# Rotas da API corrigidas
@app.route("/api/salas")
def get_salas():
    return jsonify(SALAS)

@app.route("/api/dias/<int:sala_id>")
def get_dias(sala_id):
    return jsonify(DIAS.get(sala_id, []))

@app.route("/api/horarios/<int:sala_id>/<dia>")
def get_horarios(sala_id, dia):
    return jsonify(HORARIOS.get((sala_id, dia), []))

@app.route("/api/videos/<int:sala_id>/<dia>/<horario>")
def get_videos(sala_id, dia, horario):
    return jsonify(VIDEOS.get((sala_id, dia, horario), []))

@app.route("/upload", methods=["POST"])
def upload_file():
    # Validação dos parâmetros
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    if "cameraIP" not in request.form or "dia" not in request.form or "horario" not in request.form:
        return jsonify({"error": "Missing required parameters (cameraIP, dia, horario)"}), 400

    file = request.files["file"]
    cameraIP = request.form["cameraIP"]
    dia = request.form["dia"]
    horario = request.form["horario"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Envia o arquivo para o S3
        s3_client.upload_fileobj(file, S3_BUCKET, file.filename, ExtraArgs={"ACL": "public-read"})
        video_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"
        
        # Salvar no banco SQLite
        conn = sqlite3.connect("uploads.db")  # Certifique-se de que esse é o nome correto do arquivo
        cursor = conn.cursor()

        # Criar a tabela se não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cameraIP TEXT,
                dia TEXT,
                horario TEXT,
                video_url TEXT
            )
        ''')
        conn.commit()

        # Inserir dados
        cursor.execute("INSERT INTO uploads (cameraIP, dia, horario, video_url) VALUES (?, ?, ?, ?)",
                       (cameraIP, dia, horario, video_url))
        conn.commit()
        conn.close()

        # Resposta com sucesso
        return jsonify({
            "message": "File uploaded successfully!",
            "url": video_url,
            "cameraIP": cameraIP,
            "dia": dia,
            "horario": horario
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/list_videos")
def list_videos():
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        files = [obj["Key"] for obj in response.get("Contents", [])]
        return jsonify({"videos": files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/listavideos", methods=["GET"])
def get_uploads():
    cameraIP = request.args.get("cameraIP")
    dia = request.args.get("dia")
    horario = request.args.get("horario")
    
    try:
        conn = sqlite3.connect("uploads.db")
        cursor = conn.cursor()
        
        query = "SELECT * FROM uploads WHERE 1=1"
        params = []
        
        if cameraIP:
            query += " AND cameraIP = ?"
            params.append(cameraIP)
        if dia:
            query += " AND dia = ?"
            params.append(dia)
        if horario:
            query += " AND horario = ?"
            params.append(horario)
        
        cursor.execute(query, params)
        uploads = cursor.fetchall()
        conn.close()
        
        result = [
            {"id": row[0], "cameraIP": row[1], "dia": row[2], "horario": row[3], "video_url": row[4]}
            for row in uploads
        ]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
      

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)