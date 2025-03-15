from flask_openapi3 import OpenAPI, Info, Tag
from flask import Flask, request, send_from_directory, redirect, jsonify
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, Documento
from logger import logger
from schemas import *
from flask_cors import CORS

import os
import boto3

app = Flask(__name__)

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)


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

if __name__ == "__main__":
    app.run(debug=True)

# Configuração da AWS
S3_BUCKET = "video-esporte"  # Substitua pelo nome do seu bucket
S3_REGION = "us-east-2"  # Substitua pela sua região da AWS
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

# Inicializa o cliente do S3
s3_client = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

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

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/list_videos")
def list_videos():
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        files = [obj["Key"] for obj in response.get("Contents", [])]
        return jsonify({"videos": files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500