import customtkinter as ctk
from tkinter import filedialog, messagebox
import requests
import os
from PIL import Image

SERVER_URL = "http://127.0.0.1:5000/upload"

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

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.attributes('-fullscreen', True)  # Tela cheia

def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)
    root.destroy()

root.bind("<Escape>", exit_fullscreen)


# Change image paths to use client directory
img_path = os.path.join("client", "upload.png")
img = Image.open(img_path)
img = img.resize((120, 120), Image.LANCZOS)
photo = ctk.CTkImage(light_image=img, size=(120, 120))

label = ctk.CTkLabel(
    root,
    text="Selecione um vídeo para enviar:",
    font=("Times New Roman", 30, "bold"),
    anchor="w", justify="left",
    fg_color="transparent"
)
label.pack(pady=(250, 1), anchor="w", padx=500)  # (topo, entre label e botão)

btn = ctk.CTkButton(
    root,
    text="Clique para enviar vídeo",
    image=photo,
    command=upload_video,
    width=900,
    height=200,
    fg_color="#FFFFFF",
    corner_radius=30,
    font=("Arial", 24, "bold"),
    border_width=2,
    border_color="#94E4FF",
    compound="top",  # imagem acima do texto
    
   
)
btn.pack(pady=(100, 200))  # (entre label e botão, depois espaço abaixo)



# Update background image path
bg_img_path = os.path.join("client", "filme.png")
if os.path.exists(bg_img_path):
    desired_width = 2400
    desired_height = 2000
    bg_img = Image.open(bg_img_path)
    bg_img = bg_img.resize((desired_width, desired_height), Image.LANCZOS)
    bg_photo = ctk.CTkImage(light_image=bg_img, size=(desired_width, desired_height))
    bg_label = ctk.CTkLabel(root, image=bg_photo, text="")
    # Mova a imagem mais para a direita ajustando relx (ex: 0.7)
    bg_label.place(relx=0.6, rely=0.5, anchor="center")
    bg_label.lower()


# Update corner image path
corner_img_path = os.path.join("client", "cavaloo.png")
if os.path.exists(corner_img_path):
    corner_img = Image.open(corner_img_path)
    corner_img = corner_img.resize((250, 250), Image.LANCZOS)
    corner_photo = ctk.CTkImage(light_image=corner_img, size=(250, 250))
    corner_label = ctk.CTkLabel(root, image=corner_photo, text="")
    corner_label.place(relx=0.0, rely=1.0, anchor="sw")
    

root.mainloop()
