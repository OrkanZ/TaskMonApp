with open('services.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar donde empieza def comprar_recompensa_personal
start_index = 0
for i, l in enumerate(lines):
    if l.startswith('def comprar_recompensa_personal'):
        start_index = i
        break

# Parte 1: Hasta pokemon_id=nuevo_id,
part1 = []
for l in lines:
    part1.append(l)
    if "pokemon_id=nuevo_id," in l:
        break

middle_code = """            hp_maximo=hp_calc,
            hp_actual=hp_calc,
            tier=BossTier.NORMAL,
            completada=False
        )
        session.add(nuevo_jefe)
        
    session.commit()

import json
import os

def add_combat_log_message(msg: str):
    log_file = "combat_log.json"
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except:
            pass
            
    # Formato: [timestamp, msg]
    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    logs.insert(0, f"[{now_str}] {msg}")
    
    # Mantener maximo 5
    if len(logs) > 5:
        logs = logs[:5]
        
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
        
def get_combat_logs() -> list[str]:
    log_file = "combat_log.json"
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def obtener_recompensas_personales(session: Session):
    return session.execute(select(RecompensaPersonal)).scalars().all()

def crear_recompensa_personal(session: Session, nombre: str, precio: int, icono: str):
    nueva = RecompensaPersonal(nombre=nombre, precio=precio, icono=icono)
    session.add(nueva)
    session.commit()
    return nueva

def eliminar_recompensa_personal(session: Session, id_recompensa: int):
    rec = session.execute(select(RecompensaPersonal).where(RecompensaPersonal.id == id_recompensa)).scalars().first()
    if rec:
        session.delete(rec)
        session.commit()
        return True
    return False

"""

part2 = lines[start_index:]

with open('services.py', 'w', encoding='utf-8') as f:
    f.writelines(part1)
    f.write(middle_code)
    f.writelines(part2)
