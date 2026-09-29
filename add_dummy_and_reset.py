import random
from datetime import date
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from models import ListaTareas, BancoMisiones, MisionRegular, Dificultad
from database import engine
import services

def main():
    with Session(engine) as session:
        # Añadir más misiones dummy al banco
        lista_diaria = session.execute(select(ListaTareas).where(ListaTareas.nombre == "Misiones Diarias")).scalars().first()
        lista_semanal = session.execute(select(ListaTareas).where(ListaTareas.nombre == "Misiones Semanales")).scalars().first()
        
        if lista_diaria:
            for i in range(6, 15):
                m = BancoMisiones(
                    titulo=f"[Dummy Diaria] Nueva Tarea {i}",
                    lista_id=lista_diaria.id,
                    cooldown_dias=0,
                    dificultad=Dificultad.FACIL
                )
                session.add(m)
                
        if lista_semanal:
            for i in range(6, 15):
                m = BancoMisiones(
                    titulo=f"[Dummy Semanal] Nueva Tarea {i}",
                    lista_id=lista_semanal.id,
                    cooldown_dias=0,
                    dificultad=Dificultad.NORMAL
                )
                session.add(m)
                
        # Borrar el historial de MisionRegular de Diarias/Semanales generadas hoy para que el actualizador genere más.
        hoy = date.today()
        if lista_diaria:
            hoy_diarias = session.execute(
                select(MisionRegular).join(BancoMisiones).where(
                    and_(
                        BancoMisiones.lista_id == lista_diaria.id,
                        MisionRegular.fecha_asignacion == hoy
                    )
                )
            ).scalars().all()
            for m in hoy_diarias:
                session.delete(m)
                
        if lista_semanal:
            hoy_semanales = session.execute(
                select(MisionRegular).join(BancoMisiones).where(
                    and_(
                        BancoMisiones.lista_id == lista_semanal.id,
                        # Para forzar reinicio, borramos las de esta semana
                        MisionRegular.fecha_asignacion == hoy
                    )
                )
            ).scalars().all()
            for m in hoy_semanales:
                session.delete(m)
                
        session.commit()
        
        # Ahora forzamos la actualización para que genere 3 nuevas
        services.update_system_missions(session)
        session.commit()
        print("Más misiones añadidas y reseteadas para hoy.")

if __name__ == "__main__":
    main()
