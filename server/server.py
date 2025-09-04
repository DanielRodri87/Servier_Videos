import os
import uuid
import json
import sqlite3
import cv2
import datetime
from flask import Flask, request, render_template, send_from_directory, url_for

# Move BASE_DIR definition and creation to top
BASE_DIR = os.path.abspath("media")
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

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

# --- Função para extrair o primeiro frame ---
def extract_thumbnail(video_path, thumb_path):
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    if success:
        cv2.imwrite(thumb_path, frame)
    cap.release()
    return success

# --- Upload ---
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("video")
    if not file:
        return "Nenhum arquivo enviado", 400
    
    uid = str(uuid.uuid4())
    today = datetime.date.today()
    save_dir = os.path.join(BASE_DIR, "videos", f"{today:%Y/%m/%d}", uid)
    original_dir = os.path.join(save_dir, "original")
    processed_dir = os.path.join(save_dir, "processed")
    thumbs_dir = os.path.join(save_dir, "thumbs")

    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(thumbs_dir, exist_ok=True)

    # salva original
    ext = file.filename.rsplit(".", 1)[-1].lower()
    orig_path = os.path.join(original_dir, f"video.{ext}")
    file.save(orig_path)

    # metadados
    size_bytes = os.path.getsize(orig_path)
    duration, fps, width, height = extract_metadata(orig_path)

    # extrai thumb
    thumb_path = os.path.join(thumbs_dir, "thumb.jpg")
    extract_thumbnail(orig_path, thumb_path)

    # insere no banco
    with sqlite3.connect(DB) as conn:
        conn.execute("""
        INSERT INTO videos (id, original_name, original_ext, mime_type, size_bytes,
                            duration_sec, fps, width, height, path_original, path_processed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (uid, file.filename, ext, file.mimetype, size_bytes,
              duration, fps, width, height, orig_path, processed_dir))

    # meta.json
    meta = {
        "id": uid,
        "original_name": file.filename,
        "ext": ext,
        "size_bytes": size_bytes,
        "duration_sec": duration,
        "fps": fps,
        "width": width,
        "height": height,
        "thumb": os.path.relpath(thumb_path, BASE_DIR).replace("\\","/")
    }
    with open(os.path.join(save_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=4)

    return {"id": uid, "status": "uploaded", "thumb": meta["thumb"]}

# --- Galeria ---
@app.route("/")
def gallery():
    with sqlite3.connect(DB) as conn:
        rows = conn.execute("SELECT id, original_name, path_original FROM videos").fetchall()

    videos = []
    for r in rows:
        uid, name, path_orig = r
        # Use the same path structure as in meta.json
        base_path = f"videos/{datetime.date.today():%Y/%m/%d}/{uid}"
        video_path = f"{base_path}/original/video.{os.path.splitext(name)[1]}"
        thumb_path = f"{base_path}/thumbs/thumb.jpg"
        videos.append((uid, name, video_path, thumb_path))

    return render_template("gallery.html", videos=videos)

# --- Servir arquivos ---
@app.route("/media/<path:filename>")
def media(filename):
    full_path = os.path.join(BASE_DIR, filename)
    directory = os.path.dirname(full_path)
    filename = os.path.basename(full_path)
    
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")  # Debug log
        return f"File not found: {filename}", 404
        
    return send_from_directory(directory, filename)

if __name__ == "__main__":
    app.run(debug=True)
