from database import get_session
from models import PokemonCapturado, RegistroPokedex
from sqlalchemy import select

def fix_and_give_tepig():
    with get_session() as session:
        # Fix Snivy missing from history (because it evolved before the migration!)
        snivy_in_reg = session.execute(select(RegistroPokedex).where(RegistroPokedex.pokeapi_id == 495)).scalars().first()
        if not snivy_in_reg:
            session.add(RegistroPokedex(pokeapi_id=495))
            
        # Add Tepig (498) to history
        tepig_in_reg = session.execute(select(RegistroPokedex).where(RegistroPokedex.pokeapi_id == 498)).scalars().first()
        if not tepig_in_reg:
            session.add(RegistroPokedex(pokeapi_id=498))
            
        # Remove current team
        current_team = session.execute(select(PokemonCapturado).where(PokemonCapturado.en_equipo == True)).scalars().all()
        for pk in current_team:
            pk.en_equipo = False
            
        # Give Tepig ready to evolve (Level 16, 260 XP)
        tepig = PokemonCapturado(pokeapi_id=498, nivel=16, xp=260, en_equipo=True)
        session.add(tepig)
        
        session.commit()
        print("¡Snivy restaurado en la Pokédex!")
        print("¡Tepig Nivel 16 (260 XP) ha sido añadido a tu equipo!")

if __name__ == "__main__":
    fix_and_give_tepig()
