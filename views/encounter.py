import flet as ft
import flet.canvas as cv
import random
import time
import asyncio
from database import get_session
from models import Inventario, PokemonCapturado, ItemType
from sqlalchemy import select
import pokeapi
import pokemon_metadata
import item_metadata

class EncounterView(ft.Container):
    def __init__(self, rareza, on_finish, forced_pokemon_id=None, forced_level=None, is_boss=False, boss_id=None):
        super().__init__()
        self.opacity = 0
        self.animate_opacity = 800
        self.expand = True
        
        if is_boss:
            self.bgcolor = "#111111"
        else:
            self.gradient = ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=[
                    "#5473A8", # Cielo arriba
                    "#81A2D2", # Cielo medio
                    "#E0E2F0", # Horizonte cielo
                    "#B4E7A2", # Horizonte suelo
                    "#5AB975", # Suelo medio
                    "#338048"  # Suelo abajo
                ],
                stops=[0.0, 0.14, 0.28, 0.28, 0.64, 1.0]
            )
        self.rareza_encuentro = rareza
        self.on_finish = on_finish
        self.is_boss = is_boss
        self.boss_id = boss_id
        
        self.berry_multiplier = 1.0
        
        if forced_pokemon_id is not None:
            self.pokemon_id = forced_pokemon_id
        else:
            self.pokemon_id = self.pick_pokemon()
            
        self.info = pokeapi.get_pokemon_info(self.pokemon_id)
        self.meta = pokemon_metadata.POKEMON_METADATA.get(self.pokemon_id, {})
        
        self.sprite = ft.Image(
            src=self.info["sprites"].get("animated") or self.info["sprites"].get("front_default"),
            width=150, height=150, fit="contain",
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )
        
        pk_rareza = self.meta.get("rareza", "Común")
        name = self.info["name"].capitalize()
        
        # Calcular nivel
        with get_session() as session:
            from models import Usuario
            usuario = session.get(Usuario, 1)
            trainer_level = usuario.nivel if usuario else 1

        is_evolved = "Evolución" in self.meta.get("metodo", "") or "Evolucion" in self.meta.get("metodo", "")
        ev_str = self.meta.get("evolucion")
        
        if forced_level is not None:
            self.pokemon_level = forced_level
        else:
            self.pokemon_level = 1
            if is_evolved and ev_str and ev_str.startswith("Nivel ("):
                import re
                match = re.search(r"Nivel \((\d+)\)", ev_str)
                if match:
                    min_lvl = int(match.group(1))
                    if trainer_level >= min_lvl:
                        self.pokemon_level = min_lvl
                    else:
                        self.pokemon_level = trainer_level
                else:
                    self.pokemon_level = random.randint(1, trainer_level) if trainer_level < 10 else random.randint(1, 10)
            else:
                if trainer_level < 10:
                    self.pokemon_level = random.randint(1, max(1, trainer_level))
                else:
                    self.pokemon_level = random.randint(1, 10)
        
        text_color_rareza = ft.Colors.BLACK
        rareza_weight = ft.FontWeight.NORMAL
        
        if pk_rareza == "Legendario": 
            rareza_weight = ft.FontWeight.W_900
        elif pk_rareza == "Muy Raro": 
            rareza_weight = ft.FontWeight.BOLD
        elif pk_rareza == "Raro": 
            text_color_rareza = ft.Colors.BLUE_400
            rareza_weight = ft.FontWeight.BOLD
            
        if pk_rareza in ["Legendario", "Muy Raro"]:
            if pk_rareza == "Legendario":
                grad_colors = [ft.Colors.YELLOW_300, ft.Colors.AMBER_500, ft.Colors.ORANGE_600]
            else:
                grad_colors = [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
                
            gradient = ft.LinearGradient(
                begin=ft.Alignment(-1.0, -1.0),
                end=ft.Alignment(1.0, 1.0),
                colors=grad_colors
            )
            
            title_text = ft.ShaderMask(
                content=ft.Text(name, weight=rareza_weight, text_align=ft.TextAlign.CENTER, size=24),
                blend_mode=ft.BlendMode.SRC_IN,
                shader=gradient
            )
        else:
            title_text = ft.Text(name, weight=rareza_weight, text_align=ft.TextAlign.LEFT, color=text_color_rareza, size=24)
            
        level_label = ft.Text("Nv ", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_600)
        level_number = ft.Text(str(self.pokemon_level), size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
        title_content = ft.Row([title_text, ft.Container(width=10), level_label, level_number], alignment=ft.MainAxisAlignment.CENTER)
            
        title_box = ft.Container(
            content=title_content,
            bgcolor="#F8F8F8",
            border=ft.Border(top=ft.BorderSide(3, "#424242"), bottom=ft.BorderSide(3, "#424242"), left=ft.BorderSide(3, "#424242"), right=ft.BorderSide(3, "#424242")),
            border_radius=8,
            padding=ft.Padding(left=15, top=4, right=15, bottom=4),
            margin=ft.Margin(left=0, top=20, right=0, bottom=0),
            shadow=ft.BoxShadow(blur_radius=0, spread_radius=1, color="#60000000", offset=ft.Offset(3, 3))
        )
            
        msg_str = f"¡Es {name}!" if is_boss else f"¡Un {name} salvaje de Nv. {self.pokemon_level} ha aparecido!"
        self.msg_text = ft.Text(msg_str, size=16, color=ft.Colors.WHITE_70, text_align=ft.TextAlign.CENTER, italic=True)
        
        self.btn_ball = ft.FilledButton("Lanzar Pokéball", on_click=self.open_balls_menu, style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700))
        self.btn_item = ft.FilledButton("Usar Objeto", on_click=self.open_items_menu, style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700))
        self.btn_flee = ft.OutlinedButton("Huir", on_click=self.flee, style=ft.ButtonStyle(color=ft.Colors.GREY_400))
        self.action_row = ft.Row([self.btn_ball, self.btn_item], alignment=ft.MainAxisAlignment.CENTER)
        
        shadow_color = "#2B170B" if is_boss else "#1A3311"
        enemy_base = cv.Canvas(
            [
                cv.Oval(0, 0, 160, 45, paint=ft.Paint(color=shadow_color, style=ft.PaintingStyle.FILL))
            ],
            width=160, height=45,
            opacity=0.9
        )
        
        self.pokeball_sprite = ft.Image(
            src="", width=30, height=30, fit="contain", visible=False,
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.LINEAR),
            animate_rotation=ft.Animation(100, ft.AnimationCurve.LINEAR)
        )
        
        enemy_stack = ft.Stack([
            ft.Container(enemy_base, top=140, left=20),
            ft.Container(self.sprite, top=20, left=25),
            ft.Container(self.pokeball_sprite, top=180, left=85) # Centrado abajo
        ], width=200, height=200)
        
        enemy_layer = ft.Container(
            content=enemy_stack,
            alignment=ft.Alignment(0, -0.44)
        )
        
        ui_layer = ft.Column([
            ft.Row([title_box], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(expand=True),
            ft.Container(
                content=self.msg_text,
                padding=20,
                bgcolor="#111111",
                border_radius=10,
                border=ft.Border.all(1, ft.Colors.WHITE_24),
                width=350
            ),
            ft.Container(height=20),
            self.action_row,
            self.btn_flee,
            ft.Container(height=40)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        if self.is_boss:
            bg_layer = ft.Row([
                ft.Image(src="boss_bg.png", fit="cover", opacity=0.6, width=1000, height=1000),
                ft.Image(src="boss_bg.png", fit="cover", opacity=0.6, width=1000, height=1000)
            ], spacing=0)
            self.content = ft.Stack([bg_layer, enemy_layer, ui_layer], expand=True)
        else:
            self.content = ft.Stack([enemy_layer, ui_layer], expand=True)
        
        self.inventory_modal = ft.AlertDialog(
            modal=False,
            bgcolor="#1A1A1A",
            title=ft.Text("Mochila", text_align=ft.TextAlign.CENTER),
            content=ft.Column([], tight=True, scroll=ft.ScrollMode.AUTO, height=300, width=300),
            actions=[ft.TextButton("Cancelar", on_click=self.close_inventory_modal)],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.capture_modal = ft.AlertDialog(
            modal=True,
            bgcolor="#1A1A1A",
            content=ft.Container(
                content=ft.Column([], tight=True, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=300,
                padding=20
            ),
            actions=[ft.FilledButton("Continuar", on_click=self.close_capture_modal_and_finish, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700))],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        
    def did_mount(self):
        self.page.run_task(self.intro_animation)
        
    async def intro_animation(self):
        import asyncio
        await asyncio.sleep(0.1)
        self.opacity = 1
        self.update()

    def flee(self, e):
        self.log_msg("Has escapado sin problemas.")
        self.btn_ball.disabled = True
        self.btn_item.disabled = True
        self.btn_flee.disabled = True
        if self.page: self.page.update()
        time.sleep(1.5)
        self.on_finish()

    def pick_pokemon(self):
        r = random.random()
        if self.rareza_encuentro == "Común":
            target_rarity = "Común" if r < 0.90 else "Raro"
        else:
            target_rarity = "Raro" if r < 0.90 else "Muy Raro"
            
        base_candidates = []
        for pid, meta in pokemon_metadata.POKEMON_METADATA.items():
            if meta.get("rareza", "Común") == target_rarity:
                met = meta.get("metodo_obtencion", meta.get("metodo", ""))
                if met in ["Captura", "Captura/Evolucion", "Captura/Evolución", "Captura / Evolucion", "Captura / Evolución"]:
                    base_candidates.append(pid)
                    
        if base_candidates:
            with get_session() as session:
                capturados = session.execute(select(PokemonCapturado.pokeapi_id)).scalars().all()
            
            unowned = [pid for pid in base_candidates if pid not in capturados]
            if unowned:
                candidates = unowned
            else:
                candidates = base_candidates
        else:
            candidates = list(pokemon_metadata.POKEMON_METADATA.keys())
            
        return random.choice(candidates)

    def log_msg(self, msg):
        self.msg_text.value = msg
        if self.page: self.page.update()

    def close_inventory_modal(self, e=None):
        self.inventory_modal.open = False
        if self.page:
            try:
                self.page.close(self.inventory_modal)
            except Exception:
                pass
            self.page.update()

    def close_capture_modal_and_finish(self, e):
        self.capture_modal.open = False
        if self.page:
            try:
                self.page.close(self.capture_modal)
            except Exception:
                pass
            self.page.update()
        self.on_finish()

    def open_balls_menu(self, e):
        self.inventory_modal.title.value = "Selecciona una Pokéball"
        self.inventory_modal.content.controls.clear()
        
        balls = [ItemType.POKEBALL, ItemType.ULTRABALL, ItemType.MASTERBALL]
        
        with get_session() as session:
            inv_items = session.execute(select(Inventario).where(Inventario.tipo_objeto.in_(balls))).scalars().all()
            inv_dict = {item.tipo_objeto: item.cantidad for item in inv_items}
            
            for b in balls:
                qty = inv_dict.get(b, 0)
                meta = item_metadata.ITEM_METADATA.get(b)
                if not meta: continue
                
                btn = ft.Container(
                    content=ft.Row([
                        ft.Image(src=meta["sprite"], width=30, height=30) if "sprite" in meta else ft.Icon(meta["icon"], color=meta["color"]),
                        ft.Text(f"{meta['name']} (x{qty})", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if qty > 0 else ft.Colors.WHITE_24)
                    ]),
                    padding=10,
                    bgcolor="#252525" if qty > 0 else "#111111",
                    border_radius=8,
                    on_click=self.throw_ball if qty > 0 else None,
                    data=b
                )
                self.inventory_modal.content.controls.append(btn)
                
        if self.page:
            try:
                self.page.open(self.inventory_modal)
            except Exception:
                if self.inventory_modal not in self.page.overlay:
                    self.page.overlay.append(self.inventory_modal)
                self.inventory_modal.open = True
                self.page.update()

    def open_items_menu(self, e):
        self.inventory_modal.title.value = "Selecciona un Objeto"
        self.inventory_modal.content.controls.clear()
        
        items = [ItemType.CEBO]
        
        with get_session() as session:
            inv_items = session.execute(select(Inventario).where(Inventario.tipo_objeto.in_(items))).scalars().all()
            inv_dict = {item.tipo_objeto: item.cantidad for item in inv_items}
            
            for b in items:
                qty = inv_dict.get(b, 0)
                meta = item_metadata.ITEM_METADATA.get(b)
                if not meta: continue
                
                btn = ft.Container(
                    content=ft.Row([
                        ft.Image(src=meta["sprite"], width=30, height=30) if "sprite" in meta else ft.Icon(meta["icon"], color=meta["color"]),
                        ft.Text(f"{meta['name']} (x{qty})", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if qty > 0 else ft.Colors.WHITE_24)
                    ]),
                    padding=10,
                    bgcolor="#252525" if qty > 0 else "#111111",
                    border_radius=8,
                    on_click=self.use_item if qty > 0 else None,
                    data=b
                )
                self.inventory_modal.content.controls.append(btn)
                
        if self.page:
            try:
                self.page.open(self.inventory_modal)
            except Exception:
                if self.inventory_modal not in self.page.overlay:
                    self.page.overlay.append(self.inventory_modal)
                self.inventory_modal.open = True
                self.page.update()

    async def throw_ball(self, e):
        tipo_ball = e.control.data
        self.close_inventory_modal()
        
        # Consumir ball
        with get_session() as session:
            inv = session.execute(select(Inventario).where(Inventario.tipo_objeto == tipo_ball)).scalar_one_or_none()
            if inv and inv.cantidad > 0:
                inv.cantidad -= 1
                session.commit()
            else:
                return
                
        meta = item_metadata.ITEM_METADATA.get(tipo_ball)
        self.log_msg(f"¡Has lanzado una {meta['name']}!")
        
        self.btn_ball.disabled = True
        self.btn_item.disabled = True
        self.btn_flee.disabled = True
        if self.page: self.page.update()
        
        # --- ANIMACIÓN: Lanzamiento ---
        self.pokeball_sprite.src = meta['sprite']
        self.pokeball_sprite.visible = True
        self.pokeball_sprite.opacity = 1
        self.pokeball_sprite.scale = 2.0
        self.pokeball_sprite.offset = ft.Offset(0, 0)
        self.pokeball_sprite.rotate = 0
        self.update()
        await asyncio.sleep(0.1)
        
        # Vuela hacia el pokémon
        self.pokeball_sprite.offset = ft.Offset(0, -5.5) # Sube
        self.pokeball_sprite.scale = 1.3
        self.update()
        await asyncio.sleep(0.4)
        
        # --- ANIMACIÓN: Absorción ---
        self.sprite.scale = 0
        self.update()
        await asyncio.sleep(0.2)
        
        # --- ANIMACIÓN: Caída ---
        self.pokeball_sprite.offset = ft.Offset(0, -2.0) # Cae a la base
        self.pokeball_sprite.scale = 1.3
        self.update()
        await asyncio.sleep(0.4)
        
        # Cálculo de captura
        base_rate = 1/3 # Común: 1/3
        pk_rareza = self.meta.get("rareza", "Común")
        if pk_rareza == "Raro": base_rate = 1/6
        elif pk_rareza == "Muy Raro": base_rate = 1/9
        elif pk_rareza == "Legendario": base_rate = 1/9
        
        multiplier = 1.0
        if tipo_ball == ItemType.ULTRABALL: multiplier = 2.0
        elif tipo_ball == ItemType.MASTERBALL: multiplier = 1000.0
        
        chance = base_rate * multiplier * self.berry_multiplier
        success = random.random() < chance
        self.berry_multiplier = 1.0 # Se reinicia el buff de baya

        
        # --- ANIMACIÓN: Temblores ---
        for i in range(1, 4):
            await asyncio.sleep(0.6)
            self.log_msg(f"{i}...")
            self.pokeball_sprite.rotate = -0.3
            self.update()
            await asyncio.sleep(0.15)
            self.pokeball_sprite.rotate = 0.3
            self.update()
            await asyncio.sleep(0.15)
            self.pokeball_sprite.rotate = 0
            self.update()
        
        await asyncio.sleep(0.5)
        
        if success:
            with get_session() as session:
                existente = session.execute(select(PokemonCapturado).where(PokemonCapturado.pokeapi_id == self.pokemon_id)).scalar_one_or_none()
                is_duplicate = (existente is not None)
                if not is_duplicate:
                    self.log_msg(f"¡Ya está! ¡{self.info['name'].capitalize()} atrapado!")
                    pk = PokemonCapturado(pokeapi_id=self.pokemon_id, nivel=self.pokemon_level, xp=0, en_equipo=False)
                    session.add(pk)
                else:
                    self.log_msg(f"¡Atrapado! Tu {self.info['name'].capitalize()} sube 3 niveles al ser repetido.")
                    existente.nivel += 3
                    
                # Registrar en la Pokédex si no lo está
                from models import RegistroPokedex
                reg_pokedex = session.execute(select(RegistroPokedex).where(RegistroPokedex.pokeapi_id == self.pokemon_id)).scalar_one_or_none()
                if not reg_pokedex:
                    session.add(RegistroPokedex(pokeapi_id=self.pokemon_id))
                    
                if getattr(self, "is_boss", False) and getattr(self, "boss_id", None):
                    from models import JefeMisionPrincipal
                    jefe = session.get(JefeMisionPrincipal, self.boss_id)
                    if jefe:
                        jefe.capturado = True
                        
                session.commit()
                    
            # --- ANIMACIÓN: Brillo de captura ---
            self.pokeball_sprite.scale = 1.6
            self.update()
            await asyncio.sleep(0.15)
            self.pokeball_sprite.scale = 1.3
            self.update()
            
            # --- MODAL DE CAPTURA ---
            col = self.capture_modal.content.content
            col.controls.clear()
            
            col.controls.append(
                ft.Image(
                    src=self.info["sprites"].get("animated") or self.info["sprites"].get("front_default"),
                    width=120, height=120, fit="contain"
                )
            )
            col.controls.append(
                ft.Text(f"¡Has atrapado a {self.info['name'].capitalize()}!", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER)
            )
            if is_duplicate:
                col.controls.append(
                    ft.Text("¡Ya lo tenías!\nEl Pokémon original de tu PC ha recibido +3 Niveles.", size=14, color=ft.Colors.AMBER_400, text_align=ft.TextAlign.CENTER)
                )
            else:
                col.controls.append(
                    ft.Text("¡Datos registrados en la Pokédex por primera vez!", size=14, color=ft.Colors.GREEN_400, text_align=ft.TextAlign.CENTER)
                )
                
            if self.page:
                try:
                    self.page.open(self.capture_modal)
                except Exception:
                    if self.capture_modal not in self.page.overlay:
                        self.page.overlay.append(self.capture_modal)
                    self.capture_modal.open = True
                    self.page.update()
        else:
            self.log_msg("¡Oh no! El Pokémon se ha liberado.")
            # --- ANIMACIÓN: Ruptura ---
            self.pokeball_sprite.opacity = 0
            self.sprite.scale = 1
            self.update()
            await asyncio.sleep(1.5)
            
            pk_rareza = self.meta.get("rareza", "Común")
            flee_rate = 0.0 if pk_rareza in ["Legendario", "Muy Raro"] else 0.10
            
            if random.random() < flee_rate:
                self.log_msg("¡El Pokémon ha huido!")
                if self.page: self.page.update()
                await asyncio.sleep(2.0)
                self.on_finish()
            else:
                self.pokeball_sprite.visible = False
                self.btn_ball.disabled = False
                self.btn_item.disabled = False
                self.btn_flee.disabled = False
                self.log_msg("El Pokémon está esperando tu siguiente movimiento...")
                if self.page: self.page.update()

    async def use_item(self, e):
        tipo_item = e.control.data
        self.close_inventory_modal()
        
        meta = item_metadata.ITEM_METADATA.get(tipo_item)
        if not meta: return
        
        self.btn_ball.disabled = True
        self.btn_item.disabled = True
        self.btn_flee.disabled = True
        if self.page: self.page.update()
        
        await asyncio.sleep(0.5)
        with get_session() as session:
            inv = session.execute(select(Inventario).where(Inventario.tipo_objeto == tipo_item)).scalar_one_or_none()
            if inv and inv.cantidad > 0:
                inv.cantidad -= 1
                session.commit()
            else:
                return
                
        # --- ANIMACIÓN: Lanzamiento de objeto ---
        self.pokeball_sprite.src = meta['sprite']
        self.pokeball_sprite.visible = True
        self.pokeball_sprite.opacity = 1
        self.pokeball_sprite.scale = 2.0
        self.pokeball_sprite.offset = ft.Offset(0, 0)
        self.pokeball_sprite.rotate = 0
        self.update()
        await asyncio.sleep(0.1)
        
        # Vuela hacia el pokémon
        self.pokeball_sprite.offset = ft.Offset(0, -5.5) # Sube
        self.pokeball_sprite.scale = 1.3
        self.update()
        await asyncio.sleep(0.4)
        
        # --- ANIMACIÓN: Consumo ---
        self.pokeball_sprite.scale = 0
        self.update()
        await asyncio.sleep(0.3)
        self.pokeball_sprite.visible = False
        
        if tipo_item == ItemType.CEBO:
            self.berry_multiplier = 2.0
            self.log_msg(f"Has usado {meta['name']}. ¡El Pokémon bajó la guardia!")
            
        await asyncio.sleep(1.5)
        
        self.btn_ball.disabled = False
        self.btn_item.disabled = False
        self.btn_flee.disabled = False
        if self.page: self.page.update()
