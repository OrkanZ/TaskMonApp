import sqlite3

def migrate():
    conn = sqlite3.connect("taskmon.db")
    c = conn.cursor()
    
    try:
        c.execute("ALTER TABLE misiones_regulares ADD COLUMN orden INTEGER DEFAULT 0")
        print("Añadida columna orden a misiones_regulares")
    except sqlite3.OperationalError as e:
        print(f"La columna orden ya existe o hubo un error: {e}")
        
    try:
        c.execute("ALTER TABLE banco_misiones ADD COLUMN notas TEXT")
        print("Añadida columna notas a banco_misiones")
    except sqlite3.OperationalError as e:
        print(f"La columna notas ya existe o hubo un error: {e}")
        
    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    migrate()
