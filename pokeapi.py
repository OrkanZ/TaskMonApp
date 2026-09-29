import requests
from typing import Dict, List, Any, Optional

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

# Caché en memoria para evitar llamadas redundantes
_pokemon_cache: Dict[int, Dict[str, Any]] = {}
_type_cache: Dict[str, Dict[str, Any]] = {}
_evolution_cache: Dict[str, Dict[str, Any]] = {}

def get_pokemon_info(pokemon_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene la información básica de un Pokémon (nombre, tipos, sprites, stats).
    """
    if pokemon_id in _pokemon_cache:
        return _pokemon_cache[pokemon_id]
        
    try:
        response = requests.get(f"{POKEAPI_BASE_URL}/pokemon/{pokemon_id}", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Filtramos solo lo que necesitamos para ahorrar memoria
        types = [t["type"]["name"] for t in data["types"]]
        stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
        
        taskmon_attack = max(
            stats.get("attack", 0),
            stats.get("special-attack", 0),
            stats.get("defense", 0),
            stats.get("special-defense", 0)
        )
        
        height_m = data.get("height", 0) / 10.0
        weight_kg = data.get("weight", 0) / 10.0
        
        # Extracción segura de sprites animados de 5a gen (Blanco/Negro)
        anim_front = None
        anim_shiny = None
        try:
            anim_front = data["sprites"]["versions"]["generation-v"]["black-white"]["animated"]["front_default"]
            anim_shiny = data["sprites"]["versions"]["generation-v"]["black-white"]["animated"]["front_shiny"]
        except KeyError:
            pass

        cries = data.get("cries", {})
        
        info = {
            "id": data["id"],
            "name": data["species"]["name"],
            "types": types,
            "sprites": {
                "front_default": data["sprites"].get("front_default"),
                "front_shiny": data["sprites"].get("front_shiny"),
                "official_artwork": data["sprites"].get("other", {}).get("official-artwork", {}).get("front_default"),
                "animated": anim_front,
                "animated_shiny": anim_shiny
            },
            "stats": stats,
            "taskmon_attack": taskmon_attack,
            "height_m": height_m,
            "weight_kg": weight_kg,
            "cries": cries
        }
        
        _pokemon_cache[pokemon_id] = info
        return info
    except requests.RequestException as e:
        print(f"Error al obtener Pokémon {pokemon_id}: {e}")
        return None

_gen5_cache = None

def get_generation_5_pokemon():
    global _gen5_cache
    if _gen5_cache is not None:
        return _gen5_cache
        
    url = "https://pokeapi.co/api/v2/generation/5"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            result = {}
            for s in data["pokemon_species"]:
                pid = int(s["url"].rstrip('/').split('/')[-1])
                result[pid] = s["name"].capitalize()
            _gen5_cache = result
            return result
    except Exception:
        pass
    return {}

_species_cache = {}

def get_pokemon_species_info(pokemon_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene la información de especie de un Pokémon (descripción de la Pokédex).
    """
    if pokemon_id in _species_cache:
        return _species_cache[pokemon_id]
        
    try:
        response = requests.get(f"{POKEAPI_BASE_URL}/pokemon-species/{pokemon_id}", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        flavor_texts = [ft["flavor_text"] for ft in data["flavor_text_entries"] if ft["language"]["name"] == "es"]
        if not flavor_texts:
            flavor_texts = [ft["flavor_text"] for ft in data["flavor_text_entries"] if ft["language"]["name"] == "en"]
            
        description = flavor_texts[0].replace("\n", " ").replace("\f", " ") if flavor_texts else "Descripción no disponible."
        
        info = {
            "description": description,
            "evolution_chain_url": data.get("evolution_chain", {}).get("url")
        }
        
        _species_cache[pokemon_id] = info
        return info
    except Exception as e:
        print(f"Error al obtener especie de Pokémon {pokemon_id}: {e}")
        return None

def check_evolution(pokemon_id: int, current_level: int) -> Optional[int]:
    """
    Comprueba si un Pokémon debe evolucionar en el nivel actual.
    Devuelve la nueva ID si evoluciona, o None en caso contrario.
    """
    species_info = get_pokemon_species_info(pokemon_id)
    if not species_info or not species_info.get("evolution_chain_url"):
        return None
        
    evo_url = species_info["evolution_chain_url"]
    
    if evo_url in _evolution_cache:
        evo_data = _evolution_cache[evo_url]
    else:
        try:
            res = requests.get(evo_url, timeout=5)
            res.raise_for_status()
            evo_data = res.json()
            _evolution_cache[evo_url] = evo_data
        except Exception as e:
            print(f"Error al obtener cadena evolutiva: {e}")
            return None
            
    def search_chain(node, target_id):
        if not node or "species" not in node:
            return None
        node_id = int(node["species"]["url"].rstrip("/").split("/")[-1])
        if node_id == target_id:
            return node
        for next_node in node.get("evolves_to", []):
            result = search_chain(next_node, target_id)
            if result:
                return result
        return None
        
    current_node = search_chain(evo_data.get("chain", {}), pokemon_id)
    if not current_node:
        return None
        
    for evolution in current_node.get("evolves_to", []):
        for detail in evolution.get("evolution_details", []):
            if detail.get("trigger", {}).get("name") == "level-up":
                min_level = detail.get("min_level")
                if min_level and current_level >= min_level:
                    new_id = int(evolution["species"]["url"].rstrip("/").split("/")[-1])
                    return new_id
                    
    return None

def get_type_data(type_name: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos de relaciones de daño de un tipo.
    """
    if type_name in _type_cache:
        return _type_cache[type_name]
        
    try:
        response = requests.get(f"{POKEAPI_BASE_URL}/type/{type_name}", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        damage_relations = data["damage_relations"]
        relations = {
            "double_damage_to": [t["name"] for t in damage_relations["double_damage_to"]],
            "half_damage_to": [t["name"] for t in damage_relations["half_damage_to"]],
            "no_damage_to": [t["name"] for t in damage_relations["no_damage_to"]],
        }
        
        _type_cache[type_name] = relations
        return relations
    except requests.RequestException as e:
        print(f"Error al obtener datos del tipo {type_name}: {e}")
        return None

def get_type_multiplier(attacker_types: List[str], defender_types: List[str]) -> float:
    """
    Calcula el multiplicador de daño basado en las ventajas de tipos.
    Toma en cuenta múltiples tipos del atacante y del defensor.
    Para simplificar, tomaremos la mejor ventaja de los atacantes contra los defensores.
    """
    if not attacker_types or not defender_types:
        return 1.0

    best_multiplier = 0.0

    for atk_type in attacker_types:
        type_data = get_type_data(atk_type)
        if not type_data:
            continue
            
        current_multiplier = 1.0
        for def_type in defender_types:
            if def_type in type_data["double_damage_to"]:
                current_multiplier *= 1.2
            elif def_type in type_data["half_damage_to"] or def_type in type_data["no_damage_to"]:
                current_multiplier *= 0.8
                
        if current_multiplier > best_multiplier:
            best_multiplier = current_multiplier
            
    return best_multiplier if best_multiplier > 0 else 1.0
