import sqlite3

def run_migration():
    conn = sqlite3.connect("taskmon.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE huevos ADD COLUMN tipo_huevo VARCHAR")
        conn.commit()
        print("Migración exitosa: Columna 'tipo_huevo' añadida a 'huevos'.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("La columna 'tipo_huevo' ya existe.")
        else:
            print(f"Error en la migración: {e}")
            
    conn.close()

if __name__ == "__main__":
    run_migration()
