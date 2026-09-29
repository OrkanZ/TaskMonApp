import flet as ft
from database import get_session
from models import JefeMisionPrincipal
from sqlalchemy import select
import pokeapi
from datetime import datetime
import services
from views.pokedex import TYPE_COLORS

class BossView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        
        self.title_text = ft.Text("Desaparece en: ...", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_ACCENT_400)
        self.boss_name = ft.Text("Buscando Jefe...", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.boss_name_mask = ft.ShaderMask(
            content=self.boss_name,
            shader=ft.LinearGradient(colors=["#FFD700", "#FF4500"]),
            blend_mode=ft.BlendMode.SRC_IN
        )
        
        self.boss_types_row = ft.Row([], alignment=ft.MainAxisAlignment.CENTER)
        self.boss_hp_text = ft.Text("0/0 HP", size=16, color=ft.Colors.WHITE_70)
        
        self.boss_hp_bar = ft.ProgressBar(value=1.0, color=ft.Colors.WHITE, bgcolor=ft.Colors.TRANSPARENT, height=20)
        self.boss_hp_mask = ft.ShaderMask(
            content=self.boss_hp_bar,
            shader=ft.LinearGradient(colors=["#FFD700", "#FF4500"]),
            blend_mode=ft.BlendMode.SRC_IN
        )
        self.boss_hp_container = ft.Container(
            content=self.boss_hp_mask,
            bgcolor="#33000000",
            border_radius=10,
            height=20
        )
        
        self.boss_image = ft.Image(src="", width=250, height=250, fit="contain", visible=False)
        self.boss_icon = ft.Icon(ft.Icons.FORT, size=150, color=ft.Colors.WHITE_24)
        
        self.image_container = ft.Container(
            content=ft.Stack([self.boss_icon, self.boss_image], alignment=ft.Alignment(0, 0)),
            alignment=ft.Alignment(0, 0),
            margin=ft.Margin.only(top=20, bottom=20)
        )
        
        self.combat_log_list = ft.ListView(expand=True, spacing=5, padding=10)
        self.combat_log_container = ft.Container(
            content=self.combat_log_list,
            height=150,
            bgcolor="#1A1A1A",
            border=ft.Border.all(1, ft.Colors.WHITE_24),
            border_radius=10,
            margin=ft.Margin.only(left=20, right=20, top=10)
        )
        
        self.boss_card = ft.Container(
            content=ft.Column([
                ft.Row([self.boss_name_mask], alignment=ft.MainAxisAlignment.CENTER),
                self.boss_types_row,
                ft.Container(height=10),
                self.boss_hp_container,
                ft.Container(height=5),
                ft.Row([self.boss_hp_text], alignment=ft.MainAxisAlignment.CENTER)
            ]),
            padding=20,
            border_radius=15,
            bgcolor="#2A1B1B",
            border=ft.Border.all(2, ft.Colors.RED_900),
            margin=ft.Margin.only(left=20, right=20)
        )
        
        main_column = ft.Column([
            ft.Container(height=10),
            ft.Row([self.title_text], alignment=ft.MainAxisAlignment.CENTER),
            self.image_container,
            self.boss_card,
            ft.Container(height=10),
            ft.Row([ft.Text("⚔️ Registro de Combate", weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)], alignment=ft.MainAxisAlignment.CENTER),
            self.combat_log_container
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
        
        self.content = ft.Stack([
            ft.Row([
                ft.Image(src="boss_bg.png", fit="cover", opacity=0.4, width=1000, height=1000),
                ft.Image(src="boss_bg.png", fit="cover", opacity=0.4, width=1000, height=1000)
            ], spacing=0),
            main_column
        ])
        
    def did_mount(self):
        self.load_data()
        
    def load_data(self):
        with get_session() as session:
            services.check_and_spawn_monthly_boss(session)
            
            jefe = session.execute(
                select(JefeMisionPrincipal).where(JefeMisionPrincipal.completada == False)
            ).scalars().first()
            
            jefe_derrotado = False
            if not jefe:
                jefe = session.execute(
                    select(JefeMisionPrincipal).where(JefeMisionPrincipal.completada == True).order_by(JefeMisionPrincipal.id.desc())
                ).scalars().first()
                if jefe:
                    jefe_derrotado = True
                    
            # Calcular tiempo hasta el final del mes
            now = datetime.now()
            if now.month == 12:
                next_month = now.replace(year=now.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                next_month = now.replace(month=now.month+1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            diff = next_month - now
            days = diff.days
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if jefe:
                # Cargar info oficial
                info = pokeapi.get_pokemon_info(jefe.pokemon_id)
                
                boss_display_name = info["name"].capitalize() if info else jefe.titulo.replace("Derrotar a ", "").split(" ")[0]
                self.boss_name.value = f"{boss_display_name}  Nv {getattr(jefe, 'nivel', 1)}"
                
                if info:
                    self.boss_types_row.controls.clear()
                    type_colors_list = []
                    
                    if "types" in info:
                        for t in info["types"]:
                            bg_color, text_color = TYPE_COLORS.get(t.lower(), ("#777777", "white"))
                            type_colors_list.append(bg_color)
                            self.boss_types_row.controls.append(
                                ft.Container(
                                    content=ft.Text(t.upper(), size=10, weight=ft.FontWeight.BOLD, color=text_color),
                                    padding=5,
                                    bgcolor=bg_color,
                                    border_radius=5
                                )
                            )
                            
                    if len(type_colors_list) == 1:
                        type_colors_list.append("#FFFFFF")
                    elif len(type_colors_list) == 0:
                        type_colors_list = ["#FFD700", "#FF4500"]
                        
                    boss_gradient = ft.LinearGradient(
                        begin=ft.Alignment(-1.0, 0),
                        end=ft.Alignment(1.0, 0),
                        colors=type_colors_list
                    )
                    self.boss_name_mask.shader = boss_gradient
                    self.boss_hp_mask.shader = boss_gradient
                            
                    if info["sprites"].get("animated"):
                        self.boss_image.src = info["sprites"]["animated"]
                        self.boss_image.visible = True
                        self.boss_icon.visible = False
                    elif info["sprites"].get("official_artwork"):
                        self.boss_image.src = info["sprites"]["official_artwork"]
                        self.boss_image.visible = True
                        self.boss_icon.visible = False
                    else:
                        self.boss_image.visible = False
                        self.boss_icon.visible = True
                else:
                    self.boss_image.visible = False
                    self.boss_icon.visible = True
                    
                if not jefe_derrotado:
                    self.boss_hp_text.value = f"{jefe.hp_actual} / {jefe.hp_maximo} HP"
                    self.boss_hp_text.text_align = ft.TextAlign.LEFT
                    self.boss_hp_bar.value = jefe.hp_actual / jefe.hp_maximo
                    self.boss_hp_bar.visible = True
                    self.boss_hp_container.visible = True
                    self.title_text.value = f"Desaparece en: {days}d {hours}h {minutes}m"
                    self.title_text.color = ft.Colors.RED_ACCENT_400
                    self.boss_card.bgcolor = "#2A1B1B"
                    self.boss_card.border = ft.Border.all(2, ft.Colors.RED_900)
                    self.boss_image.color = None
                    self.boss_image.color_blend_mode = ft.BlendMode.MODULATE
                    self.boss_card.on_click = None
                else:
                    if getattr(jefe, "capturado", False):
                        self.boss_hp_text.value = f"¡{boss_display_name} capturado!\nEsperando al mes siguiente."
                        self.boss_hp_text.text_align = ft.TextAlign.CENTER
                        self.boss_hp_bar.value = 0
                        self.boss_hp_bar.visible = False
                        self.boss_hp_container.visible = False
                        self.title_text.value = f"Nuevo Jefe en: {days}d {hours}h {minutes}m"
                        self.title_text.color = ft.Colors.GREEN_400
                        self.boss_card.bgcolor = ft.Colors.GREEN_900
                        self.boss_card.border = ft.Border.all(2, ft.Colors.GREEN_400)
                        self.boss_image.color = ft.Colors.BLACK_54
                        self.boss_image.color_blend_mode = ft.BlendMode.SRC_A_TOP
                        self.boss_card.on_click = None
                    else:
                        self.boss_hp_text.value = f"¡{boss_display_name} ha sido derrotado!\nPulsa para capturarlo."
                        self.boss_hp_text.text_align = ft.TextAlign.CENTER
                        self.boss_hp_bar.value = 0
                        self.boss_hp_bar.visible = False
                        self.boss_hp_container.visible = False
                        self.title_text.value = f"Desaparece en: {days}d {hours}h {minutes}m"
                        self.title_text.color = ft.Colors.AMBER_400
                        self.boss_card.bgcolor = ft.Colors.AMBER_900
                        self.boss_card.border = ft.Border.all(2, ft.Colors.AMBER_400)
                        self.boss_image.color = None
                        self.boss_image.color_blend_mode = ft.BlendMode.MODULATE
                        
                        def handle_boss_capture(e, j=jefe):
                            if hasattr(self, 'start_boss_encounter_fn'):
                                self.start_boss_encounter_fn(j.pokemon_id, getattr(j, "nivel", 1), j.id, self.load_data)
                                
                        self.boss_card.on_click = handle_boss_capture
            else:
                self.boss_name.value = "¡Zona Segura!"
                self.boss_hp_text.value = "No hay jefe activo."
                self.boss_hp_text.text_align = ft.TextAlign.LEFT
                self.boss_hp_bar.value = 0
                self.boss_hp_bar.visible = True
                self.boss_hp_container.visible = True
                self.boss_image.visible = False
                self.boss_icon.visible = True
                self.boss_icon.name = ft.Icons.CHECK_CIRCLE_OUTLINE
                self.boss_icon.color = ft.Colors.GREEN_900
                self.title_text.color = ft.Colors.GREEN_400
                self.title_text.value = "Paz Mundial"
                self.boss_card.bgcolor = "#2A1B1B"
                self.boss_card.border = ft.Border.all(2, ft.Colors.GREEN_900)
                self.boss_image.color = None
                self.boss_card.on_click = None
                self.boss_types_row.controls.clear()
                
            self.combat_log_list.controls.clear()
            logs = services.get_combat_logs()
            if not logs:
                self.combat_log_list.controls.append(ft.Text("Aún no hay actividad reciente...", color=ft.Colors.WHITE_38, italic=True, size=12))
            else:
                for msg in logs:
                    self.combat_log_list.controls.append(ft.Text(msg, color=ft.Colors.WHITE_70, size=12))
                
        try:
            self.update()
        except Exception:
            pass
