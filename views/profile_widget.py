import flet as ft
from database import get_session
from models import Usuario, MisionRegular, LogroDesbloqueado
from sqlalchemy import select, func

class ProfileWidget(ft.Container):
    def __init__(self):
        super().__init__()
        self.nivel_text = ft.Text("Nv. 1", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.WHITE)
        self.xp_text = ft.Text("0 / 100 XP", size=10, color=ft.Colors.WHITE_54)
        self.monedas_text = ft.Text("0", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.AMBER_400)
        
        self.xp_bar = ft.ProgressBar(
            value=0, 
            color=ft.Colors.LIGHT_BLUE_ACCENT_400, 
            bgcolor=ft.Colors.WHITE_10, 
            width=100, 
            height=6
        )
        self.avatar_container = ft.Container(
            content=ft.CircleAvatar(
                content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_GREY_800
            ),
            shape=ft.BoxShape.CIRCLE,
            padding=2
        )
        
        self.content = ft.Row([
            ft.Column([
                ft.Row([
                    ft.Row([self.monedas_text, ft.Icon(ft.Icons.MONETIZATION_ON, color=ft.Colors.AMBER_400, size=16)], spacing=2),
                    ft.Container(width=10), # Espaciador
                    self.nivel_text,
                ], alignment=ft.MainAxisAlignment.END, spacing=0),
                self.xp_bar,
                self.xp_text
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2),
            
            self.avatar_container
        ], alignment=ft.MainAxisAlignment.END, spacing=10)
        
        self.padding = ft.Padding(0, 0, 15, 0)
        self.on_click = self.show_profile_details
        
    def did_mount(self):
        self.update_data()
        
    def update_data(self):
        with get_session() as session:
            usuario = session.get(Usuario, 1)
            if not usuario:
                usuario = Usuario(nivel=1, xp_actual=0, monedas=0)
                session.add(usuario)
                session.commit()
                
            xp_max = min(50 + (usuario.nivel - 1) * 25, 500)
            self.nivel_text.value = f"Nv. {usuario.nivel}"
            self.xp_text.value = f"{usuario.xp_actual} / {xp_max} XP"
            self.monedas_text.value = f"{usuario.monedas}"
            self.xp_bar.value = min(1.0, usuario.xp_actual / max(1, xp_max))
            
            if usuario.boost_xp_restantes > 0:
                self.avatar_container.border = ft.Border.all(3, ft.Colors.BLUE_ACCENT_400)
                self.avatar_container.shadow = ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.Colors.BLUE_ACCENT_700)
            else:
                self.avatar_container.border = None
                self.avatar_container.shadow = None
                
        self.update()

    def show_profile_details(self, e):
        with get_session() as session:
            usuario = session.get(Usuario, 1)
            total_completadas = session.execute(
                select(func.count(MisionRegular.id)).where(MisionRegular.completada == True)
            ).scalar() or 0
            
        xp_max = min(50 + (usuario.nivel - 1) * 25, 500)
        
        def get_trainer_title(nivel):
            if nivel < 10: return "Entrenador Novato"
            if nivel < 20: return "Entrenador Promesa"
            if nivel < 30: return "Entrenador Experto"
            if nivel < 40: return "Entrenador Veterano"
            if nivel < 50: return "Líder de Gimnasio"
            if nivel < 60: return "As del Frente"
            if nivel < 70: return "Miembro del Alto Mando"
            if nivel < 80: return "Campeón Regional"
            if nivel < 90: return "Entrenador Legendario"
            if nivel < 100: return "Maestro Pokémon"
            return "Campeón Mundial"
        
        title = get_trainer_title(usuario.nivel)
        
        column_content = ft.Column([
            ft.Row([
                ft.CircleAvatar(
                    content=ft.Icon(ft.Icons.PERSON, size=40, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.BLUE_GREY_800,
                    radius=30
                ),
                ft.Container(width=15),
                ft.Column([
                    ft.Text(f"Nivel {usuario.nivel}", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text(title, color=ft.Colors.WHITE_54)
                ], spacing=0)
            ]),
            ft.Divider(height=20, color=ft.Colors.WHITE_24),
            ft.Text("Estadísticas", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_ACCENT_400),

            ft.Container(height=10),
            ft.Row([
                ft.Icon(ft.Icons.STAR, color=ft.Colors.LIGHT_BLUE_ACCENT_400),
                ft.Text(f"Experiencia Acumulada: {usuario.xp_actual} / {max(1, xp_max)} XP")
            ]),
            ft.Row([
                ft.Icon(ft.Icons.MONETIZATION_ON, color=ft.Colors.AMBER_400),
                ft.Text(f"Monedas Actuales: {usuario.monedas} 🪙")
            ]),
            ft.Row([
                ft.Icon(ft.Icons.TASK_ALT, color=ft.Colors.GREEN_400),
                ft.Text(f"Misiones Completadas: {total_completadas}")
            ])
        ], tight=True)
                
        if usuario.boost_xp_restantes > 0:
            column_content.controls.extend([
                ft.Divider(height=20, color=ft.Colors.WHITE_24),
                ft.Text("✨ Mejoras Activas", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
                ft.Container(height=5),
                ft.Row([
                    ft.Icon(ft.Icons.TRENDING_UP, color=ft.Colors.GREEN_400),
                    ft.Text(f"XP Boost (+50%) durante {usuario.boost_xp_restantes} tareas más.")
                ])
            ])
            
        desbloqueados_ids = [d.logro_id for d in session.execute(select(LogroDesbloqueado)).scalars().all()]
        
        medallas_grid = ft.GridView(
            expand=False,
            runs_count=4,
            max_extent=80,
            child_aspect_ratio=1.0,
            spacing=10,
            run_spacing=10,
        )
        
        from achievement_metadata import ACHIEVEMENTS
        for logro_id, meta in ACHIEVEMENTS.items():
            is_unlocked = logro_id in desbloqueados_ids
            color = meta["color"] if is_unlocked else ft.Colors.WHITE_24
            
            medallas_grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(meta["icon"], color=color, size=30),
                        ft.Text(meta["title"] if is_unlocked else "???", size=10, text_align=ft.TextAlign.CENTER, color=color)
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    padding=5,
                    bgcolor=ft.Colors.WHITE_10 if is_unlocked else ft.Colors.BLACK_12,
                    border_radius=10,
                    tooltip=meta["desc"]
                )
            )
            
        column_content.controls.extend([
            ft.Divider(height=20, color=ft.Colors.WHITE_24),
            ft.Text("🏅 Medallas de Entrenador", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
            ft.Container(height=10),
            ft.Container(
                content=medallas_grid,
                height=200
            )
        ])
            
        sheet = ft.BottomSheet(
            ft.Container(
                padding=20,
                bgcolor="#1E1E1E",
                content=ft.Column([column_content], scroll=ft.ScrollMode.AUTO, height=600)
            )
        )
        self.page.overlay.append(sheet)
        sheet.open = True
        self.page.update()
