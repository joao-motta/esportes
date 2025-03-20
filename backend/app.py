from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import boto3

app = Flask(__name__)
CORS(app)

# Conectar ao banco de dados SQLite e criar a tabela uploads
def init_db():
    conn = sqlite3.connect("uploads.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            quadra TEXT NOT NULL,
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

# API para listar as clientes (agora baseado na tabela 'uploads')
@app.route("/api/clientes")
def get_clientes():
    try:
        conn = sqlite3.connect("uploads.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT clientes FROM uploads")
        clientes = cursor.fetchall()
        conn.close()

        result = [{"nome": row[0]} for row in clientes]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API para listar as salas (agora baseado na tabela 'uploads')
@app.route("/api/salas")
def get_salas():
    try:
        conn = sqlite3.connect("uploads.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT quadra FROM uploads")
        salas = cursor.fetchall()
        conn.close()

        result = [{"nome": row[0]} for row in salas]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API para listar os dias de uma sala
@app.route("/api/dias/<string:quadra>")
def get_dias(quadra):
    try:
        conn = sqlite3.connect("uploads.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT dia FROM uploads WHERE quadra = ?", (quadra,))
        dias = cursor.fetchall()
        conn.close()

        result = [{"dia": row[0]} for row in dias]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API para listar os horários de uma sala e dia
@app.route("/api/horarios/<string:quadra>/<string:dia>")
def get_horarios(quadra, dia):
    try:
        conn = sqlite3.connect("uploads.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT horario FROM uploads WHERE quadra = ? AND dia = ?", (quadra, dia))
        horarios = cursor.fetchall()
        conn.close()

        result = [{"horario": row[0]} for row in horarios]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API para upload de vídeo
@app.route("/upload", methods=["POST"])
def upload_file():
    # Validação dos parâmetros
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    if "cliente" not in request.form or "quadra" not in request.form or "cameraIP" not in request.form or "dia" not in request.form or "horario" not in request.form:
        return jsonify({"error": "Missing required parameters (cliente, quadra, cameraIP, dia, horario)"}), 400

    file = request.files["file"]
    cliente = request.form["cliente"]
    quadra = request.form["quadra"]
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
        conn = sqlite3.connect("uploads.db")
        cursor = conn.cursor()

        # Inserir os dados do upload diretamente na tabela uploads
        cursor.execute("INSERT INTO uploads (cliente, quadra, cameraIP, dia, horario, video_url) VALUES (?, ?, ?, ?, ?, ?)",
                       (cliente, quadra, cameraIP, dia, horario, video_url))
        conn.commit()
        conn.close()

        # Resposta com sucesso
        return jsonify({
            "message": "File uploaded successfully!",
            "url": video_url,
            "cliente": cliente,
            "quadra": quadra,
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
    cliente = request.args.get("cliente")
    quadra = request.args.get("quadra")
    cameraIP = request.args.get("cameraIP")
    dia = request.args.get("dia")
    horario = request.args.get("horario")
    
    try:
        conn = sqlite3.connect("uploads.db")
        cursor = conn.cursor()
        
        query = "SELECT * FROM uploads WHERE 1=1"
        params = []
        
        if cliente:
            query += " AND cliente = ?"
            params.append(cliente)
        if quadra:
            query += " AND quadra = ?"
            params.append(quadra)
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
            {"id": row[0], "cliente": row[1], "quadra": row[2], "cameraIP": row[3], "dia": row[4], "horario": row[5], "video_url": row[6]}
            for row in uploads
        ]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
