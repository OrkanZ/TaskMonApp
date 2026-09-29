import sqlite3

def main():
    conn = sqlite3.connect("taskmon.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE banco_misiones ADD COLUMN recurrencia_dias INTEGER DEFAULT NULL")
        print("Migración completada: columna recurrencia_dias añadida a banco_misiones.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("La columna recurrencia_dias ya existe.")
        else:
            print(f"Error durante la migración: {e}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
