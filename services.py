import random
from datetime import date, datetime
import json
import os
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from models import (
    Usuario, Inventario, ItemType, BancoMisiones, MisionRegular, 
    MissionType, JefeMisionPrincipal, PokemonCapturado, Huevo,
    RegistroPokedex, Estadisticas, LogroDesbloqueado, BossTier, RecompensaPersonal,
    Dificultad, ListaTareas, Prioridad
)
from achievement_metadata import ACHIEVEMENTS
import pokeapi

def registrar_pokedex(session: Session, pokeapi_id: int):
    existe = session.execute(
        select(RegistroPokedex).where(RegistroPokedex.pokeapi_id == pokeapi_id)
    ).scalars().first()
    if not existe:
        session.add(RegistroPokedex(pokeapi_id=pokeapi_id))

def generar_misiones(session: Session, tipo: MissionType, cantidad: int = 3):
    """
    Genera misiones para el día o la semana obteniéndolas del BancoMisiones.
    Respeta el cooldown.
    """
    hoy = date.today()
    
    # 1. Obtener misiones del banco que están disponibles según su cooldown
    # En SQLite / SQLAlchemy con date math simple: 
    # Filtramos en Python por simplicidad de compatibilidad, o usando SQL.
    todas_misiones_banco = session.execute(select(BancoMisiones)).scalars().all()
    
    misiones_disponibles = []
    for bm in todas_misiones_banco:
        if bm.ultima_aparicion is None:
            misiones_disponibles.append(bm)
        else:
            dias_pasados = (hoy - bm.ultima_aparicion).days
            if dias_pasados >= bm.cooldown_dias:
                misiones_disponibles.append(bm)
                
    if len(misiones_disponibles) < cantidad:
        print(f"Advertencia: No hay suficientes misiones disponibles para {tipo.value}.")
        seleccionadas = misiones_disponibles
    else:
        seleccionadas = random.sample(misiones_disponibles, k=cantidad)
        
    nuevas_misiones = []
    for ms in seleccionadas:
        ms.ultima_aparicion = hoy  # Actualizar fecha de aparición
        nueva_regular = MisionRegular(
            banco_mision=ms,
            tipo=tipo,
            completada=False,
            fecha_asignacion=hoy,
            fecha_limite=hoy
        )
        session.add(nueva_regular)
        nuevas_misiones.append(nueva_regular)
        
    return nuevas_misiones
    
def calcular_y_aplicar_dano_jefe(session: Session, dificultad: Dificultad = None):
    """
    Calcula el daño infligido al jefe por el equipo activo y actualiza su HP.
    Retorna (dano_total, jefe_actualizado)
    """
    jefe = session.execute(
        select(JefeMisionPrincipal).where(JefeMisionPrincipal.completada == False)
    ).scalars().first()
    
    if not jefe:
        return 0, None  # No hay jefe activo
        
    # Obtener equipo
    equipo = session.execute(
        select(PokemonCapturado).where(PokemonCapturado.en_equipo == True)
    ).scalars().all()
    
    if not equipo:
        return 0, jefe  # Sin equipo, no hay daño
        
    # Obtener datos del Jefe en PokeAPI
    jefe_info = pokeapi.get_pokemon_info(jefe.pokemon_id)
    jefe_types = jefe_info["types"] if jefe_info else ["normal"]
    
    # Determinar multiplicador de dificultad
    multiplicador_dificultad = 1.0
    if dificultad == Dificultad.MUY_FACIL:
        multiplicador_dificultad = 0.5
    elif dificultad == Dificultad.FACIL:
        multiplicador_dificultad = 1.0
    elif dificultad == Dificultad.NORMAL:
        multiplicador_dificultad = 1.5
    elif dificultad == Dificultad.DIFICIL:
        multiplicador_dificultad = 2.5
    
    dano_total = 0
    for pk in equipo:
        pk_info = pokeapi.get_pokemon_info(pk.pokeapi_id)
        if not pk_info:
            continue
            
        poder_base = pk_info.get("taskmon_attack", 50)
        pk_types = pk_info["types"]
        multiplicador_tipo = pokeapi.get_type_multiplier(pk_types, jefe_types)
        
        # Fórmula de daño: (Poder Base + Nivel) * Modificador Dificultad * Modificador Tipo * Varianza(0.95 - 1.05)
        varianza = random.uniform(0.95, 1.05)
        dano = int((poder_base + pk.nivel) * multiplicador_dificultad * multiplicador_tipo * varianza)
        dano_total += max(1, dano) # Al menos 1 de daño
        
    jefe.hp_actual = max(0, jefe.hp_actual - dano_total)
    
    if jefe.hp_actual <= 0:
        jefe.hp_actual = 0
        jefe.completada = True
        # Aquí se podría disparar lógica de captura del jefe.
        print(f"¡Has derrotado a {jefe.titulo}!")
        
    return dano_total, jefe

