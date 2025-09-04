import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import os

SERVER_URL = "http://127.0.0.1:5000/upload"  # URL do servidor Flask

def upload_video():
    filepath = filedialog.askopenfilename(
        title="Selecione um vídeo",
        filetypes=[("Vídeos", "*.mp4 *.avi *.mov *.mkv *.wmv")]
    )
    if not filepath:
        return
    
    try:
        with open(filepath, "rb") as f:
            files = {"video": (os.path.basename(filepath), f, "video/mp4")}
            response = requests.post(SERVER_URL, files=files)
        
        if response.status_code == 200:
            messagebox.showinfo("Sucesso", f"Upload concluído!\n{response.json()}")
        else:
            messagebox.showerror("Erro", f"Falha no upload: {response.text}")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

# Interface Tkinter
root = tk.Tk()
root.title("Cliente de Upload de Vídeos")

btn = tk.Button(root, text="Selecionar e enviar vídeo", command=upload_video, width=40, height=3)
btn.pack(pady=20)

root.mainloop()
