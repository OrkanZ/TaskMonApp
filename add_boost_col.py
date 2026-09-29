import sqlite3

def upgrade_db():
    try:
        conn = sqlite3.connect("taskmon.db")
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE usuarios ADD COLUMN boost_xp_restantes INTEGER DEFAULT 0")
        conn.commit()
        conn.close()
        print("Migración completada exitosamente.")
    except Exception as e:
        print(f"Error o la columna ya existe: {e}")

if __name__ == '__main__':
    upgrade_db()