def drop_loot(session: Session, dificultad: Dificultad):
    """
    Lógica de probabilidades para obtener objetos tras completar misiones basada en la dificultad.
    """
    if not dificultad:
        dificultad = Dificultad.NORMAL
        
    objetos_comunes = [ItemType.POKEBALL, ItemType.CEBO, ItemType.ACELERADOR]
    objetos_raros = [
        ItemType.ULTRABALL, ItemType.CARAMELO_RARO, ItemType.BOOST_XP, ItemType.PIEDRA_HOJA, 
        ItemType.PIEDRA_FUEGO, ItemType.PIEDRA_AGUA, ItemType.PIEDRA_LUNAR, 
        ItemType.PIEDRA_INTERCAMBIO, ItemType.PIEDRA_DIA, ItemType.PIEDRA_TRUENO, 
        ItemType.PIEDRA_NOCHE, ItemType.PIEDRA_SOLAR
    ]
    objetos_muy_raros = [ItemType.MASTERBALL, ItemType.HUEVO, ItemType.FOSIL_TAPA, ItemType.FOSIL_PLUMA]
    
    roll = random.uniform(0, 100)
    item_obtenido = None
    
    if dificultad == Dificultad.MUY_FACIL:
        if roll <= 15:
            item_obtenido = random.choice(objetos_comunes)
            
    elif dificultad == Dificultad.FACIL:
        if roll <= 30:
            item_obtenido = random.choice(objetos_comunes)
        elif roll <= 35:
            item_obtenido = random.choice(objetos_raros)
            
    elif dificultad == Dificultad.NORMAL:
        if roll <= 50:
            item_obtenido = random.choice(objetos_comunes)
        elif roll <= 70:
            item_obtenido = random.choice(objetos_raros)
        elif roll <= 75:
            item_obtenido = random.choice(objetos_muy_raros)
            
    elif dificultad == Dificultad.DIFICIL:
        if roll <= 85:
            item_obtenido = random.choice(objetos_raros)
        else:
            item_obtenido = random.choice(objetos_muy_raros)
            
    if item_obtenido:
        inv = session.execute(
            select(Inventario).where(Inventario.tipo_objeto == item_obtenido)
        ).scalars().first()
        if inv:
            inv.cantidad += 1
        else:
            session.add(Inventario(tipo_objeto=item_obtenido, cantidad=1))
        return item_obtenido
        
    return None

