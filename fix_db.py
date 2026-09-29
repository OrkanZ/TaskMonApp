import sqlite3
import json

conn = sqlite3.connect("taskmon.db")
c = conn.cursor()

# 1. Print current state
c.execute("SELECT id, tipo_objeto FROM inventario")
rows = c.fetchall()
print("Inventario actual:", rows)

c.execute("SELECT id, tipo_huevo FROM huevos")
rows2 = c.fetchall()
print("Huevos actuales:", rows2)

# 2. Fix it
# Revert "Acelerador Eclosión" -> "ACELERADOR"
# Because SQLAlchemy stores the Enum *name*!
# The name in models.py is ACELERADOR.
c.execute("UPDATE inventario SET tipo_objeto = 'ACELERADOR' WHERE tipo_objeto = 'Acelerador Eclosión'")
c.execute("UPDATE inventario SET tipo_objeto = 'CEBO' WHERE tipo_objeto = 'Baya Meloc'")
c.execute("UPDATE inventario SET tipo_objeto = 'BOOST_XP' WHERE tipo_objeto = 'Huevo Suerte'")

c.execute("UPDATE huevos SET tipo_huevo = 'ACELERADOR' WHERE tipo_huevo = 'Acelerador Eclosión'")
c.execute("UPDATE huevos SET tipo_huevo = 'CEBO' WHERE tipo_huevo = 'Baya Meloc'")
c.execute("UPDATE huevos SET tipo_huevo = 'BOOST_XP' WHERE tipo_huevo = 'Huevo Suerte'")

# If the original string was 'Acelerador' maybe that was stored?
# Let's also fix 'Acelerador' -> 'ACELERADOR' just in case.
# Wait, SQLAlchemy by default stores the NAME of the enum (e.g. 'ACELERADOR').
# But maybe it was storing the value if values_callable was used? No, default is name.

conn.commit()

c.execute("SELECT id, tipo_objeto FROM inventario")
print("Inventario tras fix:", c.fetchall())

conn.close()
