import flet as ft
from database import get_session
from models import PokemonCapturado, RegistroPokedex
from sqlalchemy import select
import pokeapi
import pokemon_metadata

TYPE_COLORS = {
    "normal": ("#A8A77A", "black"),
    "fire": ("#EE8130", "white"),
    "water": ("#6390F0", "white"),
    "electric": ("#F7D02C", "black"),
    "grass": ("#7AC74C", "black"),
    "ice": ("#96D9D6", "black"),
    "fighting": ("#C22E28", "white"),
    "poison": ("#A33EA1", "white"),
    "ground": ("#E2BF65", "black"),
    "flying": ("#A98FF3", "black"),
    "psychic": ("#F95587", "white"),
    "bug": ("#A6B91A", "black"),
    "rock": ("#B6A136", "black"),
    "ghost": ("#735797", "white"),
    "dragon": ("#6F35FC", "white"),
    "dark": ("#705848", "white"),
    "steel": ("#B7B7CE", "black"),
    "fairy": ("#D685AD", "black"),
}

DARK_TYPE_COLORS = {
    "normal": "#1A1A15",
    "fire": "#2A1005",
    "water": "#0A152A",
    "electric": "#1F1A05",
    "grass": "#10200A",
    "ice": "#0A2020",
    "fighting": "#250505",
    "poison": "#1A051A",
    "ground": "#201505",
    "flying": "#151025",
    "psychic": "#250510",
    "bug": "#151A05",
    "rock": "#1A1505",
    "ghost": "#100A1A",
    "dragon": "#100525",
    "dark": "#100D0B",
    "steel": "#15151A",
    "fairy": "#25101A",
}

