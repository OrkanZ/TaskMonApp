from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from datetime import date
from models import MisionRegular, MissionType
from database import engine

def main():
    with Session(engine) as session:
        hoy = date.today()
        diarias = session.execute(
            select(MisionRegular).where(
                and_(
                    MisionRegular.tipo == MissionType.DIARIA,
                    MisionRegular.fecha_asignacion == hoy
                )
            )
        ).scalars().all()
        
        print(f"Total Diarias Asignadas Hoy: {len(diarias)}")
        for d in diarias:
            print(f"- ID: {d.id}, Completada: {d.completada}, Banco_ID: {d.banco_mision_id}")

if __name__ == "__main__":
    main()
