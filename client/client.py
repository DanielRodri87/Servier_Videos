import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import os
from PIL import Image, ImageTk, ImageDraw
import io

SERVER_URL = "http://127.0.0.1:5000/upload"  # URL do servidor Flask

class VideoUploadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cliente de Upload de Vídeos")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Centralizar a janela
        self.center_window()
        
        # Criar o layout principal
        self.create_widgets()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_horse_image(self):
        """Criar uma imagem simples do cavalinho com câmera"""
        img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Corpo do cavalo (marrom)
        draw.ellipse([30, 60, 90, 100], fill="#8B4513", outline="#654321", width=2)
        
        # Cabeça
        draw.ellipse([20, 30, 60, 70], fill="#8B4513", outline="#654321", width=2)
        
        # Orelhas
        draw.ellipse([25, 25, 35, 45], fill="#8B4513", outline="#654321")
        draw.ellipse([45, 25, 55, 45], fill="#8B4513", outline="#654321")
        
        # Olhos (com óculos)
        draw.ellipse([25, 40, 35, 50], fill="white")
        draw.ellipse([45, 40, 55, 50], fill="white")
        draw.ellipse([27, 42, 33, 48], fill="black")
        draw.ellipse([47, 42, 53, 48], fill="black")
        
        # Óculos
        draw.ellipse([22, 37, 38, 53], outline="black", width=2)
        draw.ellipse([42, 37, 58, 53], outline="black", width=2)
        draw.line([38, 45, 42, 45], fill="black", width=2)
        
        # Focinho
        draw.ellipse([35, 55, 45, 65], fill="#A0522D", outline="#654321")
        
        # Pernas
        draw.rectangle([35, 100, 40, 115], fill="#8B4513", outline="#654321")
        draw.rectangle([55, 100, 60, 115], fill="#8B4513", outline="#654321")
        draw.rectangle([65, 100, 70, 115], fill="#8B4513", outline="#654321")
        draw.rectangle([75, 100, 80, 115], fill="#8B4513", outline="#654321")
        
        # Câmera
        draw.rectangle([70, 70, 95, 85], fill="black", outline="gray", width=1)
        draw.circle([82, 77], 5, fill="gray", outline="black")
        draw.rectangle([95, 73, 100, 80], fill="black")
        
        return img
    
    def create_film_strip_decoration(self, canvas, x, y, width, height):
        """Criar decoração de filme"""
        # Desenhar fita de filme
        canvas.create_rectangle(x, y, x + width, y + height, 
                              fill="#87CEEB", outline="#5F9EA0", width=2)
        
        # Furos da fita
        hole_size = 8
        spacing = 15
        for i in range(0, width, spacing):
            if i + hole_size < width:
                canvas.create_rectangle(x + i + 3, y + 2, 
                                      x + i + 3 + hole_size, y + 2 + hole_size,
                                      fill="white", outline="#5F9EA0")
                canvas.create_rectangle(x + i + 3, y + height - hole_size - 2, 
                                      x + i + 3 + hole_size, y + height - 2,
                                      fill="white", outline="#5F9EA0")
    
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Canvas para decorações
        decoration_canvas = tk.Canvas(main_frame, bg="#f0f0f0", height=150, highlightthickness=0)
        decoration_canvas.pack(fill=tk.X, pady=(0, 20))
        
        # Decorações de filme
        self.create_film_strip_decoration(decoration_canvas, 400, 20, 200, 30)
        self.create_film_strip_decoration(decoration_canvas, 450, 80, 300, 25)
        self.create_film_strip_decoration(decoration_canvas, 350, 120, 150, 20)
        
        # Título
        title_label = tk.Label(main_frame, text="FAÇA UPLOAD DO VÍDEO", 
                             font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#333")
        title_label.pack(pady=(0, 30))
        
        # Frame para o conteúdo central
        content_frame = tk.Frame(main_frame, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame esquerdo para o cavalinho
        left_frame = tk.Frame(content_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Cavalinho
        try:
            horse_img = self.create_horse_image()
            horse_photo = ImageTk.PhotoImage(horse_img)
            horse_label = tk.Label(left_frame, image=horse_photo, bg="#f0f0f0")
            horse_label.image = horse_photo  # Manter referência
            horse_label.pack(pady=(50, 0))
        except:
            # Fallback se PIL não estiver disponível
            horse_label = tk.Label(left_frame, text="🐴📹", font=("Arial", 48), bg="#f0f0f0")
            horse_label.pack(pady=(50, 0))
        
        # Frame direito para a área de upload
        right_frame = tk.Frame(content_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Área de upload (caixa pontilhada)
        upload_frame = tk.Frame(right_frame, bg="#e6f7ff", relief=tk.SOLID, bd=1)
        upload_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 30))
        
        # Canvas para a borda pontilhada
        upload_canvas = tk.Canvas(upload_frame, bg="#e6f7ff", highlightthickness=0)
        upload_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Desenhar borda pontilhada
        upload_canvas.create_rectangle(2, 2, 398, 198, outline="#87CEEB", 
                                     width=2, dash=(5, 5))
        
        # Ícone de nuvem (usando texto Unicode)
        cloud_label = tk.Label(upload_canvas, text="☁", font=("Arial", 48), 
                             bg="#e6f7ff", fg="#87CEEB")
        cloud_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
        
        # Seta para cima
        arrow_label = tk.Label(upload_canvas, text="↑", font=("Arial", 24), 
                             bg="#e6f7ff", fg="#87CEEB")
        arrow_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
        
        # Texto de instrução
        instruction_label = tk.Label(upload_canvas, text="Clique aqui para escolher um arquivo", 
                                   font=("Arial", 12), bg="#e6f7ff", fg="#333")
        instruction_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        
        # Bind click na área de upload
        def on_upload_click(event=None):
            self.upload_video()
        
        upload_canvas.bind("<Button-1>", on_upload_click)
        cloud_label.bind("<Button-1>", on_upload_click)
        arrow_label.bind("<Button-1>", on_upload_click)
        instruction_label.bind("<Button-1>", on_upload_click)
        
        # Frame para botões
        button_frame = tk.Frame(right_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botão Histórico
        history_btn = tk.Button(button_frame, text="HISTÓRICO", 
                              font=("Arial", 10), bg="white", fg="#666",
                              relief=tk.SOLID, bd=1, padx=20, pady=8,
                              command=self.show_history)
        history_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Enviar
        send_btn = tk.Button(button_frame, text="ENVIAR", 
                           font=("Arial", 10), bg="#87CEEB", fg="white",
                           relief=tk.SOLID, bd=1, padx=30, pady=8,
                           command=self.upload_video)
        send_btn.pack(side=tk.RIGHT)
        
        # Decorações de filme no final
        bottom_canvas = tk.Canvas(main_frame, bg="#f0f0f0", height=80, highlightthickness=0)
        bottom_canvas.pack(fill=tk.X, pady=(20, 0))
        
        self.create_film_strip_decoration(bottom_canvas, 100, 10, 180, 25)
        self.create_film_strip_decoration(bottom_canvas, 300, 40, 250, 30)
    
    def upload_video(self):
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
    
    def show_history(self):
        messagebox.showinfo("Histórico", "Funcionalidade de histórico em desenvolvimento!")

# Interface Tkinter
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoUploadApp(root)
    root.mainloop()