class PokedexView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        
        self.header = ft.Text("GENERACIÓN 5", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)
        
        self.grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=120,
            child_aspect_ratio=0.75,
            spacing=10,
            run_spacing=10,
        )
        
        self.content = ft.Column([
            ft.Container(height=10),
            ft.Row([self.header], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=5),
            self.grid
        ], expand=True)
        
        self.modal = ft.AlertDialog(
            modal=False,
            content_padding=0,
            bgcolor=ft.Colors.TRANSPARENT
        )

    def close_modal(self, e=None):
        self.modal.open = False
        if self.page:
            self.page.update()

    def show_details(self, e):
        data = e.control.data
        if not data: return
        
        if isinstance(data, tuple):
            pid, is_caught = data
        else:
            pid = data
            is_caught = True
            
        if self.page:
            if self.modal not in self.page.overlay:
                self.page.overlay.append(self.modal)
            self.modal.content = ft.Container(
                content=ft.Column([
                    ft.Text("Descargando datos...", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
                    ft.ProgressBar()
                ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                bgcolor="#1A1A1A",
                border_radius=15
            )
            self.modal.open = True
            self.page.update()
            
        # Obtener datos reales
        info = pokeapi.get_pokemon_info(pid)
        species = pokeapi.get_pokemon_species_info(pid)
        
        if not info or not species:
            self.modal.content = ft.Container(
                content=ft.Column([
                    ft.Text("Error", color=ft.Colors.RED_400, weight=ft.FontWeight.BOLD, size=18),
                    ft.Text("No se pudo cargar la información."),
                    ft.Row([ft.TextButton("Cerrar", on_click=self.close_modal)], alignment=ft.MainAxisAlignment.END)
                ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                bgcolor="#1A1A1A",
                border_radius=15
            )
            if self.page:
                self.page.update()
            return
            
        meta = pokemon_metadata.POKEMON_METADATA.get(pid, {})
        metodo = meta.get("metodo", "Desconocido")
        
        if is_caught:
            rareza = meta.get("rareza", "Desconocida")
            anim_src = info["sprites"].get("animated") or info["sprites"].get("official_artwork") or info["sprites"].get("front_default")
            img = ft.Image(src=anim_src, width=120, height=120, fit="contain")
            
            primary_type = info["types"][0].lower() if info["types"] else "normal"
            primary_bg_color = TYPE_COLORS.get(primary_type, ("#777777", "white"))[0]
            
            modal_bg_color = None
            bg_gradient = None
            if len(info["types"]) > 1:
                t1 = info["types"][0].lower()
                t2 = info["types"][1].lower()
                c1 = DARK_TYPE_COLORS.get(t1, "#1A1A1A")
                c2 = DARK_TYPE_COLORS.get(t2, "#1A1A1A")
                bg_gradient = ft.LinearGradient(
                    begin=ft.Alignment(-1.0, -1.0),
                    end=ft.Alignment(1.0, 1.0),
                    colors=[c1, c2]
                )
            else:
                modal_bg_color = DARK_TYPE_COLORS.get(primary_type, "#1A1A1A")
            
            type_chips = []
            for t in info["types"]:
                chip_bg_color, text_color = TYPE_COLORS.get(t.lower(), ("#777777", "white"))
                type_chips.append(
                    ft.Container(
                        content=ft.Text(t.upper(), size=10, weight=ft.FontWeight.BOLD, color=text_color),
                        padding=5,
                        bgcolor=chip_bg_color,
                        border_radius=5
                    )
                )
                
            types_row = ft.Row(type_chips, alignment=ft.MainAxisAlignment.CENTER)
            
            evolucion = meta.get("evolucion", None)
            
            text_color_rareza = ft.Colors.GREY_500
            num_stars = 1
            rareza_weight = ft.FontWeight.NORMAL
            
            if rareza == "Legendario": 
                text_color_rareza = ft.Colors.AMBER_400
                num_stars = 3
                rareza_weight = ft.FontWeight.W_900
            elif rareza == "Muy Raro": 
                text_color_rareza = ft.Colors.PURPLE_400
                num_stars = 3
                rareza_weight = ft.FontWeight.BOLD
            elif rareza == "Raro": 
                text_color_rareza = ft.Colors.BLUE_400
                num_stars = 2
                rareza_weight = ft.FontWeight.BOLD
                
            rareza_stars = [ft.Icon(ft.Icons.STAR, size=16, color=text_color_rareza) for _ in range(num_stars)]
            
            if rareza in ["Legendario", "Muy Raro"]:
                # Efecto Premium con degradado
                if rareza == "Legendario":
                    grad_colors = [ft.Colors.YELLOW_300, ft.Colors.AMBER_500, ft.Colors.ORANGE_600]
                else:
                    grad_colors = [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
                    
                gradient = ft.LinearGradient(
                    begin=ft.Alignment(-1.0, -1.0),
                    end=ft.Alignment(1.0, 1.0),
                    colors=grad_colors
                )
                rareza_row = ft.ShaderMask(
                    content=ft.Row([
                        ft.Text(rareza.upper(), size=14, weight=rareza_weight),
                        ft.Row(rareza_stars, spacing=0)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
                    blend_mode=ft.BlendMode.SRC_IN,
                    shader=gradient
                )
            else:
                rareza_row = ft.Row([
                    ft.Text(rareza.upper(), size=12, color=text_color_rareza, weight=rareza_weight),
                    ft.Row(rareza_stars, spacing=0)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=5)
            
            with get_session() as session:
                en_pc = session.execute(
                    select(PokemonCapturado).where(PokemonCapturado.pokeapi_id == pid)
                ).scalars().first() is not None
                
            en_pc_texto = "Si" if en_pc else "No"
            color_texto_pc = ft.Colors.GREEN_400 if en_pc else ft.Colors.RED_400
            
            stats = [
                ft.Text(f"⚔️ Poder Base: {info['taskmon_attack']}", size=14, color=ft.Colors.RED_400, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text("📏 Altura: ", size=12, color=ft.Colors.WHITE_70),
                    ft.Text(f"{info['height_m']} m", size=12, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                ft.Row([
                    ft.Text("⚖️ Peso: ", size=12, color=ft.Colors.WHITE_70),
                    ft.Text(f"{info['weight_kg']} kg", size=12, color=ft.Colors.AMBER_400, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                ft.Row([
                    ft.Text("🎯 Obtención: ", size=12, color=ft.Colors.WHITE_70),
                    ft.Text(f"{metodo}", size=12, color=ft.Colors.CYAN_300, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
            ]
            if evolucion:
                stats.append(ft.Row([
                    ft.Text("✨ Evolución: ", size=12, color=ft.Colors.WHITE_70),
                    ft.Text(f"{evolucion}", size=12, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2))
                
            stats.append(ft.Row([
                ft.Text("📦 Lo tienes: ", size=12, color=ft.Colors.WHITE_70),
                ft.Text(f"{en_pc_texto}", size=12, color=color_texto_pc, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=2))
            
            stats_col = ft.Column(stats, spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            desc = ft.Text(f'"{species["description"]}"', size=12, color=ft.Colors.WHITE_70, text_align=ft.TextAlign.CENTER, italic=True)
            
            if rareza in ["Legendario", "Muy Raro"]:
                if rareza == "Legendario":
                    title_grad = [ft.Colors.YELLOW_300, ft.Colors.AMBER_500, ft.Colors.ORANGE_600]
                else:
                    title_grad = [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
                title_text = ft.ShaderMask(
                    content=ft.Text(f"#{pid} - {info['name'].capitalize()}", weight=ft.FontWeight.W_900, text_align=ft.TextAlign.CENTER, size=20),
                    blend_mode=ft.BlendMode.SRC_IN,
                    shader=ft.LinearGradient(
                        begin=ft.Alignment(-1.0, -1.0),
                        end=ft.Alignment(1.0, 1.0),
                        colors=title_grad
                    )
                )
            else:
                title_text = ft.Text(f"#{pid} - {info['name'].capitalize()}", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.Colors.AMBER_400, size=18)
        
        else:
            anim_src = info["sprites"].get("front_default") 
            img = ft.Image(src=anim_src, width=120, height=120, fit="contain", color=ft.Colors.BLACK, color_blend_mode=ft.BlendMode.SRC_IN)
            types_row = ft.Row([
                ft.Container(
                    content=ft.Text("???", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    padding=5, bgcolor=ft.Colors.GREY_800, border_radius=5
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
            
            rareza_row = ft.Row([
                ft.Text("???", size=12, color=ft.Colors.GREY_500, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER)
            
            evolucion = meta.get("evolucion", None)
            
            stats_list = [
                ft.Text(f"🎯 Obtención: {metodo}", size=14, color=ft.Colors.CYAN_300, weight=ft.FontWeight.BOLD)
            ]
            
            if evolucion:
                stats_list.append(ft.Text(f"✨ Evolución: {evolucion}", size=12, color=ft.Colors.GREEN_400))
                
            stats_col = ft.Column(stats_list, spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            desc = ft.Text("Sigue completando tareas o busca huevos para descubrir a este Pokémon.", size=12, color=ft.Colors.WHITE_54, text_align=ft.TextAlign.CENTER, italic=True)
            title_text = ft.Text(f"#{pid} - {info['name'].capitalize()}", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.Colors.GREY_500, size=18)
            
            modal_bg_color = "#1A1A1A"
            bg_gradient = None
            primary_bg_color = ft.Colors.WHITE_24
            
        self.modal.content = ft.Container(
            content=ft.Column([
                title_text,
                ft.Container(height=5),
                ft.Row([img], alignment=ft.MainAxisAlignment.CENTER),
                types_row,
                ft.Container(height=2),
                rareza_row,
                ft.Divider(color=primary_bg_color),
                stats_col,
                ft.Divider(color=primary_bg_color),
                desc,
                ft.Container(height=10),
                ft.Row([ft.TextButton("Cerrar", on_click=self.close_modal)], alignment=ft.MainAxisAlignment.END)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
            width=280,
            padding=20,
            bgcolor=modal_bg_color,
            gradient=bg_gradient,
            border_radius=15
        )
        
        if self.page:
            self.page.update()

    def did_mount(self):
        self.load_data()

    def load_data(self):
        self.grid.controls.clear()
        
        gen5_data = pokeapi.get_generation_5_pokemon()
        
        with get_session() as session:
            caught_list = session.execute(
                select(RegistroPokedex.pokeapi_id)
            ).scalars().all()
            caught_set = set(caught_list)
            
            for pid in sorted(gen5_data.keys()):
                is_caught = pid in caught_set
                name = gen5_data[pid]
                
                meta = pokemon_metadata.POKEMON_METADATA.get(pid, {})
                rareza = meta.get("rareza", "Bajo")
                
                if is_caught:
                    if rareza == "Legendario": border_color = ft.Colors.AMBER_400
                    elif rareza == "Muy Raro": border_color = ft.Colors.PURPLE_400
                    elif rareza == "Raro": border_color = ft.Colors.BLUE_400
                    else: border_color = ft.Colors.GREY_400
                else:
                    border_color = ft.Colors.WHITE_10
                
                sprite_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pid}.png"
                
                img = ft.Image(
                    src=sprite_url, 
                    width=80, 
                    height=80, 
                    fit="contain",
                    color=None if is_caught else ft.Colors.BLACK,
                    color_blend_mode=ft.BlendMode.SRC_IN if not is_caught else None
                )
                
                inner_content = ft.Column([
                        img,
                        ft.Text(f"#{pid}", size=12, color=ft.Colors.AMBER_700 if is_caught else ft.Colors.WHITE_30, weight=ft.FontWeight.BOLD),
                        ft.Text(name, size=12, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE if is_caught else ft.Colors.WHITE_54, weight=ft.FontWeight.W_600)
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)

                if is_caught and rareza in ["Legendario", "Muy Raro"]:
                    if rareza == "Legendario":
                        grad_colors = [ft.Colors.YELLOW_300, ft.Colors.AMBER_500, ft.Colors.ORANGE_600]
                    else:
                        grad_colors = [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
                        
                    card = ft.Container(
                        content=ft.Container(
                            content=inner_content,
                            bgcolor="#1B2A1B",
                            border_radius=10,
                            padding=3
                        ),
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1.0, -1.0),
                            end=ft.Alignment(1.0, 1.0),
                            colors=grad_colors
                        ),
                        border_radius=12,
                        padding=2,
                        on_click=self.show_details,
                        data=(pid, True)
                    )
                else:
                    card = ft.Container(
                        content=inner_content,
                        bgcolor="#1B2A1B" if is_caught else "#111111", 
                        border_radius=10, 
                        border=ft.Border.all(2, border_color),
                        padding=5,
                        on_click=self.show_details,
                        data=(pid, is_caught)
                    )
                
                self.grid.controls.append(card)
                
        try:
            self.update()
        except Exception:
            pass
