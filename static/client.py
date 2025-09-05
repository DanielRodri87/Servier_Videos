import customtkinter as ctk
from tkinter import filedialog, messagebox
import requests
import os
from PIL import Image
import json

# Configurações padrão
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = "5000"
CONFIG_FILE = "server_config.json"

class VideoUploadClient:
    def __init__(self):
        self.server_ip = DEFAULT_IP
        self.server_port = DEFAULT_PORT
        self.server_url = ""
        
        # Carrega configurações salvas
        self.load_config()
        
        # Configura a interface
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.exit_fullscreen)
        
        self.setup_ui()
        
    def load_config(self):
        """Carrega configurações salvas do servidor"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.server_ip = config.get('ip', DEFAULT_IP)
                    self.server_port = config.get('port', DEFAULT_PORT)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
        
        self.update_server_url()
    
    def save_config(self):
        """Salva as configurações do servidor"""
        try:
            config = {
                'ip': self.server_ip,
                'port': self.server_port
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def update_server_url(self):
        """Atualiza a URL do servidor"""
        self.server_url = f"http://{self.server_ip}:{self.server_port}/upload"
    
    def show_server_config(self):
        """Mostra janela para configurar servidor"""
        config_window = ctk.CTkToplevel(self.root)
        config_window.title("Configuração do Servidor")
        config_window.geometry("500x350")  # Aumentei altura para o novo botão
        config_window.transient(self.root)
        
        # Centraliza a janela
        config_window.update_idletasks()
        x = (config_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (config_window.winfo_screenheight() // 2) - (350 // 2)
        config_window.geometry(f"500x350+{x}+{y}")
        
        # Força a janela a ser construída antes de tentar grab_set
        config_window.wait_visibility()
        config_window.grab_set()
        
        # Título
        title_label = ctk.CTkLabel(
            config_window,
            text="Configuração do Servidor",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20)
        
        # Frame para os campos
        frame = ctk.CTkFrame(config_window)
        frame.pack(pady=20, padx=40, fill="x")
        
        # IP e Porta
        ip_var = ctk.StringVar(value=self.server_ip)
        port_var = ctk.StringVar(value=self.server_port)
        
        ip_label = ctk.CTkLabel(frame, text="IP do Servidor:", font=("Arial", 14))
        ip_label.pack(pady=(20, 5))
        
        ip_entry = ctk.CTkEntry(
            frame, 
            placeholder_text="Ex: 192.168.1.100",
            font=("Arial", 12),
            width=300,
            textvariable=ip_var
        )
        ip_entry.pack(pady=(0, 10))
        
        port_label = ctk.CTkLabel(frame, text="Porta do Servidor:", font=("Arial", 14))
        port_label.pack(pady=(10, 5))
        
        port_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Ex: 5000", 
            font=("Arial", 12),
            width=300,
            textvariable=port_var
        )
        port_entry.pack(pady=(0, 20))
        
        # Display dos valores atuais
        current_values = ctk.CTkLabel(
            frame,
            text=f"Valores atuais - IP: {self.server_ip}, Porta: {self.server_port}",
            font=("Arial", 12),
            text_color="gray"
        )
        current_values.pack(pady=(0, 10))
        
        # Container para botões
        buttons_container = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_container.pack(fill="x", pady=(10, 0))
        
        # Botão confirmar
        confirm_btn = ctk.CTkButton(
            buttons_container,
            text="✅ Confirmar",
            command=lambda: confirm_values(),
            width=150,
            height=35,
            font=("Arial", 14, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        confirm_btn.pack(side="top", pady=5)
        
        def confirm_values():
            new_ip = ip_var.get().strip()
            new_port = port_var.get().strip()
            
            if not new_ip or not new_port:
                messagebox.showerror("Erro", "⚠️ Preencha IP e Porta!")
                return
                
            try:
                # Validação de IP e Porta aqui...
                self.server_ip = new_ip
                self.server_port = new_port
                self.update_server_url()
                self.update_status_label()
                current_values.configure(
                    text=f"Valores atuais - IP: {self.server_ip}, Porta: {self.server_port}"
                )
                messagebox.showinfo("Sucesso", "✅ Valores atualizados!")
            except Exception as e:
                messagebox.showerror("Erro", f"❌ Erro ao atualizar: {str(e)}")
        
        # Botão testar
        test_btn = ctk.CTkButton(
            buttons_container,
            text="🔍 Testar Conexão",
            command=test_connection,
            width=150,
            height=35,
            font=("Arial", 14, "bold"),
            fg_color="#e67e22",
            hover_color="#d35400"
        )
        test_btn.pack(side="top", pady=5)
        
        # Botão salvar e fechar
        save_btn = ctk.CTkButton(
            buttons_container,
            text="💾 Salvar e Fechar",
            command=save_and_close,
            width=150,
            height=35,
            font=("Arial", 14, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        save_btn.pack(side="top", pady=5)

        # Botões
        button_frame = ctk.CTkFrame(config_window, fg_color="transparent")
        button_frame.pack(pady=(20, 30), fill="x")
        
        def test_connection():
            """Testa a conexão com o servidor"""
            test_ip = ip_entry.get().strip()
            test_port = port_entry.get().strip()
            
            if not test_ip or not test_port:
                messagebox.showerror("Erro", "⚠️ Preencha IP e Porta!")
                return
            
            try:
                test_url = f"http://{test_ip}:{test_port}/"
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    messagebox.showinfo("Sucesso", "✅ Conexão com servidor OK!\n\nServidor respondeu corretamente.")
                else:
                    messagebox.showwarning("Aviso", f"⚠️ Servidor respondeu com código: {response.status_code}")
            except requests.exceptions.Timeout:
                messagebox.showerror("Erro de Conexão", f"⏰ Timeout na conexão!\n\nVerifique se o servidor está rodando.")
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Erro de Conexão", f"❌ Não foi possível conectar!\n\nVerifique:\n• IP e porta corretos\n• Servidor está rodando\n• Mesma rede")
            except Exception as e:
                messagebox.showerror("Erro", f"❌ Erro inesperado:\n{str(e)}")
        
        def save_and_close():
            """Salva configurações e fecha janela"""
            new_ip = ip_entry.get().strip()
            new_port = port_entry.get().strip()
            
            if not new_ip or not new_port:
                messagebox.showerror("Erro", "⚠️ Preencha IP e Porta!")
                return
            
            # Valida formato básico do IP
            try:
                parts = new_ip.split('.')
                if len(parts) != 4:
                    raise ValueError("IP deve ter 4 partes")
                for part in parts:
                    if not (0 <= int(part) <= 255):
                        raise ValueError("Partes do IP devem estar entre 0-255")
            except:
                messagebox.showerror("Erro", "⚠️ Formato de IP inválido!\n\nUse formato: xxx.xxx.xxx.xxx")
                return
            
            # Valida porta
            try:
                port_num = int(new_port)
                if not (1 <= port_num <= 65535):
                    raise ValueError("Porta deve estar entre 1-65535")
            except:
                messagebox.showerror("Erro", "⚠️ Porta inválida!\n\nUse um número entre 1 e 65535")
                return
            
            self.server_ip = new_ip
            self.server_port = new_port
            self.update_server_url()
            self.save_config()
            self.update_status_label()
            config_window.destroy()
            messagebox.showinfo("Sucesso", f"✅ Configurações salvas!\n\nNovo servidor: {new_ip}:{new_port}")
        
        # Foca no campo IP
        ip_entry.focus()
    
    def upload_video(self):
        """Faz upload do vídeo para o servidor"""
        filepath = filedialog.askopenfilename(
            title="Selecione um vídeo",
            filetypes=[("Vídeos", "*.mp4 *.avi *.mov *.mkv *.wmv")]
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, "rb") as f:
                files = {"video": (os.path.basename(filepath), f, "video/mp4")}
                response = requests.post(self.server_url, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                messagebox.showinfo("Sucesso", f"✅ Upload concluído!\nID: {result.get('id', 'N/A')}")
            else:
                messagebox.showerror("Erro", f"❌ Falha no upload: {response.text}")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Erro de Conexão", 
                               f"❌ Não foi possível conectar ao servidor!\n\n"
                               f"Verifique se:\n"
                               f"• O servidor está rodando\n"
                               f"• IP e porta estão corretos\n"
                               f"• Você está na mesma rede\n\n"
                               f"Servidor configurado: {self.server_url}")
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro inesperado: {str(e)}")
    
    def update_status_label(self):
        """Atualiza o label com status do servidor"""
        self.status_label.configure(text=f"Servidor: {self.server_ip}:{self.server_port}")
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Label principal
        label = ctk.CTkLabel(
            self.root,
            text="Selecione um vídeo para enviar:",
            font=("Times New Roman", 30, "bold"),
            anchor="w",
            justify="left",
            fg_color="transparent"
        )
        label.pack(pady=(200, 1), anchor="w", padx=500)
        
        # Status do servidor
        self.status_label = ctk.CTkLabel(
            self.root,
            text=f"Servidor: {self.server_ip}:{self.server_port}",
            font=("Arial", 16),
            fg_color="transparent"
        )
        self.status_label.pack(pady=(10, 20))
        
        # Botão de configuração do servidor
        config_btn = ctk.CTkButton(
            self.root,
            text="⚙️ Configurar Servidor",
            command=self.show_server_config,
            width=250,
            height=40,
            font=("Arial", 14),
            fg_color="#34495e",
            hover_color="#2c3e50"
        )
        config_btn.pack(pady=(0, 20))
        
        # Carrega imagem do botão principal
        try:
            img_path = os.path.join("client", "upload.png")
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((120, 120), Image.LANCZOS)
                photo = ctk.CTkImage(light_image=img, size=(120, 120))
            else:
                photo = None
        except:
            photo = None
        
        # Botão principal de upload
        btn = ctk.CTkButton(
            self.root,
            text="🎬 Clique para enviar vídeo",
            image=photo,
            command=self.upload_video,
            width=900,
            height=200,
            fg_color="#FFFFFF",
            corner_radius=30,
            font=("Arial", 24, "bold"),
            border_width=2,
            border_color="#94E4FF",
            compound="top",
            text_color="#000000"
        )
        btn.pack(pady=(50, 200))
        
        # Imagem de fundo
        try:
            bg_img_path = os.path.join("client", "filme.png")
            if os.path.exists(bg_img_path):
                desired_width = 2400
                desired_height = 2000
                bg_img = Image.open(bg_img_path)
                bg_img = bg_img.resize((desired_width, desired_height), Image.LANCZOS)
                bg_photo = ctk.CTkImage(light_image=bg_img, size=(desired_width, desired_height))
                bg_label = ctk.CTkLabel(self.root, image=bg_photo, text="")
                bg_label.place(relx=0.6, rely=0.5, anchor="center")
                bg_label.lower()
        except:
            pass
        
        # Imagem do canto
        try:
            corner_img_path = os.path.join("client", "cavaloo.png")
            if os.path.exists(corner_img_path):
                corner_img = Image.open(corner_img_path)
                corner_img = corner_img.resize((250, 250), Image.LANCZOS)
                corner_photo = ctk.CTkImage(light_image=corner_img, size=(250, 250))
                corner_label = ctk.CTkLabel(self.root, image=corner_photo, text="")
                corner_label.place(relx=0.0, rely=1.0, anchor="sw")
        except:
            pass
    
    def exit_fullscreen(self, event=None):
        """Sai da tela cheia e fecha aplicação"""
        self.root.attributes('-fullscreen', False)
        self.root.destroy()
    
    def run(self):
        """Inicia a aplicação"""
        self.root.mainloop()

if __name__ == "__main__":
    client = VideoUploadClient()
    client.run()