import flet as ft
from models import ItemType

ITEM_METADATA = {
    ItemType.POKEBALL: {
        "name": "Pokéball",
        "icon": ft.Icons.CATCHING_POKEMON,
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png",
        "desc": " Permite capturar pokémon salvajes",
        "price": 10,
        "min_level": 1,
        "rareza": "Común",
        "color": ft.Colors.RED_400,
        "usable_from_inventory": False,
        "requires_target": False
    },
    ItemType.ULTRABALL: {
        "name": "Ultraball",
        "icon": ft.Icons.CATCHING_POKEMON,
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/ultra-ball.png",
        "desc": "Permite capturar pokémon salvajes con mayor probabilidad de éxito.",
        "price": 30,
        "min_level": 5,
        "rareza": "Raro",
        "color": ft.Colors.YELLOW_600,
        "usable_from_inventory": False,
        "requires_target": False
    },
    ItemType.MASTERBALL: {
        "name": "Masterball",
        "icon": ft.Icons.CATCHING_POKEMON,
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/master-ball.png",
        "desc": "Permite capturar a cualquier Pokémon salvaje sin fallar.",
        "price": 150,
        "min_level": 10,
        "rareza": "Muy Raro",
        "color": ft.Colors.PURPLE_600,
        "usable_from_inventory": False,
        "requires_target": False
    },
    ItemType.ACELERADOR: {
        "name": "Acelerador Eclosión",
        "icon": ft.Icons.SPEED,
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/exp-share.png",
        "desc": "Avanza 5 tareas en la incubación de tu huevo equipado.",
        "price": 25,
        "min_level": 5,
        "rareza": "Común",
        "color": ft.Colors.BLUE_400,
        "usable_from_inventory": True,
        "requires_target": False
    },
    ItemType.BOOST_XP: {
        "name": "Huevo Suerte",
        "icon": ft.Icons.TRENDING_UP,
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/lucky-egg.png",
        "desc": "Aumenta la experiencia obtenida en misiones en un 50% durante las próximas 5 tareas.",
        "price": 30,
        "min_level": 5,
        "rareza": "Raro",
        "color": ft.Colors.BLUE_400,
        "usable_from_inventory": True,
        "requires_target": False
    },
    ItemType.HUEVO: {
        "name": "Huevo Misterioso",
        "icon": ft.Icons.EGG,
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/mystery-egg.png",
        "desc": "Un misterioso huevo Pokémon. Deberás ponerlo en la incubadora de tu PC para que eclosione.",
        "price": 500,
        "sell_price": 20,
        "rareza": "Muy Raro",
        "color": ft.Colors.GREEN_200,
        "usable_from_inventory": False,
        "requires_target": False
    },
    ItemType.FOSIL_PLUMA: {
        "name": "Fósil Pluma",
        "icon": ft.Icons.PETS,
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/plume-fossil.png",
        "desc": "Un antiguo fósil de pájaro. Podrás revivirlo en la incubadora de tu PC.",
        "price": 1000,
        "sell_price": 20,
        "rareza": "Muy Raro",
        "color": ft.Colors.AMBER_200,
        "usable_from_inventory": False,
        "requires_target": False
    },
    ItemType.FOSIL_TAPA: {
        "name": "Fósil Tapa",
        "icon": ft.Icons.SHIELD,
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/cover-fossil.png",
        "desc": "Un antiguo caparazón fósil. Podrás revivirlo en la incubadora de tu PC.",
        "price": 1000,
        "sell_price": 20,
        "rareza": "Muy Raro",
        "color": ft.Colors.BLUE_GREY_400,
        "usable_from_inventory": False,
        "requires_target": False
    },
    ItemType.FOSIL_MISTERIOSO: {
        "name": "Fósil Misterioso",
        "icon": ft.Icons.QUESTION_MARK,
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/old-amber.png",
        "desc": "Un fósil no identificado. Úsalo desde tu inventario para extraer el Fósil Tapa o el Fósil Pluma.",
        "price": 5000,
        "sell_price": 20,
        "rareza": "Muy Raro",
        "color": ft.Colors.AMBER_400,
        "usable_from_inventory": True,
        "requires_target": False
    },
    ItemType.CEBO: {
        "name": "Baya Meloc",
        "icon": ft.Icons.RESTAURANT,
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/pecha-berry.png",
        "desc": "Duplica las posibilidades de capturar al pokémon durante el siguiente lanzamiento",
        "price": 10,
        "min_level": 1,
        "rareza": "Común",
        "color": ft.Colors.PURPLE_400,
        "usable_from_inventory": False,
        "requires_target": False
    },
    ItemType.CARAMELO_RARO: {
        "name": "Caramelo Raro",
        "icon": ft.Icons.STAR,
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/rare-candy.png",
        "desc": "Sube instantáneamente 1 Nivel al Pokémon seleccionado.",
        "price": 50,
        "min_level": 5,
        "rareza": "Raro",
        "color": ft.Colors.CYAN_400,
        "usable_from_inventory": True,
        "requires_target": True
    },
    ItemType.PIEDRA_HOJA: {
        "name": "Piedra Hoja", "icon": ft.Icons.NATURE, "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/leaf-stone.png", "desc": "Una extraña piedra que hace evolucionar a ciertas especies de Pokémon.",
        "price": 1000, "sell_price": 30, "rareza": "Raro", "color": ft.Colors.GREEN_400, "usable_from_inventory": True, "requires_target": True
    },
    ItemType.PIEDRA_FUEGO: {
        "name": "Piedra Fuego", "icon": ft.Icons.LOCAL_FIRE_DEPARTMENT, "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/fire-stone.png", "desc": "Una extraña piedra que hace evolucionar a ciertas especies de Pokémon.",
        "price": 1000, "sell_price": 30, "rareza": "Raro", "color": ft.Colors.RED_400, "usable_from_inventory": True, "requires_target": True
    },
    ItemType.PIEDRA_AGUA: {
        "name": "Piedra Agua", "icon": ft.Icons.WATER_DROP, "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/water-stone.png", "desc": "Una extraña piedra que hace evolucionar a ciertas especies de Pokémon.",
        "price": 1000, "sell_price": 30, "rareza": "Raro", "color": ft.Colors.BLUE_400, "usable_from_inventory": True, "requires_target": True
    },
    ItemType.PIEDRA_LUNAR: {
        "name": "Piedra Lunar", "icon": ft.Icons.DARK_MODE, "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/moon-stone.png", "desc": "Una extraña piedra que hace evolucionar a ciertas especies de Pokémon.",
        "price": 1000, "sell_price": 30, "rareza": "Raro", "color": ft.Colors.BLUE_GREY_400, "usable_from_inventory": True, "requires_target": True
    },
    ItemType.PIEDRA_INTERCAMBIO: {
        "name": "Piedra Intercambio", "icon": ft.Icons.SWAP_HORIZ, "sprite": "piedra_intercambio.png", "desc": "Una misteriosa piedra que simula las condiciones de una evolución por intercambio.",
        "price": 1500, "sell_price": 30, "rareza": "Raro", "color": ft.Colors.PURPLE_400, "usable_from_inventory": True, "requires_target": True
    },
    ItemType.PIEDRA_DIA: {
        "name": "Piedra Día", "icon": ft.Icons.LIGHT_MODE, "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/shiny-stone.png", "desc": "Una extraña piedra que hace evolucionar a ciertas especies de Pokémon.",
        "price": 1000, "sell_price": 30, "rareza": "Raro", "color": ft.Colors.YELLOW_400, "usable_from_inventory": True, "requires_target": True
    },
    ItemType.PIEDRA_TRUENO: {
        "name": "Piedra Trueno", "icon": ft.Icons.BOLT, "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/thunder-stone.png", "desc": "Una extraña piedra que hace evolucionar a ciertas especies de Pokémon.",
        "price": 1000, "sell_price": 30, "rareza": "Raro", "color": ft.Colors.YELLOW_600, "usable_from_inventory": True, "requires_target": True
    },
    ItemType.PIEDRA_NOCHE: {
        "name": "Piedra Noche", "icon": ft.Icons.NIGHTLIGHT_ROUND, "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/dusk-stone.png", "desc": "Una extraña piedra que hace evolucionar a ciertas especies de Pokémon.",
        "price": 1000, "sell_price": 30, "rareza": "Raro", "color": ft.Colors.DEEP_PURPLE_800, "usable_from_inventory": True, "requires_target": True
    },
    ItemType.PIEDRA_SOLAR: {
        "name": "Piedra Solar", "icon": ft.Icons.WB_SUNNY, "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/sun-stone.png", "desc": "Una extraña piedra que hace evolucionar a ciertas especies de Pokémon.",
        "price": 1000, "sell_price": 30, "rareza": "Raro", "color": ft.Colors.ORANGE_400, "usable_from_inventory": True, "requires_target": True
    }
}

SHOP_INVENTORY = [
    ItemType.POKEBALL,
    ItemType.CEBO,
    ItemType.ACELERADOR,
    ItemType.BOOST_XP,
    ItemType.ULTRABALL,
    ItemType.CARAMELO_RARO,
    ItemType.MASTERBALL
]
