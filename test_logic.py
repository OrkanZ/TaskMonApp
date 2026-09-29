from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import JefeMisionPrincipal, BossTier, MissionType, Base
import init_db
import services

def run_test():
    # Reiniciamos la base de datos para una prueba limpia
    print("--- Inicializando DB ---")
    init_db.init_db()
    
    from database import engine, DB_PATH
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    
    with Session(engine) as session:
        # Añadir un Jefe de Prueba (Kyurem)
        print("--- Configurando Jefe de Prueba ---")
        jefe = JefeMisionPrincipal(
            titulo="Derrotar a Kyurem (Semana 1)",
            pokemon_id=646,
            hp_maximo=1000,
            hp_actual=1000,
            tier=BossTier.A
        )
        session.add(jefe)
        session.commit()
        
        print("\n--- Generando Misiones Diarias ---")
        misiones = services.generar_misiones(session, MissionType.DIARIA, 3)
        session.commit() # Guardar misiones para obtener IDs
        for m in misiones:
            print(f"- [ ] {m.banco_mision.titulo} (ID: {m.id})")
        
        # Simulamos completar la primera misión
        mision_a_completar = misiones[0]
        print(f"\n--- Completando Misión: {mision_a_completar.banco_mision.titulo} ---")
        
        exito, resultados = services.completar_mision(session, mision_a_completar.id)
        
        if exito:
            print("¡Misión Completada con Éxito!")
            print(f"XP Ganada: {resultados['xp_ganada']}")
            print(f"Monedas: {resultados['monedas_ganadas']}")
            print(f"Loot: {resultados['loot'] if resultados['loot'] else 'Nada'}")
            print(f"Daño al Jefe (Mewtwo): {resultados['dano_jefe']}")
            print(f"HP Restante del Jefe: {resultados['jefe_hp_actual']}")
            progreso, req = resultados['huevo_progreso']
            print(f"Progreso Huevo: {progreso}/{req}")
            print(f"Combo Diario completado: {resultados['combo_diario']}")
        else:
            print("Error al completar la misión.")

if __name__ == "__main__":
    run_test()
