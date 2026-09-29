from sqlalchemy.orm import Session
from database import engine
from models import MisionRegular, Usuario
from sqlalchemy import select
import services

def main():
    with Session(engine) as session:
        usuario = session.execute(select(Usuario)).scalars().first()
        print(f"XP inicial: {usuario.xp_actual}")
        
        # Obtener las 3 diarias
        diarias = session.execute(
            select(MisionRegular).where(MisionRegular.tipo == "DIARIA")
        ).scalars().all()
        
        print(f"Encontradas {len(diarias)} misiones diarias.")
        
        for m in diarias:
            if not m.completada:
                exito, res = services.completar_mision(session, m.id)
                print(f"Completada misión {m.id}. Resultados: {res}")
                
        usuario = session.execute(select(Usuario)).scalars().first()
        print(f"XP final: {usuario.xp_actual}")

if __name__ == "__main__":
    main()
