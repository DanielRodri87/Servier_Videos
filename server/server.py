import os
import uuid
import json
import sqlite3
import cv2
import datetime
from flask import Flask, request, render_template, send_from_directory

BASE_DIR = "media"
DB = "videos.db"

app = Flask(__name__)

# --- Função para extrair metadados ---
def extract_metadata(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frames / fps if fps > 0 else 0
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return duration, fps, width, height

# --- Upload ---
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("video")
    if not file:
        return "Nenhum arquivo enviado", 400
    
    uid = str(uuid.uuid4())
    today = datetime.date.today()
    save_dir = os.path.join(BASE_DIR, "videos", f"{today:%Y/%m/%d}", uid)
    os.makedirs(os.path.join(save_dir, "original"), exist_ok=True)
    os.makedirs(os.path.join(save_dir, "processed"), exist_ok=True)
    os.makedirs(os.path.join(save_dir, "thumbs"), exist_ok=True)

    # salva original
    ext = file.filename.rsplit(".", 1)[-1].lower()
    orig_path = os.path.join(save_dir, "original", f"video.{ext}")
    file.save(orig_path)

    # metadados
    size_bytes = os.path.getsize(orig_path)
    duration, fps, width, height = extract_metadata(orig_path)

    # insere no banco
    with sqlite3.connect(DB) as conn:
        conn.execute("""
        INSERT INTO videos (id, original_name, original_ext, mime_type, size_bytes,
                            duration_sec, fps, width, height, path_original)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (uid, file.filename, ext, file.mimetype, size_bytes,
              duration, fps, width, height, orig_path))

    # meta.json
    meta = {
        "id": uid,
        "original_name": file.filename,
        "ext": ext,
        "size_bytes": size_bytes,
        "duration_sec": duration,
        "fps": fps,
        "width": width,
        "height": height
    }
    with open(os.path.join(save_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=4)

    return {"id": uid, "status": "uploaded"}

# --- Galeria ---
@app.route("/gallery")
def gallery():
    with sqlite3.connect(DB) as conn:
        rows = conn.execute("SELECT id, original_name, path_original FROM videos").fetchall()
    return render_template("gallery.html", videos=rows)

# --- Servir arquivos ---
@app.route("/media/<path:filename>")
def media(filename):
    return send_from_directory(BASE_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
