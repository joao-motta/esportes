from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import boto3

app = Flask(__name__)
CORS(app)

# Dados simulados
SALAS = {1: "Quadra Futebol", 2: "Ginásio Basquete"}
DIAS = {1: ["2025-03-15", "2025-03-16"], 2: ["2025-03-15"]}
HORARIOS = {(1, "2025-03-15"): ["10:00", "14:00"], (2, "2025-03-15"): ["15:00"]}
VIDEOS = {(1, "2025-03-15", "10:00"): [{"nome": "Treino.mp4", "url": "https://exemplo.com/video.mp4"}]}

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

# Rotas da API
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
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        s3_client.upload_fileobj(file, S3_BUCKET, file.filename, ExtraArgs={"ACL": "public-read"})
        video_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"
        return jsonify({"message": "File uploaded successfully!", "url": video_url}), 200

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

if __name__ == "__main__":
    app.run(debug=True)
