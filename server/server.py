import os
import uuid
import json
import sqlite3
import cv2
import datetime
import numpy as np
import socket
from flask import Flask, request, render_template, send_from_directory, url_for

# Move BASE_DIR definition and update static folder config
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

app = Flask(__name__, 
    static_folder=BASE_DIR,  # Define pasta raiz como static
    static_url_path='/static'  # URL prefix para arquivos estáticos
)

DB = "videos.db"

# Função para obter o IP local da máquina
def get_local_ip():
    try:
        # Conecta a um endereço externo para descobrir o IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

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
def extract_thumbnail(video_path, thumb_path, filter_name=None):
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    if success:
        if filter_name:
            frame = apply_filter(frame, filter_name)
        cv2.imwrite(thumb_path, frame)
    cap.release()
    return success

# --- Função para aplicar filtros ---
def apply_filter(frame, filter_name):
    if filter_name == 'gray':
        return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    elif filter_name == 'clahe':
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl,a,b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return frame

def process_video(input_path, output_path, filter_name):
    # Primeiro salva com codec básico em arquivo temporário
    temp_output = output_path + '.temp.avi'
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    out = cv2.VideoWriter(temp_output, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        processed = apply_filter(frame, filter_name)
        out.write(processed)
        
    cap.release()
    out.release()

    # Converte para MP4 com H.264 usando FFMPEG
    import subprocess
    try:
        subprocess.run([
            'ffmpeg', '-y',  # Sobrescreve arquivo existente
            '-i', temp_output,  # Arquivo de entrada
            '-c:v', 'libx264',  # Codec H.264
            '-preset', 'medium',  # Preset de compressão
            '-crf', '23',  # Qualidade (menor = melhor)
            '-pix_fmt', 'yuv420p',  # Formato de pixel compatível
            output_path  # Arquivo de saída
        ], check=True)
    finally:
        # Limpa arquivo temporário
        if os.path.exists(temp_output):
            os.remove(temp_output)

# --- Upload ---
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("video")
    if not file:
        return "Nenhum arquivo enviado", 400
    
    uid = str(uuid.uuid4())
    today = datetime.date.today()
    save_dir = os.path.join(MEDIA_DIR, "videos", f"{today:%Y/%m/%d}", uid)
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

# --- Aplicar filtro ---
@app.route("/apply_filter/<video_id>/<filter_name>")
def apply_filter_route(video_id, filter_name):
    if filter_name not in ['gray', 'clahe']:
        return "Filtro inválido", 400
        
    with sqlite3.connect(DB) as conn:
        # Busca vídeo original com colunas específicas
        video = conn.execute("""
            SELECT id, original_name, path_original, duration_sec, fps, 
                   width, height, size_bytes 
            FROM videos WHERE id=?""", (video_id,)).fetchone()
        if not video:
            return "Vídeo não encontrado", 404
            
    # Usa o mesmo diretório base do vídeo original
    original_path = video[2]  # path_original é o índice 2 agora
    base_dir = os.path.dirname(os.path.dirname(original_path))
    processed_dir = os.path.join(base_dir, "processed")
    
    os.makedirs(processed_dir, exist_ok=True)
    
    try:
        # Processa o vídeo no diretório processed
        output_path = os.path.join(processed_dir, f"video_{filter_name}.mp4")
        process_video(original_path, output_path, filter_name)
        
        # Gera thumbnail com o filtro aplicado
        thumb_path = os.path.join(base_dir, "thumbs", f"thumb_{filter_name}.jpg")
        extract_thumbnail(output_path, thumb_path, filter_name)
        
        # Insere no banco
        with sqlite3.connect(DB) as conn:
            conn.execute("""
            INSERT INTO videos (id, original_name, original_ext, mime_type, size_bytes,
                              duration_sec, fps, width, height, filter, original_video_id,
                              path_original, path_processed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), f"{video[1]}_{filter_name}", "mp4", "video/mp4",
                  os.path.getsize(output_path), video[3], video[4], video[5], 
                  video[6], filter_name, video_id, output_path, processed_dir))
                  
        return {"status": "processed", "filter": filter_name}
        
    except Exception as e:
        print(f"Error processing video: {str(e)}")  # Debug log
        return f"Erro ao processar vídeo: {str(e)}", 500

# --- Galeria ---
@app.route("/")
def gallery():
    with sqlite3.connect(DB) as conn:
        rows = conn.execute("""
            SELECT id, original_name, path_original, filter 
            FROM videos ORDER BY created_at DESC""").fetchall()

    videos = []
    for r in rows:
        uid, name, path_orig, filter_name = r
        video_dir = os.path.dirname(os.path.dirname(path_orig))
        
        # Ajusta os caminhos para usar paths relativos ao BASE_DIR
        video_path = os.path.relpath(path_orig, BASE_DIR)
        
        # Define thumb path based on filter
        if filter_name:
            thumb_name = f"thumb_{filter_name}.jpg"
        else:
            thumb_name = "thumb.jpg"
        
        thumb_dir = os.path.join(os.path.dirname(os.path.dirname(path_orig)), "thumbs")
        thumb_path = os.path.join(os.path.relpath(thumb_dir, BASE_DIR), thumb_name)
        
        # Adiciona nome do filtro ao título se existir
        display_name = f"{name} ({filter_name})" if filter_name else name
        videos.append((uid, display_name, video_path, thumb_path))

    return render_template("gallery.html", videos=videos)

# Rota para servir arquivos de mídia
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
    # Configurações para executar na rede local
    HOST = "0.0.0.0"  # Aceita conexões de qualquer IP
    PORT = 5000       # Porta padrão do Flask
    
    # Obtém o IP local da máquina
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("🎬 SERVIDOR DE VÍDEOS INICIADO")
    print("=" * 60)
    print(f"📱 Acesso Local:      http://localhost:{PORT}")
    print(f"🌐 Acesso na Rede:    http://{local_ip}:{PORT}")
    print("=" * 60)
    print("💡 Para acessar de outros computadores na rede:")
    print(f"   Digite no navegador: http://{local_ip}:{PORT}")
    print("=" * 60)
    print("🔥 Servidor rodando... Pressione Ctrl+C para parar")
    print("=" * 60)
    
    # Inicia o servidor Flask
    app.run(
        host=HOST,
        port=PORT,
        debug=True,
        use_reloader=False  # Evita reinicializar duas vezes no modo debug
    )