from database import engine, get_session
from models import Base, PokemonCapturado, RegistroPokedex
from sqlalchemy import select

def run_migration():
    print("Creando la nueva tabla RegistroPokedex si no existe...")
    Base.metadata.create_all(bind=engine)
    
    print("Moviendo datos...")
    with get_session() as session:
        # Obtenemos todos los pokemon actualmente capturados
        capturados = session.execute(select(PokemonCapturado.pokeapi_id)).scalars().all()
        
        # Obtenemos los que ya están en registro (por si se corre dos veces)
        ya_registrados = session.execute(select(RegistroPokedex.pokeapi_id)).scalars().all()
        set_registrados = set(ya_registrados)
        
        nuevos_registros = 0
        for pid in set(capturados):
            if pid not in set_registrados:
                nuevo = RegistroPokedex(pokeapi_id=pid)
                session.add(nuevo)
                nuevos_registros += 1
                
        session.commit()
        print(f"Migración completada. Añadidos {nuevos_registros} registros históricos a la Pokédex.")

if __name__ == "__main__":
    run_migration()
