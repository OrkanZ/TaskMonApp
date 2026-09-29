import sqlite3

def main():
    conn = sqlite3.connect("taskmon.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE estadisticas ADD COLUMN encuentro_comun_progreso INTEGER DEFAULT 0")
        print("Añadida columna encuentro_comun_progreso.")
    except sqlite3.OperationalError as e:
        print(f"Nota: {e}")
        
    try:
        cursor.execute("ALTER TABLE estadisticas ADD COLUMN encuentro_raro_progreso INTEGER DEFAULT 0")
        print("Añadida columna encuentro_raro_progreso.")
    except sqlite3.OperationalError as e:
        print(f"Nota: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
