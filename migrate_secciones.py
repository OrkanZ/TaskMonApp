import sqlite3

def migrate():
    conn = sqlite3.connect("taskmon.db")
    c = conn.cursor()
    
    # Crear tabla secciones
    c.execute("""
    CREATE TABLE IF NOT EXISTS secciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100) NOT NULL,
        lista_id INTEGER NOT NULL,
        orden INTEGER DEFAULT 0,
        FOREIGN KEY(lista_id) REFERENCES listas_tareas(id)
    )
    """)
    print("Tabla secciones creada o ya existe")
    
    # Añadir seccion_id a banco_misiones
    try:
        c.execute("ALTER TABLE banco_misiones ADD COLUMN seccion_id INTEGER REFERENCES secciones(id)")
        print("Añadida columna seccion_id a banco_misiones")
    except sqlite3.OperationalError as e:
        print(f"La columna seccion_id ya existe o hubo un error: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
