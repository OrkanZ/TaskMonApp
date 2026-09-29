import random
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import ListaTareas, BancoMisiones, Dificultad
from database import engine

def main():
    with Session(engine) as session:
        lista_diaria = session.execute(select(ListaTareas).where(ListaTareas.nombre == "Misiones Diarias")).scalars().first()
        lista_semanal = session.execute(select(ListaTareas).where(ListaTareas.nombre == "Misiones Semanales")).scalars().first()
        
        if lista_diaria:
            for i in range(1, 6):
                m = BancoMisiones(
                    titulo=f"[Dummy Diaria] Tarea de prueba {i}",
                    lista_id=lista_diaria.id,
                    cooldown_dias=0,
                    dificultad=Dificultad.FACIL
                )
                session.add(m)
                
        if lista_semanal:
            for i in range(1, 6):
                m = BancoMisiones(
                    titulo=f"[Dummy Semanal] Tarea de prueba {i}",
                    lista_id=lista_semanal.id,
                    cooldown_dias=0,
                    dificultad=Dificultad.NORMAL
                )
                session.add(m)
                
        session.commit()
        print("Misiones dummy creadas en el BancoMisiones para Diarias y Semanales.")

if __name__ == "__main__":
    main()
