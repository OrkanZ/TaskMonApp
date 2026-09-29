from database import get_session
from models import BancoMisiones, MisionRegular, MissionCategory, MissionType
from datetime import date

def forzar_mision_en_pantalla():
    with get_session() as session:
        # 1. Creamos la misión en el banco general
        nueva_mision = BancoMisiones(
            titulo="Probar que esto sale en pantalla", 
            categoria=MissionCategory.PRODUCTIVIDAD, 
            cooldown_dias=1
        )
        session.add(nueva_mision)
        session.commit() # Guardamos para que se le asigne un ID

        # 2. La asignamos FORZOSAMENTE a las misiones activas de hoy
        mision_activa_hoy = MisionRegular(
            banco_mision_id=nueva_mision.id,
            tipo=MissionType.DIARIA,
            completada=False,
            fecha_asignacion=date.today()
        )
        session.add(mision_activa_hoy)
        session.commit()
        print(f"Misión '{nueva_mision.titulo}' forzada añadida a la pantalla de hoy.")

if __name__ == "__main__":
    forzar_mision_en_pantalla()
