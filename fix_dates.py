import sqlite3
conn = sqlite3.connect('taskmon.db')
c = conn.cursor()
c.execute("UPDATE misiones_regulares SET fecha_limite = fecha_asignacion WHERE tipo = 'Diaria' AND fecha_limite IS NULL")
conn.commit()
conn.close()
print('Fix applied')
