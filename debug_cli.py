import sys
from database import get_session
from models import Usuario, PokemonCapturado, Inventario, ItemType, RegistroPokedex
from sqlalchemy import select

def print_menu():
    print("\n" + "="*40)
    print("🛠️  HERRAMIENTA DE DEBUG - TASKMON 🛠️")
    print("="*40)
    print("1. 👤 Modificar Perfil (Monedas, Nivel, XP)")
    print("2. 🐲 Añadir Pokémon (ID de PokéAPI, Nivel, XP)")
    print("3. 🎒 Modificar Inventario (Añadir/Quitar objetos)")
    print("4. 📖 Desbloquear toda la Pokédex (Gen 5)")
    print("5. 🧹 Limpiar tu PC (Borrar todos los Pokémon)")
    print("6. 🥚 Modificar Huevo Equipado (Tareas completadas)")
    print("0. Salir")
    print("="*40)

def modificar_perfil(session):
    user = session.execute(select(Usuario)).scalars().first()
    if not user:
        user = Usuario()
        session.add(user)
        
    print(f"\nDatos Actuales -> Nivel: {user.nivel}, XP: {user.xp_actual}, Monedas: {user.monedas}")
    
    n = input("Nuevo Nivel (Enter para omitir): ")
    if n.isdigit(): user.nivel = int(n)
        
    x = input("Nueva XP (Enter para omitir): ")
    if x.isdigit(): user.xp_actual = int(x)
        
    m = input("Nuevas Monedas (Enter para omitir): ")
    if m.isdigit(): user.monedas = int(m)
        
    session.commit()
    print("✅ Perfil actualizado.")

def anadir_pokemon(session):
    pid_str = input("\nID del Pokémon (PokéAPI, ej. 495 para Snivy): ")
    if not pid_str.isdigit():
        print("❌ ID inválida.")
        return
        
    pid = int(pid_str)
    
    # Comprobar si ya lo tiene (no se permiten duplicados en DB ahora mismo)
    existente = session.execute(select(PokemonCapturado).where(PokemonCapturado.pokeapi_id == pid)).scalars().first()
    if existente:
        print(f"⚠️ Ya tienes al Pokémon #{pid} en el PC.")
        mod = input("¿Quieres modificar sus stats? (s/n): ")
        if mod.lower() != 's': return
        pk = existente
    else:
        pk = PokemonCapturado(pokeapi_id=pid)
        session.add(pk)
        print("✅ Nuevo Pokémon añadido al PC.")
        
    niv = input(f"Nivel actual ({pk.nivel}): ")
    if niv.isdigit(): pk.nivel = int(niv)
        
    xp = input(f"XP actual ({pk.xp}): ")
    if xp.isdigit(): pk.xp = int(xp)
        
    eq = input(f"¿En equipo? (s/n) ({'Sí' if pk.en_equipo else 'No'}): ")
    if eq.lower() == 's': pk.en_equipo = True
    elif eq.lower() == 'n': pk.en_equipo = False
        
    # Añadir a registro histórico también
    reg = session.execute(select(RegistroPokedex).where(RegistroPokedex.pokeapi_id == pid)).scalars().first()
    if not reg:
        session.add(RegistroPokedex(pokeapi_id=pid))
        
    session.commit()
    print("✅ Stats del Pokémon guardadas.")

def modificar_inventario(session):
    print("\nObjetos disponibles:")
    for tipo in ItemType:
        print(f"- {tipo.value}")
        
    tipo_str = input("\nNombre exacto del objeto a modificar: ")
    try:
        tipo = ItemType(tipo_str)
    except ValueError:
        print("❌ Tipo de objeto no válido.")
        return
        
    item = session.execute(select(Inventario).where(Inventario.tipo_objeto == tipo)).scalars().first()
    if not item:
        item = Inventario(tipo_objeto=tipo, cantidad=0)
        session.add(item)
        
    cant = input(f"Cantidad actual ({item.cantidad}). Introduce nueva cantidad: ")
    if cant.isdigit():
        item.cantidad = int(cant)
        session.commit()
        print("✅ Inventario actualizado.")
    else:
        print("❌ Cantidad inválida.")

def desbloquear_pokedex(session):
    conf = input("\n⚠️ Esto añadirá a los 156 Pokémon de la Gen 5 al Registro Histórico. ¿Estás seguro? (s/n): ")
    if conf.lower() == 's':
        existentes = session.execute(select(RegistroPokedex.pokeapi_id)).scalars().all()
        set_existentes = set(existentes)
        
        nuevos = 0
        for i in range(494, 650):
            if i not in set_existentes:
                session.add(RegistroPokedex(pokeapi_id=i))
                nuevos += 1
                
        session.commit()
        print(f"✅ ¡Pokédex completada! Se han añadido {nuevos} nuevas entradas.")

def limpiar_pc(session):
    conf = input("\n⚠️ ¡CUIDADO! Esto borrará TODOS los Pokémon capturados. Tu Pokédex seguirá intacta. ¿Confirmar? (s/n): ")
    if conf.lower() == 's':
        session.execute(PokemonCapturado.__table__.delete())
        session.commit()
        print("🧹 PC limpiado con éxito.")

def modificar_huevo(session):
    from models import Huevo
    huevo = session.execute(select(Huevo).where(Huevo.equipado == True)).scalars().first()
    if not huevo:
        print("❌ No hay ningún huevo equipado en la incubadora.")
        return
        
    print(f"\n🥚 Huevo Equipado -> Tipo: {huevo.tipo_huevo}, Tareas: {huevo.tareas_completadas}/{huevo.tareas_requeridas}")
    
    t = input("Nuevas tareas completadas (Enter para omitir): ")
    if t.isdigit():
        huevo.tareas_completadas = int(t)
        session.commit()
        print("✅ Huevo actualizado. ¡Haz una tarea en la app para ver la eclosión si has llegado a 50!")

def main():
    while True:
        print_menu()
        opcion = input("Elige una opción: ")
        
        with get_session() as session:
            if opcion == '1':
                modificar_perfil(session)
            elif opcion == '2':
                anadir_pokemon(session)
            elif opcion == '3':
                modificar_inventario(session)
            elif opcion == '4':
                desbloquear_pokedex(session)
            elif opcion == '5':
                limpiar_pc(session)
            elif opcion == '6':
                modificar_huevo(session)
            elif opcion == '0':
                print("👋 ¡Hasta luego!")
                sys.exit(0)
            else:
                print("❌ Opción no válida.")

if __name__ == "__main__":
    main()
