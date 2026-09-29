import random
from database import get_session
from models import PokemonCapturado
from sqlalchemy import select
import services

def unlock_random():
    with get_session() as session:
        # Rango de la Gen 5
        possible_ids = list(range(494, 650))
        
        # Filtrar los que ya están capturados
        caught_ids = session.execute(select(PokemonCapturado.pokeapi_id)).scalars().all()
        for c_id in caught_ids:
            if c_id in possible_ids:
                possible_ids.remove(c_id)
                
        # Seleccionar 10 aleatorios
        to_unlock = random.sample(possible_ids, min(10, len(possible_ids)))
        
        for pid in to_unlock:
            new_pk = PokemonCapturado(pokeapi_id=pid, nivel=1, xp=0, en_equipo=False)
            session.add(new_pk)
            services.registrar_pokedex(session, pid)
            print(f"Desbloqueado #{pid}")
            
        session.commit()
        print("¡10 Pokémon desbloqueados con éxito!")

if __name__ == "__main__":
    unlock_random()
