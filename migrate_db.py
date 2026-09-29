import sqlite3

def migrate():
    conn = sqlite3.connect('taskmon.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE banco_misiones ADD COLUMN dificultad VARCHAR(20) DEFAULT 'Normal'")
        print("Añadida columna dificultad a banco_misiones")
    except sqlite3.OperationalError as e:
        print("Error añadiendo dificultad (puede que ya exista):", e)

    try:
        cursor.execute("ALTER TABLE banco_misiones ADD COLUMN prioridad VARCHAR(20) DEFAULT 'Sin prioridad'")
        print("Añadida columna prioridad a banco_misiones")
    except sqlite3.OperationalError as e:
        print("Error añadiendo prioridad (puede que ya exista):", e)

    try:
        cursor.execute("ALTER TABLE misiones_regulares ADD COLUMN fecha_limite DATE")
        print("Añadida columna fecha_limite a misiones_regulares")
    except sqlite3.OperationalError as e:
        print("Error añadiendo fecha_limite (puede que ya exista):", e)

    conn.commit()
    conn.close()
    print("Migración completada.")

if __name__ == '__main__':
    migrate()
