import os
import sys
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if hasattr(sys, 'getandroidapilevel'):
    # Entorno Android: La carpeta HOME apunta a los datos internos de la app (escribibles)
    DB_PATH = os.path.join(os.environ.get("HOME", "."), "taskmon.db")
    if not os.path.exists(DB_PATH):
        bundled_db = os.path.join(os.path.dirname(__file__), "taskmon.db")
        if os.path.exists(bundled_db):
            shutil.copy(bundled_db, DB_PATH)
else:
    # Entorno PC: Raíz del proyecto
    DB_PATH = "taskmon.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Generador de sesiones para la base de datos local."""
    return SessionLocal()
