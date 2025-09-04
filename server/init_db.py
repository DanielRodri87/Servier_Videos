import sqlite3

DB = "videos.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            original_name TEXT,
            original_ext TEXT,
            mime_type TEXT,
            size_bytes INTEGER,
            duration_sec REAL,
            fps REAL,
            width INTEGER,
            height INTEGER,
            filter TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            path_original TEXT,
            path_processed TEXT
        );
        """)
    print(f"Banco {DB} inicializado com sucesso!")

if __name__ == "__main__":
    init_db()
