# Sistema de Upload e Processamento de Vídeos

Este projeto consiste em um sistema de upload e processamento de vídeos com interface gráfica desktop e visualização web. O sistema permite fazer upload de vídeos e aplicar diferentes filtros de processamento de imagem.

## 🚀 Funcionalidades

- Upload de vídeos através de interface gráfica desktop
- Galeria web para visualização dos vídeos
- Aplicação de filtros (Escala de cinza e CLAHE)
- Geração automática de thumbnails
- Armazenamento de metadados em banco SQLite

## 📋 Pré-requisitos

- Python 3.8+
- FFmpeg
- Bibliotecas Python (requirements.txt)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/DanielRodri87/Servier_Videos```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Inicialize o banco de dados:
```bash
cd server
python init_db.py
```

## ⚡ Executando o Sistema

1. Inicie o servidor Flask:
```bash
cd server
python server.py
```

2. Em outro terminal, execute o cliente desktop:
```bash
cd static
python client.py
```

3. Acesse a galeria web em: http://127.0.0.1:5000

## 📸 Screenshots

### Interface do Cliente
![Interface do Cliente](screenshots/foto_client.png)
*Interface desktop do cliente para upload de vídeos*

### Interface do Servidor
![Interface do Servidor](screenshots/foto_servidor.png)
*Interface web do servidor mostrando a galeria de vídeos*

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask, OpenCV, FFmpeg
- **Frontend Desktop**: CustomTkinter
- **Frontend Web**: HTML, CSS
- **Banco de Dados**: SQLite
- **Processamento de Vídeo**: OpenCV, FFmpeg

## ✒️ Estrutura do Projeto

```
Servier_Videos-walison/
├── server/
│   ├── server.py
│   ├── init_db.py
│   └── templates/
│       └── gallery.html
├── static/
│   └── client.py
└── media/
    └── videos/
```

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.