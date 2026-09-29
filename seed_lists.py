from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import ListaTareas
from database import engine

def main():
    with Session(engine) as session:
        nombres = ["Misiones Diarias", "Misiones Semanales"]
        iconos = ["TODAY", "CALENDAR_MONTH"]
        colores = ["#F44336", "#FF9800"]
        
        for nombre, icono, color in zip(nombres, iconos, colores):
            if not session.execute(select(ListaTareas).where(ListaTareas.nombre == nombre)).scalars().first():
                session.add(ListaTareas(nombre=nombre, icono=icono, color=color))
        
        session.commit()
        print("Listas del sistema creadas con éxito.")

if __name__ == "__main__":
    main()
