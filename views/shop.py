import flet as ft
from database import get_session
from models import Usuario, Inventario, ItemType, Estadisticas
from sqlalchemy import select
import item_metadata
import services

class ShopView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.on_buy_callback = None
        
        # Cargar info desde metadata
        self.items_info = []
        for t in item_metadata.SHOP_INVENTORY:
            m = item_metadata.ITEM_METADATA[t]
            self.items_info.append({
                "type": t,
                "name": m["name"],
                "icon": m["icon"],
                "sprite": m.get("sprite"),
                "desc": m["desc"],
                "price": m["price"],
                "color": m["color"],
                "min_level": m.get("min_level", 1),
                "rareza": m.get("rareza", "Común")
            })
        
        self.saldo_text = ft.Text("Saldo: 0", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)
        self.saldo_icon = ft.Icon(ft.Icons.MONETIZATION_ON, color=ft.Colors.AMBER_400, size=24)
        
        self.grid = ft.GridView(
            expand=True,
            runs_count=2, # Mejor para móvil que se vean 2 columnas
            max_extent=200,
            child_aspect_ratio=0.55,
            spacing=15,
            run_spacing=15
        )
        
        self.custom_grid = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=200,
            child_aspect_ratio=0.55,
            spacing=15,
            run_spacing=15
        )
        
        self.btn_tab_objetos = ft.TextButton("Objetos", icon=ft.Icons.SHOPPING_BAG, on_click=self.show_objetos, style=ft.ButtonStyle(color=ft.Colors.AMBER_400))
        self.btn_tab_recompensas = ft.TextButton("Mis Recompensas", icon=ft.Icons.STAR, on_click=self.show_recompensas, style=ft.ButtonStyle(color=ft.Colors.WHITE_54))
        
        self.tabs_row = ft.Row([self.btn_tab_objetos, self.btn_tab_recompensas], alignment=ft.MainAxisAlignment.CENTER)
        
        self.grid_container = ft.Container(content=self.grid, expand=True, visible=True)
        self.custom_grid_container = ft.Column([
            ft.Container(height=10),
            ft.Row([
                ft.FilledButton("Nueva Recompensa", icon=ft.Icons.ADD, on_click=self.open_create_reward_modal)
            ], alignment=ft.MainAxisAlignment.CENTER),
            self.custom_grid
        ], expand=True, visible=False)
        
        self.content = ft.Column([
            ft.Row([self.saldo_text, self.saldo_icon], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(color=ft.Colors.WHITE_24),
            self.tabs_row,
            self.grid_container,
            self.custom_grid_container
        ])
        
        self.create_reward_modal = None
        
    def show_objetos(self, e):
        self.btn_tab_objetos.style = ft.ButtonStyle(color=ft.Colors.AMBER_400)
        self.btn_tab_recompensas.style = ft.ButtonStyle(color=ft.Colors.WHITE_54)
        self.grid_container.visible = True
        self.custom_grid_container.visible = False
        if self.page: self.update()
        
    def show_recompensas(self, e):
        self.btn_tab_objetos.style = ft.ButtonStyle(color=ft.Colors.WHITE_54)
        self.btn_tab_recompensas.style = ft.ButtonStyle(color=ft.Colors.AMBER_400)
        self.grid_container.visible = False
        self.custom_grid_container.visible = True
        if self.page: self.update()
        
    def did_mount(self):
        self.load_data()
        
    def load_data(self):
        self.grid.controls.clear()
        self.custom_grid.controls.clear()
        
        with get_session() as session:
            usuario = session.get(Usuario, 1)
            saldo = usuario.monedas if usuario else 0
            nivel = usuario.nivel if usuario else 1
            self.saldo_text.value = f"Saldo: {saldo}"
            
            for item in self.items_info:
                can_afford = saldo >= item["price"]
                meets_level = nivel >= item["min_level"]
                
                if meets_level:
                    btn_content = ft.Row([ft.Text(f"{item['price']}"), ft.Icon(ft.Icons.MONETIZATION_ON, size=14)], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
                    btn_bgcolor = ft.Colors.AMBER_700 if can_afford else ft.Colors.GREY_800
                    btn_color = ft.Colors.WHITE if can_afford else ft.Colors.WHITE_30
                    btn_disabled = not can_afford
                else:
                    btn_content = ft.Row([ft.Text(f"Nv. {item['min_level']}"), ft.Icon(ft.Icons.LOCK, size=14)], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
                    btn_bgcolor = ft.Colors.GREY_900
                    btn_color = ft.Colors.RED_300
                    btn_disabled = True
                
                rareza = item.get("rareza", "Común")
                rareza_colors = [ft.Colors.WHITE, ft.Colors.GREY_400, ft.Colors.GREY_600]
                rareza_weight = ft.FontWeight.NORMAL
                rareza_stars = []
                if rareza == "Legendario":
                    rareza_colors = [ft.Colors.YELLOW_300, ft.Colors.AMBER_500, ft.Colors.ORANGE_600]
                    rareza_weight = ft.FontWeight.BOLD
                    rareza_stars = [ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER_400, size=10) for _ in range(3)]
                elif rareza == "Muy Raro":
                    rareza_colors = [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
                    rareza_weight = ft.FontWeight.BOLD
                    rareza_stars = [ft.Icon(ft.Icons.STAR, color=ft.Colors.PURPLE_400, size=10) for _ in range(2)]
                elif rareza == "Raro":
                    rareza_colors = [ft.Colors.BLUE_300, ft.Colors.BLUE_400, ft.Colors.BLUE_600]
                    rareza_weight = ft.FontWeight.BOLD
                    rareza_stars = [ft.Icon(ft.Icons.STAR, color=ft.Colors.BLUE_400, size=10)]
                    
                rareza_ui = ft.ShaderMask(
                    content=ft.Row([
                        ft.Text(rareza.upper(), size=10, weight=rareza_weight),
                        ft.Row(rareza_stars, spacing=0)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                    blend_mode=ft.BlendMode.SRC_IN,
                    shader=ft.LinearGradient(
                        begin=ft.Alignment(-1.0, 0),
                        end=ft.Alignment(1.0, 0),
                        colors=rareza_colors
                    )
                )
                
                card = ft.Container(
                    content=ft.Column([
                        ft.Image(src=item["sprite"], width=40, height=40, fit="contain") if item.get("sprite") else ft.Icon(item["icon"], size=40, color=item["color"]),
                        ft.Text(item["name"], weight=ft.FontWeight.BOLD, size=16, text_align=ft.TextAlign.CENTER),
                        rareza_ui,
                        ft.Text(item["desc"], size=11, color=ft.Colors.WHITE_54, text_align=ft.TextAlign.CENTER, expand=True),
                        ft.FilledButton(
                            content=btn_content,
                            bgcolor=btn_bgcolor,
                            color=btn_color,
                            disabled=btn_disabled,
                            on_click=self.comprar_objeto,
                            data=item,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=5)
                            )
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    bgcolor="#1A1A1A",
                    border_radius=10,
                    border=ft.Border.all(1, ft.Colors.AMBER_700 if can_afford else ft.Colors.WHITE_10)
                )
                self.grid.controls.append(card)
                
            # Cargar recompensas personalizadas
            recompensas = services.obtener_recompensas_personales(session)
            for rec in recompensas:
                can_afford = saldo >= rec.precio
                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(expand=True),
                            ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.WHITE_30, icon_size=16, data=rec.id, on_click=self.delete_custom_reward, tooltip="Eliminar recompensa")
                        ], alignment=ft.MainAxisAlignment.END, height=20),
                        ft.Icon(ft.Icons.STAR, size=40, color=ft.Colors.AMBER_300),
                        ft.Text(rec.nombre, weight=ft.FontWeight.BOLD, size=16, text_align=ft.TextAlign.CENTER, expand=True),
                        ft.FilledButton(
                            content=ft.Row([ft.Text(f"{rec.precio}"), ft.Icon(ft.Icons.MONETIZATION_ON, size=14)], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                            bgcolor=ft.Colors.AMBER_700 if can_afford else ft.Colors.GREY_800,
                            color=ft.Colors.WHITE if can_afford else ft.Colors.WHITE_30,
                            disabled=not can_afford,
                            on_click=self.buy_custom_reward,
                            data=rec.id,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=5,
                    bgcolor="#1A1A1A",
                    border_radius=10,
                    border=ft.Border.all(1, ft.Colors.AMBER_700 if can_afford else ft.Colors.WHITE_10)
                )
                self.custom_grid.controls.append(card)
                
        try:
            self.update()
        except Exception:
            pass
        
    def comprar_objeto(self, e):
        item = e.control.data
        
        with get_session() as session:
            usuario = session.get(Usuario, 1)
            if not usuario or usuario.monedas < item["price"]:
                return
                
            usuario.monedas -= item["price"]
            
            inv = session.execute(
                select(Inventario).where(Inventario.tipo_objeto == item["type"])
            ).scalars().first()
            
            if inv:
                inv.cantidad += 1
            else:
                nuevo_inv = Inventario(tipo_objeto=item["type"], cantidad=1)
                session.add(nuevo_inv)
                
            estadisticas = session.get(Estadisticas, 1)
            if not estadisticas:
                estadisticas = Estadisticas()
                session.add(estadisticas)
                session.flush()
                
            estadisticas.monedas_gastadas += item["price"]
                
            session.commit()
            services.check_achievements(session)
            
        snack = ft.SnackBar(ft.Text(f"Has comprado: {item['name']}!"), bgcolor=ft.Colors.GREEN_700)
        self.page.overlay.append(snack)
        snack.open = True
        
        self.load_data()
        
        if self.on_buy_callback:
            self.on_buy_callback()

    def open_create_reward_modal(self, e):
        self.tf_nombre = ft.TextField(label="Nombre de recompensa (ej. Ver Película)", max_length=50)
        self.tf_precio = ft.TextField(label="Precio en monedas", keyboard_type=ft.KeyboardType.NUMBER, value="100")
        
        self.create_reward_modal = ft.AlertDialog(
            title=ft.Text("Añadir Recompensa Personal"),
            content=ft.Column([self.tf_nombre, self.tf_precio], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_create_reward_modal),
                ft.FilledButton("Añadir", on_click=self.save_custom_reward)
            ]
        )
        if self.page:
            self.page.overlay.append(self.create_reward_modal)
            self.create_reward_modal.open = True
            self.page.update()
            
    def close_create_reward_modal(self, e=None):
        if self.create_reward_modal:
            self.create_reward_modal.open = False
            if self.page: self.page.update()
            
    def save_custom_reward(self, e):
        nombre = self.tf_nombre.value.strip()
        try:
            precio = int(self.tf_precio.value.strip())
        except:
            precio = 100
            
        if not nombre: return
        
        with get_session() as session:
            services.crear_recompensa_personal(session, nombre, precio, ft.Icons.STAR)
            
        self.close_create_reward_modal()
        self.load_data()
        
    def delete_custom_reward(self, e):
        rid = e.control.data
        with get_session() as session:
            services.eliminar_recompensa_personal(session, rid)
        self.load_data()
        
    def buy_custom_reward(self, e):
        rid = e.control.data
        with get_session() as session:
            success, msg = services.comprar_recompensa_personal(session, rid)
            
        self.load_data()
        
        if self.page:
            snack = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN_700 if success else ft.Colors.RED_700)
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()

        
        if self.on_buy_callback:
            self.on_buy_callback()
