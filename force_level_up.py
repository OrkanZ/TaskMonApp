import sys
from database import get_session
from models import PokemonCapturado
from sqlalchemy import select

def cheat():
    with get_session() as session:
        # Buscar el primer Pokémon equipado
        pk = session.execute(
            select(PokemonCapturado).where(PokemonCapturado.en_equipo == True)
        ).scalars().first()
        
        if not pk:
            print("❌ No tienes ningún Pokémon en tu equipo. ¡Ve a la pestaña de Equipo y equipa uno primero!")
            sys.exit(1)
            
        # Nivel 16 es ideal porque la mayoría de iniciales (Snivy, Tepig, Oshawott) 
        # y Pokémon básicos evolucionan al nivel 17.
        pk.nivel = 16
        
        # Para pasar a Nivel 17 necesita 25 + (16 * 15) = 265 XP.
        # Le ponemos 260 XP, así que a la mínima tarea que completes (10 XP), subirá de nivel.
        pk.xp = 260
        
        session.commit()
        
        print(f"✅ ¡Truco activado! Tu Pokémon en el equipo ahora es Nivel 16.")
        print("Vuelve a la aplicación y completa CUALQUIER tarea para ver la evolución a Nivel 17.")

if __name__ == "__main__":
    cheat()
