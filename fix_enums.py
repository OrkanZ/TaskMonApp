import sqlite3
conn = sqlite3.connect('taskmon.db')
c = conn.cursor()
c.execute("UPDATE banco_misiones SET dificultad = 'NORMAL' WHERE dificultad = 'Normal'")
c.execute("UPDATE banco_misiones SET prioridad = 'SIN_PRIORIDAD' WHERE prioridad = 'Sin prioridad'")
conn.commit()
conn.close()
print("Fix applied")
