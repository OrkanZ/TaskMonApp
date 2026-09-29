import flet as ft
from database import get_session
from models import Inventario, ItemType, PokemonCapturado
from sqlalchemy import select
import item_metadata
import services
import pokeapi

class InventoryView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.on_item_used_callback = None
        
        self.lista = ft.ListView(
            expand=True,
            spacing=10
        )
        
        self.content = ft.Column([
            ft.Text("Tus objetos y huevos sin eclosionar se mostrarán aquí", color=ft.Colors.WHITE_54),
            self.lista
        ], expand=True)
        
        self.btn_usar = ft.FilledButton("Usar", on_click=self.handle_usar_click, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600))
        self.btn_vender = ft.OutlinedButton("Vender", on_click=self.handle_vender, style=ft.ButtonStyle(color=ft.Colors.RED_400))
        
        self.modal = ft.AlertDialog(
            modal=False,
            content_padding=0,
            bgcolor=ft.Colors.TRANSPARENT,
            elevation=0
        )
        
        # Grid Modal para seleccionar el Pokémon objetivo
        self.target_grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=100,
            child_aspect_ratio=0.7,
            spacing=10,
            run_spacing=10,
        )
        self.target_modal = ft.AlertDialog(
            modal=False,
            title=ft.Text("Selecciona un Pokémon", text_align=ft.TextAlign.CENTER),
            content=ft.Container(self.target_grid, width=350, height=400),
            actions=[ft.TextButton("Cancelar", on_click=self.close_target_modal)],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=15),
            bgcolor="#1A1A1A"
        )
        
        self.current_item = None

    def close_target_modal(self, e=None):
        self.target_modal.open = False
        if self.page: self.page.update()

    def close_modal(self):
        self.modal.open = False
        if self.page: self.page.update()
        
    def open_modal(self, e):
        tipo_objeto, cantidad = e.control.data
        self.current_item = tipo_objeto
        meta = item_metadata.ITEM_METADATA.get(tipo_objeto)
        if not meta: return
        
        if "sprite" in meta:
            icon_display = ft.Image(src=meta["sprite"], width=80, height=80, fit="contain")
        else:
            icon_display = ft.Icon(meta["icon"], color=meta["color"], size=80)
            
        rareza = meta.get("rareza", "Común")
        
        bg_color = "#1A1A1A"
        divider_color = ft.Colors.WHITE_24
        title_grad = None
        
        rareza_colors = [ft.Colors.WHITE, ft.Colors.GREY_400, ft.Colors.GREY_600]
        rareza_weight = ft.FontWeight.NORMAL
        rareza_stars = []
        if rareza == "Legendario":
            rareza_colors = [ft.Colors.YELLOW_300, ft.Colors.AMBER_500, ft.Colors.ORANGE_600]
            rareza_weight = ft.FontWeight.W_900
            rareza_stars = [ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER_400, size=14) for _ in range(3)]
            bg_color = "#2A2000"
            divider_color = ft.Colors.AMBER_700
            title_grad = rareza_colors
        elif rareza == "Muy Raro":
            rareza_colors = [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
            rareza_weight = ft.FontWeight.BOLD
            rareza_stars = [ft.Icon(ft.Icons.STAR, color=ft.Colors.PURPLE_400, size=14) for _ in range(2)]
            bg_color = "#20102A"
            divider_color = ft.Colors.PURPLE_700
            title_grad = rareza_colors
        elif rareza == "Raro":
            rareza_colors = [ft.Colors.BLUE_300, ft.Colors.BLUE_400, ft.Colors.BLUE_600]
            rareza_weight = ft.FontWeight.BOLD
            rareza_stars = [ft.Icon(ft.Icons.STAR, color=ft.Colors.BLUE_400, size=14)]
            bg_color = "#0B152A"
            divider_color = ft.Colors.BLUE_700
            
        gradient = ft.LinearGradient(
            begin=ft.Alignment(-1.0, 0),
            end=ft.Alignment(1.0, 0),
            colors=rareza_colors
        )
        
        rareza_row = ft.ShaderMask(
            content=ft.Row([
                ft.Text(rareza.upper(), size=12, weight=rareza_weight),
                ft.Row(rareza_stars, spacing=0)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
            blend_mode=ft.BlendMode.SRC_IN,
            shader=gradient
        )
        
        name_text = meta["name"]
        if title_grad:
            title_display = ft.ShaderMask(
                content=ft.Text(name_text, weight=ft.FontWeight.W_900, text_align=ft.TextAlign.CENTER, size=20),
                blend_mode=ft.BlendMode.SRC_IN,
                shader=ft.LinearGradient(
                    begin=ft.Alignment(-1.0, -1.0),
                    end=ft.Alignment(1.0, 1.0),
                    colors=title_grad
                )
            )
        else:
            title_display = ft.Text(name_text, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.Colors.AMBER_400, size=18)
            
        stats_col = ft.Column([
            ft.Row([
                ft.Text("📦 Tienes: ", size=12, color=ft.Colors.WHITE_70),
                ft.Text(f"{cantidad}", size=12, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
            ft.Row([
                ft.Text("💰 Venta: ", size=12, color=ft.Colors.WHITE_70),
                ft.Text(f"{meta.get('sell_price', max(1, meta['price'] // 2))} monedas", size=12, color=ft.Colors.AMBER_400, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
        ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        desc = ft.Text(f'"{meta["desc"]}"', size=12, color=ft.Colors.WHITE_70, text_align=ft.TextAlign.CENTER, italic=True)
        
        self.btn_usar.disabled = not meta["usable_from_inventory"]
        
        self.modal.content = ft.Container(
            content=ft.Column([
                title_display,
                ft.Container(height=5),
                ft.Row([icon_display], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=2),
                rareza_row,
                ft.Divider(color=divider_color),
                stats_col,
                ft.Divider(color=divider_color),
                desc,
                ft.Container(height=10),
                ft.Row([self.btn_vender, self.btn_usar], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Container(height=5),
                ft.Row([ft.TextButton("Cerrar", on_click=lambda e: self.close_modal())], alignment=ft.MainAxisAlignment.END)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
            width=280,
            padding=20,
            bgcolor=bg_color,
            border_radius=15
        )
        
        if self.page:
            if self.modal not in self.page.overlay:
                self.page.overlay.append(self.modal)
            self.modal.open = True
            self.page.update()
            
    def handle_vender(self, e):
        if not self.current_item: return
        with get_session() as session:
            success, msg = services.vender_objeto(session, self.current_item, 1)
            session.commit()
            
        self.close_modal()
        self.load_data()
        if success and self.on_item_used_callback:
            self.on_item_used_callback()
            
        if self.page:
            snack = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN_700 if success else ft.Colors.RED_700)
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            
    def handle_usar_click(self, e):
        if not self.current_item: return
        
        if self.current_item == ItemType.FOSIL_MISTERIOSO:
            self.open_fossil_selector()
            return
            
        meta = item_metadata.ITEM_METADATA.get(self.current_item)
        
        if meta and meta.get("requires_target"):
            self.open_target_selector()
        else:
            self.execute_usar(target_id=None)

    def open_fossil_selector(self):
        def on_fossil_click(eleccion):
            with get_session() as session:
                success, msg = services.canjear_fosil_misterioso(session, eleccion)
            self.fossil_modal.open = False
            self.modal.open = False
            self.load_data()
            if self.page:
                snack = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN_700 if success else ft.Colors.RED_700)
                self.page.overlay.append(snack)
                snack.open = True
                self.page.update()
                
        self.fossil_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Extraer Fósil"),
            content=ft.Column([
                ft.Text("¿Qué fósil deseas extraer del ámbar?"),
                ft.Container(height=10),
                ft.Row([
                    ft.FilledButton("Fósil Tapa", on_click=lambda _: on_fossil_click(ItemType.FOSIL_TAPA)),
                    ft.FilledButton("Fósil Pluma", on_click=lambda _: on_fossil_click(ItemType.FOSIL_PLUMA))
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], tight=True),
            actions=[ft.TextButton("Cancelar", on_click=lambda _: self._close_fossil_modal())]
        )
        if self.page:
            self.page.overlay.append(self.fossil_modal)
            self.fossil_modal.open = True
            self.page.update()
            
    def _close_fossil_modal(self):
        self.fossil_modal.open = False
        if self.page: self.page.update()

    def open_target_selector(self):
        self.target_grid.controls.clear()
        import pokemon_metadata
        with get_session() as session:
            pokemons = session.execute(select(PokemonCapturado).order_by(PokemonCapturado.pokeapi_id)).scalars().all()
            for pk in pokemons:
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
                            content=inner_content, bgcolor="#252525", border_radius=10, padding=3,
                        ),
                        gradient=ft.LinearGradient(begin=ft.Alignment(-1.0, -1.0), end=ft.Alignment(1.0, 1.0), colors=grad_colors),
                        border_radius=12, padding=2,
                        on_click=self.handle_target_selected,
                        data=pk.pokeapi_id
                    )
                else:
                    card = ft.Container(
                        content=inner_content,
                        bgcolor="#252525", border_radius=10, border=ft.Border.all(1, border_color),
                        padding=5,
                        on_click=self.handle_target_selected,
                        data=pk.pokeapi_id
                    )
                self.target_grid.controls.append(card)
                
        if self.page:
            if self.target_modal not in self.page.overlay:
                self.page.overlay.append(self.target_modal)
            self.target_modal.open = True
            self.page.update()

    def handle_target_selected(self, e):
        target_id = e.control.data
        self.execute_usar(target_id)
            
    def execute_usar(self, target_id=None):
        if not self.current_item: return
        
        with get_session() as session:
            success, msg = services.usar_objeto(session, self.current_item, target_id)
            if success:
                # Si gana XP, procesar subida de niveles y evoluciones como en misiones
                if self.current_item in [ItemType.CARAMELO_RARO]:
                    pk = session.execute(select(PokemonCapturado).where(PokemonCapturado.pokeapi_id == target_id)).scalars().first()
                    if pk:
                        while True:
                            if pk.nivel >= 100:
                                pk.nivel = 100
                                pk.xp = 0
                                break
                            xp_necesaria = 25 + (pk.nivel * 15)
                            if pk.xp >= xp_necesaria:
                                pk.xp -= xp_necesaria
                                pk.nivel += 1
                                # Comprobar evolucion
                                nuevo_id = pokeapi.check_evolution(pk.pokeapi_id, pk.nivel)
                                if nuevo_id:
                                    ya_lo_tiene = session.execute(select(PokemonCapturado).where(PokemonCapturado.pokeapi_id == nuevo_id)).scalars().first() is not None
                                    if not ya_lo_tiene:
                                        pk.pokeapi_id = nuevo_id
                                        services.registrar_pokedex(session, nuevo_id)
                                        msg += f" ¡Y ha evolucionado!"
                            else:
                                break
            session.commit()
            
        self.target_modal.open = False
        self.modal.open = False
        
        self.load_data()
        if self.page:
            snack = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN_700 if success else ft.Colors.RED_700)
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()

    def did_mount(self):
        self.load_data()

    def load_data(self):
        self.lista.controls.clear()
        
        icon_map = {
            ItemType.POKEBALL: (ft.Icons.CATCHING_POKEMON, ft.Colors.RED_ACCENT_400),
            ItemType.ACELERADOR: (ft.Icons.BOLT, ft.Colors.YELLOW_ACCENT_400),
            ItemType.CARAMELO_RARO: (ft.Icons.STAR, ft.Colors.PURPLE_400),
            ItemType.CEBO: (ft.Icons.RESTAURANT, ft.Colors.ORANGE_400),
            ItemType.BOOST_XP: (ft.Icons.ARROW_UPWARD, ft.Colors.BLUE_400)
        }
        
        with get_session() as session:
            objetos = session.execute(
                select(Inventario).where(Inventario.cantidad > 0)
            ).scalars().all()
            
            if not objetos:
                self.lista.controls.append(
                    ft.Text("Tu inventario está vacío. Completa misiones para obtener objetos.", color=ft.Colors.WHITE_54)
                )
            
            for obj in objetos:
                meta = item_metadata.ITEM_METADATA.get(obj.tipo_objeto)
                if not meta: continue
                
                self.lista.controls.append(
                    ft.ListTile(
                        leading=ft.Image(src=meta["sprite"], width=40, height=40, fit="contain") if "sprite" in meta else ft.Icon(meta["icon"], color=meta["color"]),
                        title=ft.Text(meta["name"]),
                        subtitle=ft.Text(f"Cantidad: {obj.cantidad}", color=ft.Colors.WHITE_54),
                        bgcolor="#252525",
                        on_click=self.open_modal,
                        data=(obj.tipo_objeto, obj.cantidad)
                    )
                )
                
        self.update()
