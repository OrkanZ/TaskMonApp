import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import (
    Base, Usuario, Inventario, ItemType, PokemonCapturado, Huevo,
    BancoMisiones, ListaTareas
)

from database import engine, DB_PATH

def init_db():
    # Eliminar base de datos si ya existe para empezar limpio (útil para desarrollo)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Base de datos anterior '{DB_PATH}' eliminada.")

    # Crear todas las tablas definidas en los modelos
    Base.metadata.create_all(engine)
    print("Tablas creadas exitosamente.")

    # Insertar datos por defecto y de prueba
    with Session(engine) as session:
        # 1. Crear el usuario inicial
        usuario = Usuario(nivel=1, xp_actual=0, monedas=0)
        session.add(usuario)

        # 2. Inicializar inventario vacío para todos los tipos de objetos
        for item in ItemType:
            session.add(Inventario(tipo_objeto=item, cantidad=0))
            
        # 3. Añadir un huevo de prueba sin equipar
        session.add(Huevo(tareas_requeridas=10, tareas_completadas=0, equipado=False))
        

        # 5. Añadir Listas del Sistema
        lista_diaria = ListaTareas(nombre="Misiones Diarias", icono="TODAY", color="#2196F3")
        lista_semanal = ListaTareas(nombre="Misiones Semanales", icono="DATE_RANGE", color="#9C27B0")
        session.add_all([lista_diaria, lista_semanal])
        session.commit() # Commit to get IDs
        
        # 6. Añadir misiones base al Banco de Misiones para que el sistema las seleccione
        diarias = [
            "Misión Diaria de ejemplo 1 (Edítame)",
            "Misión Diaria de ejemplo 2 (Edítame)",
            "Misión Diaria de ejemplo 3 (Edítame)"
        ]
        
        semanales = [
            "Misión Semanal de ejemplo 1 (Edítame)",
            "Misión Semanal de ejemplo 2 (Edítame)",
            "Misión Semanal de ejemplo 3 (Edítame)"
        ]

        misiones_iniciales = []
        for d in diarias:
            misiones_iniciales.append(BancoMisiones(titulo=d, lista_id=lista_diaria.id, cooldown_dias=1))
            
        for s in semanales:
            misiones_iniciales.append(BancoMisiones(titulo=s, lista_id=lista_semanal.id, cooldown_dias=7))
            
        session.add_all(misiones_iniciales)

        # Guardar todos los cambios
        session.commit()
        print("Base de datos inicializada y datos de prueba insertados con éxito.")

if __name__ == "__main__":
    init_db()
