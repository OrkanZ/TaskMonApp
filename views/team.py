import flet as ft
from database import get_session
from models import PokemonCapturado, Huevo
from sqlalchemy import select
import pokeapi
import pokemon_metadata
import asyncio
from views.pokedex import TYPE_COLORS, DARK_TYPE_COLORS

class TeamView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.bgcolor = "#0B131D" # Azul muy oscuro y suave para el fondo de toda la pestaña
        self.padding = 20
        
        self.team_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        
        self.egg_progress = ft.ProgressBar(value=0, width=200, color=ft.Colors.GREEN_ACCENT_400, bgcolor=ft.Colors.GREEN_900)
        self.egg_text = ft.Text("Huevo Misterioso", weight=ft.FontWeight.W_600)
        self.egg_status = ft.Text("0/0", color=ft.Colors.WHITE_54)
        
        # Modal para el PC
        self.pc_grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=100,
            child_aspect_ratio=0.7,
            spacing=10,
            run_spacing=10,
        )
        self.pc_modal = ft.AlertDialog(
            modal=False,
            title=ft.Text("Tu PC - Selecciona un Pokémon", text_align=ft.TextAlign.CENTER),
            content=ft.Container(self.pc_grid, width=350, height=400),
            actions=[ft.TextButton("Cancelar", on_click=self.close_pc)],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=15),
            bgcolor="#1A1A1A"
        )
        
        self.details_modal = ft.AlertDialog(
            modal=False,
            content_padding=0,
            bgcolor=ft.Colors.TRANSPARENT,
            elevation=0
        )
        
        # Modal para Ver PC
        self.view_pc_grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=100,
            child_aspect_ratio=0.7,
            spacing=10,
            run_spacing=10,
        )
        self.view_pc_modal = ft.AlertDialog(
            modal=False,
            title=ft.Text("Tu PC - Todos tus Pokémon", text_align=ft.TextAlign.CENTER),
            content=ft.Container(self.view_pc_grid, width=350, height=400),
            actions=[ft.TextButton("Cerrar", on_click=self.close_view_pc)],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=15),
            bgcolor="#1A1A1A"
        )
        
        # Modal para Incubadora
        self.incubator_grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=100,
            child_aspect_ratio=0.7,
            spacing=10,
            run_spacing=10,
        )
        self.incubator_modal = ft.AlertDialog(
            modal=False,
            title=ft.Text("Incubadora - Selecciona un Huevo/Fósil", text_align=ft.TextAlign.CENTER),
            content=ft.Container(self.incubator_grid, width=350, height=400),
            actions=[ft.TextButton("Cancelar", on_click=self.close_incubator)],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=15),
            bgcolor="#1A1A1A"
        )
        
        # Modal para detalles del huevo equipado
        self.egg_details_modal = ft.AlertDialog(
            modal=False,
            shape=ft.RoundedRectangleBorder(radius=15),
            bgcolor="#1A1A1A",
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.egg_icon_container = ft.Container(content=ft.Icon(ft.Icons.EGG, color=ft.Colors.GREEN_200, size=40))
        
        self.content = ft.Column([
            ft.Text("Tus Pokémon activos (Máx 3)", color=ft.Colors.WHITE_70, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            self.team_row,
            ft.Container(height=20),
            ft.FilledButton("💻 Abrir PC", on_click=self.open_view_pc, style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE)),
            ft.Container(height=10),
            ft.Text("Incubadora", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_ACCENT_400),
            ft.Container(
                content=ft.Row([
                    self.egg_icon_container,
                    ft.Column([
                        self.egg_text,
                        self.egg_progress,
                        self.egg_status
                    ])
                ]),
                padding=20,
                border_radius=15,
                bgcolor="#1E2A1E",
                border=ft.Border.all(2, ft.Colors.GREEN_900),
                on_click=self.open_incubator_modal
            )
        ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def close_pc(self, e=None):
        self.pc_modal.open = False
        if self.page:
            self.page.update()

    def close_view_pc(self, e=None):
        self.view_pc_modal.open = False
        if self.page:
            self.page.update()

    async def open_view_pc(self, e):
        self.view_pc_grid.controls = [ft.Container(content=ft.ProgressRing(), alignment=ft.Alignment(0, 0), expand=True)]
        if self.page:
            if self.view_pc_modal not in self.page.overlay:
                self.page.overlay.append(self.view_pc_modal)
            self.view_pc_modal.open = True
            self.page.update()
        
        await asyncio.sleep(0.1)
        self.view_pc_grid.controls.clear()
        import pokemon_metadata
        with get_session() as session:
            # Mostramos todos los capturados (equipo + PC)
            pkmns = session.execute(select(PokemonCapturado).order_by(PokemonCapturado.pokeapi_id)).scalars().all()
            
            for pk in pkmns:
                info = pokeapi.get_pokemon_info(pk.pokeapi_id)
                if not info: continue
                
                sprite_url = info["sprites"].get("front_default")
                name = info["name"].capitalize()
                
                meta = pokemon_metadata.POKEMON_METADATA.get(pk.pokeapi_id, {})
                rareza = meta.get("rareza", "Común")
                
                border_color = ft.Colors.GREY_400
                if rareza == "Legendario": border_color = ft.Colors.AMBER_400
                elif rareza == "Muy Raro": border_color = ft.Colors.PURPLE_400
                elif rareza == "Raro": border_color = ft.Colors.BLUE_400
                
                equipo_badge = ft.Text("⭐ Equipo", size=10, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD) if pk.en_equipo else ft.Container()
                
                inner_content = ft.Column([
                    ft.Image(src=sprite_url, width=50, height=50, fit="contain") if sprite_url else ft.Icon(ft.Icons.HELP, size=50),
                    equipo_badge,
                    ft.Text(f"Nv. {pk.nivel}", size=11, color=ft.Colors.AMBER_400, weight=ft.FontWeight.BOLD),
                    ft.Text(name, size=11, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)

                if rareza in ["Legendario", "Muy Raro"]:
                    grad_colors = [ft.Colors.YELLOW_300, ft.Colors.AMBER_500, ft.Colors.ORANGE_600] if rareza == "Legendario" else [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
                    card = ft.Container(
                        content=ft.Container(
                            content=inner_content,
                            bgcolor="#252525",
                            border_radius=10,
                            padding=2,
                        ),
                        gradient=ft.LinearGradient(begin=ft.Alignment(-1.0, -1.0), end=ft.Alignment(1.0, 1.0), colors=grad_colors),
                        border_radius=12,
                        padding=2,
                        on_click=self.open_details,
                        data=pk.id
                    )
                else:
                    card = ft.Container(
                        content=inner_content,
                        bgcolor="#252525", 
                        border_radius=10, 
                        border=ft.Border.all(2, ft.Colors.GREEN_400) if pk.en_equipo else ft.Border.all(1, border_color),
                        padding=4,
                        on_click=self.open_details,
                        data=pk.id
                    )
                    
                self.view_pc_grid.controls.append(card)
                
        if self.page:
            if self.view_pc_modal not in self.page.overlay:
                self.page.overlay.append(self.view_pc_modal)
            self.view_pc_modal.open = True
            self.page.update()

    def close_incubator(self, e=None):
        self.incubator_modal.open = False
        if self.page:
            self.page.update()
            
    def close_egg_details(self, e=None):
        self.egg_details_modal.open = False
        if self.page:
            self.page.update()

    def unequip_egg(self, e):
        with get_session() as session:
            huevo = session.execute(select(Huevo).where(Huevo.equipado == True)).scalars().first()
            if huevo:
                from models import Inventario
                inv = session.execute(select(Inventario).where(Inventario.tipo_objeto == huevo.tipo_huevo)).scalar_one_or_none()
                if inv:
                    inv.cantidad += 1
                else:
                    session.add(Inventario(tipo_objeto=huevo.tipo_huevo, cantidad=1))
                
                session.delete(huevo)
                session.commit()
                
        self.close_egg_details()
        self.load_data()

    def open_incubator_modal(self, e):
        with get_session() as session:
            huevo_activo = session.execute(select(Huevo).where(Huevo.equipado == True)).scalars().first()
            if huevo_activo:
                import item_metadata
                meta = item_metadata.ITEM_METADATA.get(huevo_activo.tipo_huevo, {})
                icon = meta.get("icon", ft.Icons.EGG)
                sprite_url = meta.get("sprite")
                color = meta.get("color", ft.Colors.GREEN_200)
                name = meta.get("name", "Huevo Misterioso")
                desc = meta.get("desc", "")
                
                pct = huevo_activo.tareas_completadas / max(1, huevo_activo.tareas_requeridas)
                if pct < 0.25:
                    flavor = "Parece que no se moverá en un buen rato..."
                    flavor_color = ft.Colors.WHITE_54
                elif pct < 0.50:
                    flavor = "Ocasionalmente se calienta al tacto."
                    flavor_color = ft.Colors.YELLOW_200
                elif pct < 0.75:
                    flavor = "¡Se escuchan ruidos dentro!"
                    flavor_color = ft.Colors.ORANGE_400
                else:
                    flavor = "¡Ya casi está! ¡Está temblando mucho!"
                    flavor_color = ft.Colors.RED_400
                    
                pb = ft.ProgressBar(value=pct, color=color, bgcolor=ft.Colors.WHITE_10, height=8)
                
                self.egg_details_modal.title = ft.Text(f"Incubadora", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD)
                self.egg_details_modal.content = ft.Container(
                    content=ft.Column([
                        ft.Image(src=sprite_url, width=64, height=64, fit="contain") if sprite_url else ft.Icon(icon, size=64, color=color),
                        ft.Text(name, size=18, weight=ft.FontWeight.BOLD, color=color),
                        ft.Text(desc, size=12, color=ft.Colors.WHITE_70, text_align=ft.TextAlign.CENTER),
                        ft.Divider(color=ft.Colors.WHITE_24),
                        pb,
                        ft.Text(f"{huevo_activo.tareas_completadas}/{huevo_activo.tareas_requeridas} Tareas", size=12, color=ft.Colors.WHITE_54),
                        ft.Text(flavor, size=14, color=flavor_color, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, italic=True),
                        ft.Container(height=10),
                        ft.OutlinedButton("Quitar y devolver al Inventario", on_click=self.unequip_egg, icon=ft.Icons.REMOVE_CIRCLE, style=ft.ButtonStyle(color=ft.Colors.RED_400))
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True, spacing=10),
                    width=300, padding=10
                )
                self.egg_details_modal.actions = [ft.TextButton("Cerrar", on_click=self.close_egg_details)]
                
                if self.page and self.egg_details_modal not in self.page.overlay:
                    self.page.overlay.append(self.egg_details_modal)
                self.egg_details_modal.open = True
                if self.page: self.page.update()
                
                return

            self.incubator_grid.controls.clear()
            from models import Inventario, ItemType
            import item_metadata
            from sqlalchemy import or_, and_
            
            items = session.execute(
                select(Inventario).where(
                    and_(
                        Inventario.cantidad > 0,
                        Inventario.tipo_objeto.in_([ItemType.HUEVO, ItemType.FOSIL_PLUMA, ItemType.FOSIL_TAPA])
                    )
                )
            ).scalars().all()
            
            if not items:
                snack = ft.SnackBar(content=ft.Text("No tienes huevos ni fósiles en el inventario."), bgcolor=ft.Colors.RED_900)
                self.page.overlay.append(snack)
                snack.open = True
                self.page.update()
                return
                
            for inv in items:
                meta = item_metadata.ITEM_METADATA.get(inv.tipo_objeto, {})
                sprite = meta.get("sprite")
                icon = meta.get("icon", ft.Icons.HELP)
                color = meta.get("color", ft.Colors.WHITE)
                
                if sprite:
                    icon_display = ft.Image(src=sprite, width=40, height=40, fit="contain")
                else:
                    icon_display = ft.Icon(icon, size=40, color=color)
                
                card = ft.Container(
                    content=ft.Column([
                        icon_display,
                        ft.Text(meta.get("name", ""), size=11, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
                        ft.Text(f"x{inv.cantidad}", size=10, color=ft.Colors.WHITE_54)
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    bgcolor="#252525", border_radius=10, border=ft.Border.all(1, color),
                    padding=5,
                    on_click=self.equip_incubator_item,
                    data=inv.tipo_objeto
                )
                self.incubator_grid.controls.append(card)
                
        if self.page:
            if self.incubator_modal not in self.page.overlay:
                self.page.overlay.append(self.incubator_modal)
            self.incubator_modal.open = True
            self.page.update()

    def equip_incubator_item(self, e):
        tipo_objeto = e.control.data
        from models import Inventario
        with get_session() as session:
            inv = session.execute(select(Inventario).where(Inventario.tipo_objeto == tipo_objeto)).scalar_one_or_none()
            if inv and inv.cantidad > 0:
                inv.cantidad -= 1
                
                huevo = Huevo(equipado=True, tareas_requeridas=50, tareas_completadas=0, tipo_huevo=tipo_objeto)
                session.add(huevo)
                session.commit()
                
        self.close_incubator()
        self.load_data()

    def close_details(self, e=None):
        self.details_modal.open = False
        if self.page:
            self.page.update()

    def open_details(self, e):
        pk_id = e.control.data
        if not pk_id: return
        
        if self.page and self.details_modal not in self.page.overlay:
            self.page.overlay.append(self.details_modal)
            
        with get_session() as session:
            pk = session.get(PokemonCapturado, pk_id)
            if not pk: return
            
            info = pokeapi.get_pokemon_info(pk.pokeapi_id)
            if not info: return
            
            name = info["name"].capitalize()
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
            
            meta = pokemon_metadata.POKEMON_METADATA.get(pk.pokeapi_id, {})
            rareza = meta.get("rareza", "Común")
            
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
                grad_colors = [ft.Colors.YELLOW_300, ft.Colors.AMBER_500, ft.Colors.ORANGE_600] if rareza == "Legendario" else [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
                gradient = ft.LinearGradient(begin=ft.Alignment(-1.0, -1.0), end=ft.Alignment(1.0, 1.0), colors=grad_colors)
                rareza_row = ft.ShaderMask(
                    content=ft.Row([
                        ft.Text(rareza.upper(), size=14, weight=rareza_weight),
                        ft.Row(rareza_stars, spacing=0)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
                    blend_mode=ft.BlendMode.SRC_IN, shader=gradient
                )
            else:
                rareza_row = ft.Row([
                    ft.Text(rareza.upper(), size=12, color=text_color_rareza, weight=rareza_weight),
                    ft.Row(rareza_stars, spacing=0)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=5)
            
            poder_total = info.get('taskmon_attack', 50) + pk.nivel
            stats = [
                ft.Text(f"⚔️ Poder Total: {poder_total}", size=16, color=ft.Colors.RED_400, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text("📏 Altura: ", size=12, color=ft.Colors.WHITE_70),
                    ft.Text(f"{info['height_m']} m", size=12, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                ft.Row([
                    ft.Text("⚖️ Peso: ", size=12, color=ft.Colors.WHITE_70),
                    ft.Text(f"{info['weight_kg']} kg", size=12, color=ft.Colors.AMBER_400, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
            ]
            stats_col = ft.Column(stats, spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            if pk.nivel >= 100:
                exp_bar = ft.Column([
                    ft.Text("Nivel 100 (MÁX)", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
                    ft.ProgressBar(value=1.0, color=ft.Colors.BLUE_400, bgcolor=ft.Colors.BLUE_900, height=8),
                    ft.Text("Experiencia Máxima", size=10, color=ft.Colors.WHITE_54)
                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            else:
                xp_needed = 25 + (pk.nivel * 15)
                xp_progress = pk.xp / xp_needed if xp_needed > 0 else 0
                
                exp_bar = ft.Column([
                    ft.Text(f"Nivel {pk.nivel}", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
                    ft.ProgressBar(value=xp_progress, color=ft.Colors.BLUE_400, bgcolor=ft.Colors.BLUE_900, height=8),
                    ft.Text(f"{pk.xp} / {xp_needed} XP", size=10, color=ft.Colors.WHITE_54)
                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            if rareza in ["Legendario", "Muy Raro"]:
                if rareza == "Legendario":
                    title_grad = [ft.Colors.YELLOW_300, ft.Colors.AMBER_500, ft.Colors.ORANGE_600]
                else:
                    title_grad = [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
                title_text = ft.ShaderMask(
                    content=ft.Text(f"#{pk.pokeapi_id} - {name}", weight=ft.FontWeight.W_900, text_align=ft.TextAlign.CENTER, size=20),
                    blend_mode=ft.BlendMode.SRC_IN,
                    shader=ft.LinearGradient(
                        begin=ft.Alignment(-1.0, -1.0),
                        end=ft.Alignment(1.0, 1.0),
                        colors=title_grad
                    )
                )
            else:
                title_text = ft.Text(f"#{pk.pokeapi_id} - {name}", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.Colors.AMBER_400, size=18)
                
            self.details_modal.content = ft.Container(
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
                    exp_bar,
                    ft.Container(height=10),
                    ft.Row([ft.TextButton("Cerrar", on_click=self.close_details)], alignment=ft.MainAxisAlignment.END)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
                width=280,
                padding=20,
                bgcolor=modal_bg_color,
                gradient=bg_gradient,
                border_radius=15
            )
            
        self.details_modal.open = True
        if self.page:
            self.page.update()

    async def open_pc(self, e):
        self.pc_grid.controls = [ft.Container(content=ft.ProgressRing(), alignment=ft.Alignment(0, 0), expand=True)]
        if self.page:
            if self.pc_modal not in self.page.overlay:
                self.page.overlay.append(self.pc_modal)
            self.pc_modal.open = True
            self.page.update()
            
        await asyncio.sleep(0.1)
        self.pc_grid.controls.clear()
        
        with get_session() as session:
            # Traer pokemon atrapados que NO esten en equipo
            pc_pokemons = session.execute(
                select(PokemonCapturado).where(PokemonCapturado.en_equipo == False).order_by(PokemonCapturado.pokeapi_id)
            ).scalars().all()
            
            for pk in pc_pokemons:
                info = pokeapi.get_pokemon_info(pk.pokeapi_id)
                name = info["name"].capitalize() if info else f"#{pk.pokeapi_id}"
                sprite_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pk.pokeapi_id}.png"
                
                meta = pokemon_metadata.POKEMON_METADATA.get(pk.pokeapi_id, {})
                rareza = meta.get("rareza", "Común")
                
                border_color = ft.Colors.GREY_400
                if rareza == "Legendario": border_color = ft.Colors.AMBER_400
                elif rareza == "Muy Raro": border_color = ft.Colors.PURPLE_400
                elif rareza == "Raro": border_color = ft.Colors.BLUE_400
                
                inner_content = ft.Column([
                    ft.Image(src=sprite_url, width=60, height=60, fit="contain"),
                    ft.Text(name, size=11, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Nvl. {pk.nivel}", size=10, color=ft.Colors.WHITE_54)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)

                if rareza in ["Legendario", "Muy Raro"]:
                    grad_colors = [ft.Colors.YELLOW_300, ft.Colors.AMBER_500, ft.Colors.ORANGE_600] if rareza == "Legendario" else [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
                    card = ft.Container(
                        content=ft.Container(
                            content=inner_content,
                            bgcolor="#252525",
                            border_radius=10,
                            padding=3,
                        ),
                        gradient=ft.LinearGradient(begin=ft.Alignment(-1.0, -1.0), end=ft.Alignment(1.0, 1.0), colors=grad_colors),
                        border_radius=12,
                        padding=2,
                        on_click=self.equip_pokemon,
                        data=pk.id
                    )
                else:
                    card = ft.Container(
                        content=inner_content,
                        bgcolor="#252525", 
                        border_radius=10, 
                        border=ft.Border.all(1, border_color),
                        padding=5,
                        on_click=self.equip_pokemon,
                        data=pk.id
                    )
                self.pc_grid.controls.append(card)
                
        if self.page:
            if self.pc_modal not in self.page.overlay:
                self.page.overlay.append(self.pc_modal)
            self.pc_modal.open = True
            self.page.update()

    def equip_pokemon(self, e):
        pk_id = e.control.data
        with get_session() as session:
            pk = session.get(PokemonCapturado, pk_id)
            if pk:
                pk.en_equipo = True
                session.commit()
                
        self.close_pc()
        self.load_data()
        
        if hasattr(self, 'on_team_changed_callback') and self.on_team_changed_callback:
            self.on_team_changed_callback()

    def unequip_pokemon(self, e):
        pk_id = e.control.data
        with get_session() as session:
            pk = session.get(PokemonCapturado, pk_id)
            if pk:
                pk.en_equipo = False
                session.commit()
                
        self.load_data()
        
        if hasattr(self, 'on_team_changed_callback') and self.on_team_changed_callback:
            self.on_team_changed_callback()

    def did_mount(self):
        self.load_data()

    def load_data(self):
        self.team_row.controls.clear()
        
        with get_session() as session:
            equipo = session.execute(
                select(PokemonCapturado).where(PokemonCapturado.en_equipo == True)
            ).scalars().all()
            
            for pk in equipo:
                sprite_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pk.pokeapi_id}.png"
                
                info = pokeapi.get_pokemon_info(pk.pokeapi_id)
                name = info["name"].capitalize() if info else f"#{pk.pokeapi_id}"
                
                remove_btn = ft.Container(
                    content=ft.Icon(ft.Icons.CLOSE, color=ft.Colors.WHITE, size=16),
                    width=24, height=24,
                    bgcolor=ft.Colors.RED_900,
                    shape=ft.BoxShape.CIRCLE,
                    alignment=ft.Alignment.CENTER,
                    on_click=self.unequip_pokemon,
                    data=pk.id,
                    right=5,
                    top=5
                )
                
                meta = pokemon_metadata.POKEMON_METADATA.get(pk.pokeapi_id, {})
                rareza = meta.get("rareza", "Común")
                
                border_color = ft.Colors.GREY_400
                if rareza == "Legendario": border_color = ft.Colors.AMBER_400
                elif rareza == "Muy Raro": border_color = ft.Colors.PURPLE_400
                elif rareza == "Raro": border_color = ft.Colors.BLUE_400
                
                inner_content = ft.Stack([
                    ft.Container(
                        content=ft.Column([
                            ft.Image(src=sprite_url, width=60, height=60, fit="contain"),
                            ft.Text(name, size=11, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Nvl. {pk.nivel}", size=10, text_align=ft.TextAlign.CENTER, color=ft.Colors.AMBER_400)
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                        on_click=self.open_details,
                        data=pk.id,
                        width=100, height=125
                    ),
                    remove_btn
                ])
                
                if rareza in ["Legendario", "Muy Raro"]:
                    grad_colors = [ft.Colors.YELLOW_300, ft.Colors.AMBER_500, ft.Colors.ORANGE_600] if rareza == "Legendario" else [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
                    card = ft.Container(
                        content=ft.Container(
                            content=inner_content,
                            bgcolor="#1E2B3C", # Azul muy suave para la tarjeta
                            border_radius=10,
                            padding=3,
                        ),
                        gradient=ft.LinearGradient(begin=ft.Alignment(-1.0, -1.0), end=ft.Alignment(1.0, 1.0), colors=grad_colors),
                        border_radius=12,
                        padding=2,
                        width=100, height=125
                    )
                else:
                    card = ft.Container(
                        content=inner_content,
                        width=100, height=125, bgcolor="#1E2B3C", border_radius=10, 
                        border=ft.Border.all(2, border_color),
                        padding=5
                    )
                    
                self.team_row.controls.append(card)
                
            # Rellenar huecos vacíos
            for _ in range(3 - len(equipo)):
                add_btn = ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    icon_color=ft.Colors.WHITE_54,
                    icon_size=40,
                    on_click=self.open_pc
                )
                self.team_row.controls.append(
                    ft.Container(
                        content=add_btn,
                        alignment=ft.Alignment.CENTER,
                        width=100, height=125, bgcolor="#111824", border_radius=10,
                        border=ft.Border.all(2, ft.Colors.WHITE_10)
                    )
                )
                
            # Huevo
            from models import Huevo
            huevo = session.execute(
                select(Huevo).where(Huevo.equipado == True)
            ).scalars().first()
            
            if huevo:
                import item_metadata
                meta = item_metadata.ITEM_METADATA.get(huevo.tipo_huevo, {})
                
                sprite = meta.get("sprite")
                if sprite:
                    self.egg_icon_container.content = ft.Image(src=sprite, width=40, height=40, fit="contain")
                else:
                    self.egg_icon_container.content = ft.Icon(meta.get("icon", ft.Icons.EGG), color=meta.get("color", ft.Colors.GREEN_200), size=40)
                    
                self.egg_text.value = meta.get("name", "Incubando...")
                self.egg_progress.value = huevo.tareas_completadas / max(1, huevo.tareas_requeridas)
                self.egg_status.value = f"{huevo.tareas_completadas} / {huevo.tareas_requeridas} Tareas"
            else:
                self.egg_icon_container.content = ft.Icon(ft.Icons.EGG, color=ft.Colors.GREEN_200, size=40)
                self.egg_text.value = "Vacío - Toca para incubar"
                self.egg_progress.value = 0
                self.egg_status.value = ""
                
        try:
            self.update()
        except Exception:
            pass
