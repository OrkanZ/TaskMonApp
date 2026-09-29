from database import get_session
from models import Estadisticas
from sqlalchemy import select

def set_encounters_ready():
    with get_session() as session:
        stats = session.execute(select(Estadisticas)).scalars().first()
        if stats:
            stats.encuentro_comun_progreso = 5
            stats.encuentro_raro_progreso = 5
            session.commit()
            print("✅ Los contadores de encuentros se han puesto a 5/5 exitosamente.")
        else:
            print("❌ No se encontraron estadísticas en la base de datos.")

if __name__ == "__main__":
    set_encounters_ready()