def vender_objeto(session: Session, tipo_objeto: ItemType, cantidad: int = 1):
    """
    Vende una cantidad de un objeto del inventario, añadiendo la mitad del precio original a las monedas del usuario.
    """
    import item_metadata
    
    inv = session.execute(
        select(Inventario).where(Inventario.tipo_objeto == tipo_objeto)
    ).scalars().first()
    
    if not inv or inv.cantidad < cantidad:
        return False, "No tienes suficientes objetos."
        
    usuario = session.get(Usuario, 1)
    if not usuario:
        return False, "Error al obtener usuario."
        
    precio_base = item_metadata.ITEM_METADATA[tipo_objeto]["price"]
    precio_venta = item_metadata.ITEM_METADATA[tipo_objeto].get("sell_price", max(1, precio_base // 2))
    
    inv.cantidad -= cantidad
    usuario.monedas += (precio_venta * cantidad)
    
    return True, f"Vendido {cantidad}x {tipo_objeto.value} por {precio_venta * cantidad} monedas."

def usar_objeto(session: Session, tipo_objeto: ItemType, target_pokemon_id: int = None):
    """
    Aplica el efecto de un objeto y lo descuenta del inventario.
    """
    inv = session.execute(
        select(Inventario).where(Inventario.tipo_objeto == tipo_objeto)
    ).scalars().first()
    
    if not inv or inv.cantidad < 1:
        return False, "No tienes este objeto."
        
    estadisticas = session.get(Estadisticas, 1)
    if not estadisticas:
        estadisticas = Estadisticas()
        session.add(estadisticas)
        session.flush()
        
    estadisticas.objetos_usados += 1
        
    if tipo_objeto == ItemType.CARAMELO_RARO:
        if not target_pokemon_id: return False, "Debes seleccionar un Pokémon."
        pk = session.execute(
            select(PokemonCapturado).where(PokemonCapturado.pokeapi_id == target_pokemon_id)
        ).scalars().first()
        if not pk: return False, "Pokémon no encontrado."
        if pk.nivel >= 100: return False, "El Pokémon ya es nivel 100."
        
        # Subir 1 nivel directamente
        pk.nivel += 1
        pk.xp = 0
        inv.cantidad -= 1
        
        import pokeapi
        info = pokeapi.get_pokemon_info(pk.pokeapi_id)
        pk_name = info["name"].capitalize() if info and "name" in info else f"Pokémon {pk.pokeapi_id}"
        
        return True, f"{pk_name} ha subido al Nivel {pk.nivel}."
        
    elif tipo_objeto == ItemType.BOOST_XP:
        usuario = session.get(Usuario, 1)
        if not usuario: return False, "Usuario no encontrado"
        usuario.boost_xp_restantes += 5
        inv.cantidad -= 1
        return True, "Has activado un Boost de XP para las próximas 5 tareas."
        
    elif tipo_objeto == ItemType.ACELERADOR:
        huevo = session.execute(select(Huevo).where(Huevo.equipado == True)).scalars().first()
        if not huevo: return False, "No tienes ningún huevo equipado."
        
        huevo.tareas_completadas += 5
        inv.cantidad -= 1
        return True, "Huevo acelerado 5 pasos."
        
    elif tipo_objeto in [
        ItemType.PIEDRA_HOJA, ItemType.PIEDRA_FUEGO, ItemType.PIEDRA_AGUA,
        ItemType.PIEDRA_LUNAR, ItemType.PIEDRA_INTERCAMBIO, ItemType.PIEDRA_DIA,
        ItemType.PIEDRA_TRUENO, ItemType.PIEDRA_NOCHE, ItemType.PIEDRA_SOLAR
    ]:
        if not target_pokemon_id: return False, "Debes seleccionar un Pokémon."
        pk = session.execute(
            select(PokemonCapturado).where(PokemonCapturado.pokeapi_id == target_pokemon_id)
        ).scalars().first()
        if not pk: return False, "Pokémon no encontrado."
        
        import item_metadata
        import pokemon_metadata
        
        stone_name = item_metadata.ITEM_METADATA[tipo_objeto]["name"]
        
        next_id = target_pokemon_id + 1
        meta_next = pokemon_metadata.POKEMON_METADATA.get(next_id)
        
        if meta_next and meta_next.get("evolucion") == stone_name:
            ya_lo_tiene = session.execute(
                select(PokemonCapturado).where(PokemonCapturado.pokeapi_id == next_id)
            ).scalars().first() is not None
            
            if ya_lo_tiene:
                return False, "Ya tienes la forma evolucionada. No puedes tener duplicados."
                
            pk.pokeapi_id = next_id
            inv.cantidad -= 1
            estadisticas.pokemon_evolucionados += 1
            registrar_pokedex(session, next_id)
            
            # TODO: We could return the info to trigger the evolution animation, 
            # but for now we just return a success message.
            return True, f"¡Tu Pokémon ha evolucionado a su siguiente forma!"
        else:
            return False, "Esta piedra no tiene ningún efecto en este Pokémon."
            
    return False, "Este objeto no se puede usar así."
def avanzar_huevo(session: Session):
    """
    Avanza en 1 la tarea de eclosión del huevo equipado.
    Devuelve un diccionario con el progreso y los datos de eclosión si ocurre.
    """
    huevo = session.execute(
        select(Huevo).where(Huevo.equipado == True)
    ).scalars().first()
    
    res = {
        "tareas_completadas": 0,
        "tareas_requeridas": 0,
        "eclosionado": False,
        "pokemon_id": None,
        "monedas_compensacion": 0
    }
    
    if huevo:
        estadisticas = session.get(Estadisticas, 1)
        if not estadisticas:
            estadisticas = Estadisticas()
            session.add(estadisticas)
            session.flush()
            
        huevo.tareas_completadas += 1
        res["tareas_completadas"] = huevo.tareas_completadas
        res["tareas_requeridas"] = huevo.tareas_requeridas
        
        if huevo.tareas_completadas >= huevo.tareas_requeridas:
            huevo.equipado = False
            res["eclosionado"] = True
            estadisticas.huevos_eclosionados += 1
            
            if huevo.tipo_huevo == ItemType.FOSIL_TAPA:
                res["pokemon_id"] = 564 # Tirtouga
            elif huevo.tipo_huevo == ItemType.FOSIL_PLUMA:
                res["pokemon_id"] = 566 # Archen
            else: # ItemType.HUEVO
                import pokemon_metadata
                import random
                
                # Obtener los IDs de los pokemon obtenibles por huevo
                huevo_pool = [k for k, v in pokemon_metadata.POKEMON_METADATA.items() if "Huevo" in v.get("metodo", "")]
                
                # Obtener los que ya tiene el usuario
                capturados = session.execute(select(PokemonCapturado.pokeapi_id)).scalars().all()
                capturados_set = set(capturados)
                
                # Filtrar
                disponibles = [p for p in huevo_pool if p not in capturados_set]
                
                if disponibles:
                    res["pokemon_id"] = random.choice(disponibles)
                else:
                    # Dar compensacion
                    res["monedas_compensacion"] = 75
                    usuario = session.get(Usuario, 1)
                    if usuario:
                        usuario.monedas += 75
            
            # Registrar pokemon si aplica (evitar duplicados de fósiles)
            if res["pokemon_id"]:
                existente = session.execute(select(PokemonCapturado).where(PokemonCapturado.pokeapi_id == res["pokemon_id"])).scalars().first()
                if existente:
                    # Ya lo tiene, dar compensación
                    res["pokemon_id"] = None
                    res["monedas_compensacion"] = 75
                    usuario = session.get(Usuario, 1)
                    if usuario:
                        usuario.monedas += 75
                else:
                    session.add(PokemonCapturado(pokeapi_id=res["pokemon_id"], nivel=1, xp=0, en_equipo=False))
                    registrar_pokedex(session, res["pokemon_id"])
                
    return res

def completar_mision(session: Session, mision_id: int):
    """
    Función principal que se llama cuando el usuario pulsa "Completar" en la UI.
    """
    mision = session.get(MisionRegular, mision_id)
    if not mision or mision.completada:
        return False, {}
        
    mision.completada = True
    
    # 1. Obtener usuario para recompensas base (XP, Monedas)
    usuario = session.execute(select(Usuario)).scalars().first()
    if not usuario:
        usuario = Usuario()
        session.add(usuario)
        session.flush()
        
    dificultad_mision = mision.banco_mision.dificultad if mision.banco_mision else None
    
    if dificultad_mision == Dificultad.MUY_FACIL:
        xp_ganada = 10
        monedas_ganadas = 1
    elif dificultad_mision == Dificultad.FACIL:
        xp_ganada = 20
        monedas_ganadas = 5
    elif dificultad_mision == Dificultad.NORMAL:
        xp_ganada = 50
        monedas_ganadas = 10
    elif dificultad_mision == Dificultad.DIFICIL:
        xp_ganada = 150
        monedas_ganadas = 30
    else:
        xp_ganada = 50
        monedas_ganadas = 10
        
    if usuario.boost_xp_restantes > 0:
        xp_ganada = int(xp_ganada * 1.5)
        usuario.boost_xp_restantes -= 1
        
    bonus_xp = 0
    combo_diario = False
    combo_semanal = False
    
    if mision.tipo == MissionType.DIARIA:
        hoy = date.today()
        lista_diaria = session.execute(select(ListaTareas).where(ListaTareas.nombre == "Misiones Diarias")).scalars().first()
        if lista_diaria:
            diarias_hoy = session.execute(
                select(MisionRegular).join(BancoMisiones).where(
                    and_(MisionRegular.tipo == MissionType.DIARIA, 
                         MisionRegular.fecha_asignacion == hoy,
                         MisionRegular.id != mision.id,
                         BancoMisiones.lista_id == lista_diaria.id)
                )
            ).scalars().all()
            if len(diarias_hoy) == 2 and all(m.completada for m in diarias_hoy):
                bonus_xp = 30
                combo_diario = True
            
    elif mision.tipo == MissionType.SEMANAL:
        from datetime import timedelta
        hoy = date.today()
        lunes_esta_semana = hoy - timedelta(days=hoy.weekday())
        lista_semanal = session.execute(select(ListaTareas).where(ListaTareas.nombre == "Misiones Semanales")).scalars().first()
        if lista_semanal:
            semanales_esta_semana = session.execute(
                select(MisionRegular).join(BancoMisiones).where(
                    and_(MisionRegular.tipo == MissionType.SEMANAL, 
                         MisionRegular.fecha_asignacion >= lunes_esta_semana,
                         MisionRegular.id != mision.id,
                         BancoMisiones.lista_id == lista_semanal.id)
                )
            ).scalars().all()
            if len(semanales_esta_semana) == 2 and all(m.completada for m in semanales_esta_semana):
                bonus_xp = 75
                combo_semanal = True
            
    xp_ganada += bonus_xp
    usuario.xp_actual += xp_ganada
    usuario.monedas += monedas_ganadas
    
    nivel_usuario_subido = False
    niveles_subidos_usuario = 0
    monedas_bonus_nivel = 0
    objeto_nivel = None
    
    while True:
        xp_necesaria_usuario = min(50 + (usuario.nivel - 1) * 25, 500)
        if usuario.xp_actual >= xp_necesaria_usuario:
            usuario.xp_actual -= xp_necesaria_usuario
            usuario.nivel += 1
            nivel_usuario_subido = True
            niveles_subidos_usuario += 1
            
            recompensa_monedas = xp_necesaria_usuario // 10
            usuario.monedas += recompensa_monedas
            monedas_bonus_nivel += recompensa_monedas
            
            if usuario.nivel % 15 == 0:
                objeto = ItemType.FOSIL_MISTERIOSO
            elif usuario.nivel % 5 == 0:
                objeto = ItemType.HUEVO
                
            if usuario.nivel % 5 == 0:
                inv = session.execute(select(Inventario).where(Inventario.tipo_objeto == objeto)).scalar_one_or_none()
                if inv:
                    inv.cantidad += 1
                else:
                    session.add(Inventario(tipo_objeto=objeto, cantidad=1))
                objeto_nivel = objeto.value
        else:
            break
    
    # 2. Huevo
    huevo_progreso = avanzar_huevo(session)
    
    # 3. Daño al Boss
    dano_jefe, jefe = calcular_y_aplicar_dano_jefe(session, dificultad_mision)
    
    # 4. Loot
    loot = drop_loot(session, dificultad_mision)
    
    # 5. Equipo (XP)
    equipo = session.execute(
        select(PokemonCapturado).where(PokemonCapturado.en_equipo == True)
    ).scalars().all()
    pokemon_subidas = []
    
    import pokemon_metadata
    
    for pk in equipo:
        pk.xp += xp_ganada
        niveles_subidos = 0
        
        meta = pokemon_metadata.POKEMON_METADATA.get(pk.pokeapi_id, {})
        rareza = meta.get("rareza", "Común")
        
        if rareza == "Legendario":
            tope_xp = 200
        elif rareza == "Muy Raro":
            tope_xp = 200
        elif rareza == "Raro":
            tope_xp = 150
        else:
            tope_xp = 100
            
        # Subida de nivel recursiva (por si gana mucha XP de golpe)
        while True:
            if pk.nivel >= 100:
                pk.nivel = 100
                pk.xp = 0
                break
                
            xp_necesaria = min(25 + (pk.nivel * 15), tope_xp)
            if pk.xp >= xp_necesaria:
                pk.xp -= xp_necesaria
                pk.nivel += 1
                niveles_subidos += 1
            else:
                break
                
        if niveles_subidos > 0:
            evolucion_data = None
            nuevo_pokeapi_id = pokeapi.check_evolution(pk.pokeapi_id, pk.nivel)
            
            if nuevo_pokeapi_id:
                # Verificar si ya poseemos la forma evolucionada
                ya_lo_tiene = session.execute(
                    select(PokemonCapturado).where(PokemonCapturado.pokeapi_id == nuevo_pokeapi_id)
                ).scalars().first() is not None
                
                if not ya_lo_tiene:
                    evolucion_data = {
                        "viejo_id": pk.pokeapi_id,
                        "nuevo_id": nuevo_pokeapi_id
                    }
                    pk.pokeapi_id = nuevo_pokeapi_id
                    registrar_pokedex(session, nuevo_pokeapi_id)
                
            pokemon_subidas.append({
                "pokeapi_id": pk.pokeapi_id,
                "nivel": pk.nivel,
                "evolucion": evolucion_data
            })
            
    # Combos ya calculados arriba
            
    # 8. Estadísticas
    stats = session.execute(select(Estadisticas)).scalars().first()
    if not stats:
        stats = Estadisticas()
        session.add(stats)
        session.flush()
        
    dif = mision.banco_mision.dificultad
    if dif == Dificultad.FACIL:
        if stats.encuentro_comun_progreso < 5:
            stats.encuentro_comun_progreso = min(5, stats.encuentro_comun_progreso + 1)
    elif dif == Dificultad.NORMAL:
        if stats.encuentro_raro_progreso < 5:
            stats.encuentro_raro_progreso = min(5, stats.encuentro_raro_progreso + 1)
    elif dif == Dificultad.DIFICIL:
        if stats.encuentro_raro_progreso < 5:
            stats.encuentro_raro_progreso = min(5, stats.encuentro_raro_progreso + 2)
    # 9. Recurrencia
    if mision.banco_mision.recurrencia_dias and mision.banco_mision.recurrencia_dias > 0:
        from datetime import timedelta
        if mision.fecha_limite:
            nueva_fecha = mision.fecha_limite + timedelta(days=mision.banco_mision.recurrencia_dias)
        else:
            nueva_fecha = date.today() + timedelta(days=mision.banco_mision.recurrencia_dias)
            
        nueva_mision_instancia = MisionRegular(
            banco_mision_id=mision.banco_mision_id,
            tipo=mision.tipo,
            completada=False,
            fecha_asignacion=nueva_fecha,
            fecha_limite=nueva_fecha,
            orden=mision.orden
        )
        session.add(nueva_mision_instancia)

    # Commit a todo
    session.commit()
    
    check_achievements(session)

    
    resultados = {
        "xp_ganada": xp_ganada,
        "monedas_ganadas": monedas_ganadas,
        "loot": loot.value if loot else None,
        "dano_jefe": dano_jefe,
        "jefe_hp_actual": jefe.hp_actual if jefe else None,
        "jefe_derrotado": jefe.completada if jefe else False,
        "huevo_progreso": huevo_progreso,
        "combo_diario": combo_diario,
        "combo_semanal": combo_semanal,
        "bonus_xp": bonus_xp,
        "pokemon_subidas": pokemon_subidas,
        "nivel_usuario_subido": nivel_usuario_subido,
        "niveles_subidos_usuario": niveles_subidos_usuario,
        "nuevo_nivel_usuario": usuario.nivel,
        "monedas_bonus_nivel": monedas_bonus_nivel,
        "objeto_nivel": objeto_nivel
    }
    
    return True, resultados

def canjear_fosil_misterioso(session: Session, eleccion: ItemType):
    """
    Consume un Fósil Misterioso y otorga el fósil elegido.
    """
    inv_mist = session.execute(
        select(Inventario).where(Inventario.tipo_objeto == ItemType.FOSIL_MISTERIOSO)
    ).scalars().first()
    
    if not inv_mist or inv_mist.cantidad < 1:
        return False, "No tienes ningún Fósil Misterioso."
        
    inv_mist.cantidad -= 1
    
    inv_elegido = session.execute(
        select(Inventario).where(Inventario.tipo_objeto == eleccion)
    ).scalars().first()
    
    if inv_elegido:
        inv_elegido.cantidad += 1
    else:
        session.add(Inventario(tipo_objeto=eleccion, cantidad=1))
        
    session.commit()
    return True, f"¡Has obtenido un {eleccion.value}!"

def check_achievements(session: Session) -> list[str]:
    """
    Evalúa los logros y devuelve una lista de los IDs de logros recién desbloqueados.
    """
    desbloqueados = session.execute(select(LogroDesbloqueado.logro_id)).scalars().all()
    nuevos_logros = []
    
    usuario = session.get(Usuario, 1)
    if not usuario: return []
    
    estadisticas = session.get(Estadisticas, 1)
    if not estadisticas:
        estadisticas = Estadisticas()
        session.add(estadisticas)
        session.flush()
        
    misiones_completadas = session.execute(
        select(func.count(MisionRegular.id)).where(MisionRegular.completada == True)
    ).scalar() or 0
    
    pokedex_size = session.execute(
        select(func.count(RegistroPokedex.id))
    ).scalar() or 0
    
    jefes_derrotados = session.execute(
        select(func.count(JefeMisionPrincipal.id)).where(JefeMisionPrincipal.completada == True)
    ).scalar() or 0
    
    condiciones = {
        "tareas_1": misiones_completadas >= 1,
        "tareas_100": misiones_completadas >= 100,
        "pokedex_1": pokedex_size >= 1,
        "pokedex_50": pokedex_size >= 50,
        "evolucion_10": estadisticas.pokemon_evolucionados >= 10,
        "huevo_1": estadisticas.huevos_eclosionados >= 1,
        "monedas_10000": usuario.monedas >= 10000,
        "gasto_5000": estadisticas.monedas_gastadas >= 5000,
        "objetos_20": estadisticas.objetos_usados >= 20,
        "boss_1": jefes_derrotados >= 1,
        "boss_10": jefes_derrotados >= 10,
    }
    
    for logro_id, cumplido in condiciones.items():
        if cumplido and logro_id not in desbloqueados:
            session.add(LogroDesbloqueado(logro_id=logro_id))
            nuevos_logros.append(logro_id)
            
    if "legendario_1" not in desbloqueados:
        legendaries = [144, 145, 146, 150, 151, 243, 244, 245, 249, 250, 251, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 483, 484, 487]
        capturados = session.execute(select(RegistroPokedex.pokeapi_id)).scalars().all()
        if any(p in legendaries for p in capturados):
            session.add(LogroDesbloqueado(logro_id="legendario_1"))
            nuevos_logros.append("legendario_1")
            
    if nuevos_logros:
        session.commit()
        
    return nuevos_logros

def check_and_spawn_monthly_boss(session: Session):
    now = datetime.now()
    mes_actual = f"{now.month:02d}/{now.year}"
    titulo_esperado = f"Jefe {mes_actual}"
    
    jefes = session.execute(select(JefeMisionPrincipal)).scalars().all()
    
    tiene_jefe_este_mes = False
    ultimo_pokemon_id = None
    
    if jefes:
        ultimo_jefe = max(jefes, key=lambda x: x.id)
        ultimo_pokemon_id = ultimo_jefe.pokemon_id
        
    for j in jefes:
        if titulo_esperado in j.titulo:
            tiene_jefe_este_mes = True
        elif not j.completada:
            session.delete(j)
            
    if tiene_jefe_este_mes:
        session.commit()
        return
        
    import pokemon_metadata
    
    pool = []
    for pid, meta in pokemon_metadata.POKEMON_METADATA.items():
        if meta.get("metodo") and "Boss" in meta["metodo"]:
            pool.append(pid)
            
    capturados = session.execute(select(PokemonCapturado.pokeapi_id)).scalars().all()
    disponibles = [p for p in pool if p not in capturados]
    
    # Excluir el boss del mes anterior para que no se repita 2 meses seguidos
    if ultimo_pokemon_id and ultimo_pokemon_id in disponibles and len(disponibles) > 1:
        disponibles.remove(ultimo_pokemon_id)
    
    if disponibles:
        nuevo_id = random.choice(disponibles)
        
        usuario = session.get(Usuario, 1)
        nivel_usuario = usuario.nivel if usuario else 1
        hp_calc = 20000 + (nivel_usuario * 500)
        
        nuevo_jefe = JefeMisionPrincipal(
            titulo=titulo_esperado,
            pokemon_id=nuevo_id,
            nivel=nivel_usuario,
            hp_maximo=hp_calc,
            hp_actual=hp_calc,
            tier=BossTier.B,
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

def comprar_recompensa_personal(session: Session, id_recompensa: int):
    rec = session.execute(select(RecompensaPersonal).where(RecompensaPersonal.id == id_recompensa)).scalars().first()
    if not rec:
        return False, "Recompensa no encontrada"
        
    usuario = session.execute(select(Usuario)).scalars().first()
    if usuario.monedas < rec.precio:
        return False, "Monedas insuficientes"
        
    usuario.monedas -= rec.precio
    
    # Registrar estadísticas
    stats = session.execute(select(Estadisticas)).scalars().first()
    if stats:
        stats.monedas_gastadas += rec.precio
        
    session.commit()
    check_achievements(session) # Por si completa el logro de gastar monedas
    return True, f"¡Disfruta de tu recompensa: {rec.nombre}!"


def update_system_missions(session: Session):
    hoy = date.today()
    
    # ==========================================
    # MISIONES DIARIAS
    # ==========================================
    lista_diaria = session.execute(select(ListaTareas).where(ListaTareas.nombre == "Misiones Diarias")).scalars().first()
    if lista_diaria:
        # Check if we generated missions for today
        generadas_hoy = session.execute(
            select(func.count(MisionRegular.id)).join(BancoMisiones).where(
                and_(
                    BancoMisiones.lista_id == lista_diaria.id,
                    MisionRegular.fecha_asignacion == hoy
                )
            )
        ).scalar()
        
        if generadas_hoy == 0:
            # Delete uncompleted missions from previous days
            viejas_no_completadas = session.execute(
                select(MisionRegular).join(BancoMisiones).where(
                    and_(
                        BancoMisiones.lista_id == lista_diaria.id,
                        MisionRegular.completada == False,
                        MisionRegular.fecha_asignacion < hoy
                    )
                )
            ).scalars().all()
            
            for v in viejas_no_completadas:
                session.delete(v)
                
            # Generate 3 new
            banco_diarias = session.execute(
                select(BancoMisiones).where(BancoMisiones.lista_id == lista_diaria.id)
            ).scalars().all()
            
            if banco_diarias:
                seleccionadas = random.sample(banco_diarias, k=min(3, len(banco_diarias)))
                for ms in seleccionadas:
                    ms.dificultad = Dificultad.FACIL
                    ms.prioridad = Prioridad.SIN_PRIORIDAD
                    session.add(MisionRegular(
                        banco_mision=ms,
                        tipo=MissionType.DIARIA,
                        completada=False,
                        fecha_asignacion=hoy,
                        fecha_limite=hoy,
                        orden=0
                    ))

    # ==========================================
    # MISIONES SEMANALES
    # ==========================================
    lista_semanal = session.execute(select(ListaTareas).where(ListaTareas.nombre == "Misiones Semanales")).scalars().first()
    if lista_semanal:
        from datetime import timedelta
        lunes_esta_semana = hoy - timedelta(days=hoy.weekday())
        domingo_esta_semana = lunes_esta_semana + timedelta(days=6)
        
        generadas_esta_semana = session.execute(
            select(func.count(MisionRegular.id)).join(BancoMisiones).where(
                and_(
                    BancoMisiones.lista_id == lista_semanal.id,
                    MisionRegular.fecha_asignacion >= lunes_esta_semana,
                    MisionRegular.fecha_asignacion <= domingo_esta_semana
                )
            )
        ).scalar()
        
        if generadas_esta_semana == 0:
            viejas_no_completadas = session.execute(
                select(MisionRegular).join(BancoMisiones).where(
                    and_(
                        BancoMisiones.lista_id == lista_semanal.id,
                        MisionRegular.completada == False,
                        MisionRegular.fecha_asignacion < lunes_esta_semana
                    )
                )
            ).scalars().all()
            
            for v in viejas_no_completadas:
                session.delete(v)
                
            banco_semanales = session.execute(
                select(BancoMisiones).where(BancoMisiones.lista_id == lista_semanal.id)
            ).scalars().all()
            
            if banco_semanales:
                seleccionadas = random.sample(banco_semanales, k=min(3, len(banco_semanales)))
                for ms in seleccionadas:
                    ms.dificultad = Dificultad.NORMAL
                    ms.prioridad = Prioridad.SIN_PRIORIDAD
                    session.add(MisionRegular(
                        banco_mision=ms,
                        tipo=MissionType.SEMANAL,
                        completada=False,
                        fecha_asignacion=hoy,
                        fecha_limite=domingo_esta_semana,
                        orden=0
                    ))
