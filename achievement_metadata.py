import flet as ft

class AchievementCategory:
    PRODUCTIVIDAD = "Productividad y Constancia"
    COLECCION = "Coleccionista Pokémon"
    ECONOMIA = "Economía y Objetos"
    COMBATE = "Combates y Jefes"

ACHIEVEMENTS = {
    # Productividad
    "tareas_1": {
        "title": "Primeros Pasos",
        "desc": "Completa tu primera misión.",
        "category": AchievementCategory.PRODUCTIVIDAD,
        "icon": ft.Icons.DIRECTIONS_RUN,
        "color": ft.Colors.BROWN_400
    },
    "tareas_100": {
        "title": "Máquina de Trabajar",
        "desc": "Completa 100 misiones en total.",
        "category": AchievementCategory.PRODUCTIVIDAD,
        "icon": ft.Icons.PRECISION_MANUFACTURING,
        "color": ft.Colors.AMBER_400
    },
    "tareas_10_dia": {
        "title": "Imparable",
        "desc": "Completa 10 misiones en un solo día.",
        "category": AchievementCategory.PRODUCTIVIDAD,
        "icon": ft.Icons.LOCAL_FIRE_DEPARTMENT,
        "color": ft.Colors.DEEP_ORANGE_500
    },

    # Coleccionista
    "pokedex_1": {
        "title": "Amigo Fiel",
        "desc": "Captura a tu primer Pokémon.",
        "category": AchievementCategory.COLECCION,
        "icon": ft.Icons.FAVORITE,
        "color": ft.Colors.RED_400
    },
    "pokedex_50": {
        "title": "Investigador Pokémon",
        "desc": "Registra 50 especies diferentes en tu Pokédex.",
        "category": AchievementCategory.COLECCION,
        "icon": ft.Icons.MENU_BOOK,
        "color": ft.Colors.BLUE_400
    },
    "legendario_1": {
        "title": "Buscador de Mitos",
        "desc": "Captura a tu primer Pokémon Legendario.",
        "category": AchievementCategory.COLECCION,
        "icon": ft.Icons.STARS,
        "color": ft.Colors.PURPLE_400
    },
    "evolucion_10": {
        "title": "Biólogo Evolutivo",
        "desc": "Haz evolucionar a 10 Pokémon.",
        "category": AchievementCategory.COLECCION,
        "icon": ft.Icons.CHANGE_CIRCLE,
        "color": ft.Colors.GREEN_400
    },

    # Economía y Objetos
    "huevo_1": {
        "title": "Paso a Paso",
        "desc": "Eclosiona tu primer huevo Pokémon.",
        "category": AchievementCategory.ECONOMIA,
        "icon": ft.Icons.EGG,
        "color": ft.Colors.YELLOW_300
    },
    "monedas_10000": {
        "title": "Amasando Fortuna",
        "desc": "Acumula un total de 10,000 monedas.",
        "category": AchievementCategory.ECONOMIA,
        "icon": ft.Icons.MONETIZATION_ON,
        "color": ft.Colors.AMBER_500
    },
    "gasto_5000": {
        "title": "Cliente VIP",
        "desc": "Gasta un total de 5,000 monedas en la tienda.",
        "category": AchievementCategory.ECONOMIA,
        "icon": ft.Icons.SHOPPING_CART,
        "color": ft.Colors.LIGHT_BLUE_400
    },
    "objetos_20": {
        "title": "Bien Preparado",
        "desc": "Usa 20 objetos desde tu inventario.",
        "category": AchievementCategory.ECONOMIA,
        "icon": ft.Icons.BACKPACK,
        "color": ft.Colors.BROWN_500
    },

    # Combates y Jefes
    "boss_1": {
        "title": "Salvador del Día",
        "desc": "Derrota a tu primer Jefe de Misión Principal.",
        "category": AchievementCategory.COMBATE,
        "icon": ft.Icons.SHIELD,
        "color": ft.Colors.BLUE_GREY_400
    },
    "boss_10": {
        "title": "Héroe Implacable",
        "desc": "Derrota a 10 Jefes distintos.",
        "category": AchievementCategory.COMBATE,
        "icon": ft.Icons.GAVEL,
        "color": ft.Colors.YELLOW_700
    },
    "dano_500": {
        "title": "Golpe Crítico",
        "desc": "Haz más de 500 de daño a un Jefe en un solo ataque.",
        "category": AchievementCategory.COMBATE,
        "icon": ft.Icons.FLASH_ON,
        "color": ft.Colors.RED_ACCENT_400
    }
}
