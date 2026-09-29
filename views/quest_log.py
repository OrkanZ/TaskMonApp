import flet as ft
import services
from database import get_session
from models import MissionType, MisionRegular, JefeMisionPrincipal, BancoMisiones, ListaTareas, Dificultad, Prioridad, Seccion, Estadisticas
from sqlalchemy import select, and_, delete, or_, func
from datetime import date
import pokeapi

class MisionCard(ft.Container):
    def __init__(self, mision, on_complete, on_edit=None):
        super().__init__()
        self.mision = mision
        self.on_complete_callback = on_complete
        self.on_edit_callback = on_edit
        
        lista = mision.banco_mision.lista
        icon_name_str = lista.icono if lista else "STAR"
        icon_data = getattr(ft.Icons, icon_name_str, ft.Icons.STAR)
        icon_color = lista.color if lista else ft.Colors.WHITE
        list_name = lista.nombre if lista else "Sin Lista"
        
        prioridad = mision.banco_mision.prioridad
        dificultad = mision.banco_mision.dificultad
        
        prioridad_colores = {
            Prioridad.ALTA: ft.Colors.RED_ACCENT_400,
            Prioridad.MEDIA: ft.Colors.ORANGE_ACCENT_400,
            Prioridad.BAJA: ft.Colors.LIGHT_BLUE_ACCENT_400,
            Prioridad.SIN_PRIORIDAD: ft.Colors.TRANSPARENT
        }
        border_color = prioridad_colores.get(prioridad, ft.Colors.TRANSPARENT)
        
        fecha_texto = ""
        f_color = ft.Colors.WHITE_54
        if mision.fecha_limite:
            fecha_texto = mision.fecha_limite.strftime("%d/%m")
            if mision.fecha_limite < date.today():
                f_color = ft.Colors.RED_ACCENT_400
                fecha_texto = "⚠️ " + fecha_texto
        
        cb_color = border_color if border_color != ft.Colors.TRANSPARENT else ft.Colors.WHITE_54
        
        self.checkbox = ft.Checkbox(
            value=False,
            on_change=self.complete_clicked,
            fill_color=ft.Colors.TRANSPARENT,
            check_color=cb_color,
            border_side=ft.BorderSide(2, cb_color),
            shape=ft.RoundedRectangleBorder(radius=4)
        )
        
        row_elements = [
            self.checkbox,
            ft.Icon(icon=icon_data, color=icon_color, size=20),
            ft.Text(mision.banco_mision.titulo, weight=ft.FontWeight.W_600, size=14, expand=True)
        ]
        
        dificultad_colores = {
            Dificultad.MUY_FACIL: ft.Colors.LIGHT_BLUE_ACCENT_400,
            Dificultad.FACIL: ft.Colors.LIGHT_GREEN_ACCENT_400,
            Dificultad.NORMAL: ft.Colors.ORANGE_ACCENT_400,
            Dificultad.DIFICIL: ft.Colors.RED_ACCENT_400
        }
        dif_color = dificultad_colores.get(dificultad, ft.Colors.WHITE)
        row_elements.append(ft.Icon(ft.Icons.STAR, color=dif_color, size=14))
        
        if fecha_texto:
            row_elements.append(ft.Text(fecha_texto, color=f_color, size=12, weight=ft.FontWeight.BOLD))
            
        self.content = ft.Row(row_elements, alignment=ft.MainAxisAlignment.START)
        
        self.padding = 8
        self.border_radius = 10
        self.bgcolor = "#252525"
        self.border = ft.Border.all(1, border_color) if border_color != ft.Colors.TRANSPARENT else None
        self.on_click = self.open_edit_dialog
        
    def open_edit_dialog(self, e):
        page = self.page
        
        dificultad_edit = ft.Dropdown(
            label="Dificultad",
            options=[ft.dropdown.Option(d.value) for d in Dificultad],
            value=self.mision.banco_mision.dificultad.value
        )
        prioridad_edit = ft.Dropdown(
            label="Prioridad",
            options=[ft.dropdown.Option(p.value) for p in Prioridad],
            value=self.mision.banco_mision.prioridad.value
        )
        
        secciones_opciones = [ft.dropdown.Option("", "Sin sección")]
        with get_session() as session:
            lista_id = self.mision.banco_mision.lista_id
            if lista_id:
                secs = session.execute(select(Seccion).where(Seccion.lista_id == lista_id).order_by(Seccion.orden)).scalars().all()
                for s in secs:
                    secciones_opciones.append(ft.dropdown.Option(str(s.id), s.nombre))
                    
        seccion_edit = ft.Dropdown(
            label="Sección",
            options=secciones_opciones,
            value=str(self.mision.banco_mision.seccion_id) if self.mision.banco_mision.seccion_id else ""
        )
        
        fecha_val = [self.mision.fecha_limite]
        date_picker = ft.DatePicker(
            on_change=lambda e: update_date(e),
            on_dismiss=lambda e: update_date(e)
        )
        page.overlay.append(date_picker)
        
        def update_date(e):
            if date_picker.value:
                from datetime import timedelta
                fecha_val[0] = (date_picker.value + timedelta(hours=12)).date()
                fecha_btn.content = ft.Text(fecha_val[0].strftime("%d/%m/%Y"))
            else:
                fecha_val[0] = None
                fecha_btn.content = ft.Text("Sin fecha límite")
            page.update()
            
        def open_dp_edit(e):
            date_picker.open = True
            page.update()
            
        fecha_btn = ft.OutlinedButton(
            content=fecha_val[0].strftime("%d/%m/%Y") if fecha_val[0] else "Sin fecha límite",
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=open_dp_edit
        )
        
        notas_edit = ft.TextField(
            label="Notas",
            value=self.mision.banco_mision.notas,
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=ft.Colors.GREY_800
        )
        
        recurrencia_val = self.mision.banco_mision.recurrencia_dias or 0
        recurrencia_edit = ft.TextField(
            label="Repetir cada X días (0 = no repetir)",
            value=str(recurrencia_val),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_800
        )
        
        def save_edits(e):
            with get_session() as session:
                m_db = session.get(MisionRegular, self.mision.id)
                if m_db:
                    b_db = m_db.banco_mision
                    b_db.dificultad = Dificultad(dificultad_edit.value)
                    b_db.prioridad = Prioridad(prioridad_edit.value)
                    b_db.notas = notas_edit.value
                    b_db.seccion_id = int(seccion_edit.value) if seccion_edit.value else None
                    b_db.recurrencia_dias = int(recurrencia_edit.value) if recurrencia_edit.value and recurrencia_edit.value.isdigit() else 0
                    m_db.fecha_limite = fecha_val[0]
                    session.commit()
            
            dialog.open = False
            if self.on_edit_callback:
                self.on_edit_callback()
            page.update()
            
        def delete_mission(e):
            with get_session() as session:
                m_db = session.get(MisionRegular, self.mision.id)
                if m_db:
                    b_id = m_db.banco_mision_id
                    b_db = session.get(BancoMisiones, b_id)
                    lista = b_db.lista if b_db else None
                    is_system = lista and lista.nombre in ["Misiones Diarias", "Misiones Semanales"]
                    
                    session.delete(m_db)
                    if b_db and not is_system:
                        session.delete(b_db)
                    session.commit()
            
            dialog.open = False
            if self.on_edit_callback:
                self.on_edit_callback()
            page.update()
            
        def cancel_edits(e):
            dialog.open = False
            page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text("Editar Misión"),
            content=ft.Column([dificultad_edit, prioridad_edit, seccion_edit, fecha_btn, recurrencia_edit, notas_edit], tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton("Eliminar", on_click=delete_mission, style=ft.ButtonStyle(color=ft.Colors.RED_ACCENT_400)),
                        ft.Row([
                            ft.TextButton("Cancelar", on_click=cancel_edits),
                            ft.FilledButton("Guardar", on_click=save_edits)
                        ], spacing=10)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    width=320
                )
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
        self.margin = ft.Margin.only(bottom=10)

    def complete_clicked(self, e):
        if self.checkbox.value:
            self.checkbox.disabled = True
            self.update()
            self.on_complete_callback(self.mision.id, self)


class QuestLogView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.filtro_lista_id = None
        self.is_system_list = False
        
        self.on_lists_changed_callback = None
        
        self.misiones_list = ft.Column(scroll=ft.ScrollMode.HIDDEN, expand=True)
        
        self.title_text = ft.Text("Misiones de Hoy", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE_70)
        self.list_options_menu = ft.PopupMenuButton(
            icon=ft.Icons.MORE_VERT,
            items=[
                ft.PopupMenuItem(content=ft.Text("Añadir Sección"), icon=ft.Icons.ADD, on_click=self.open_add_section),
                ft.PopupMenuItem(content=ft.Text("Editar Nombre"), icon=ft.Icons.EDIT, on_click=self.open_edit_list),
                ft.PopupMenuItem(content=ft.Text("Eliminar Lista"), icon=ft.Icons.DELETE, on_click=self.open_delete_list),
            ],
            visible=False,
            icon_color=ft.Colors.WHITE_54
        )
        self.title_row = ft.Row([self.title_text, self.list_options_menu], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.comun_text = ft.Text("0/5", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.raro_text = ft.Text("0/5", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        
        self.encuentro_comun_btn = ft.Container(
            content=ft.Row([
                ft.Image(src="grass_common.png", width=18, height=18, fit="contain"),
                ft.Text("Encuentro común", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD, size=11),
                self.comun_text
            ], tight=True, spacing=3),
            padding=4,
            border_radius=8,
            on_click=self.on_comun_click
        )
        
        self.encuentro_raro_btn = ft.Container(
            content=ft.Row([
                ft.Image(src="grass_rare.png", width=18, height=18, fit="contain"),
                ft.Text("Encuentro Raro", color=ft.Colors.PURPLE_400, weight=ft.FontWeight.BOLD, size=11),
                self.raro_text
            ], tight=True, spacing=3),
            padding=4,
            border_radius=8,
            on_click=self.on_raro_click
        )
        
        self.encuentros_row = ft.Row([
            self.encuentro_comun_btn,
            self.encuentro_raro_btn
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.content = ft.Column([
            self.encuentros_row,
            self.title_row,
            self.misiones_list
        ], expand=True)

    def get_rareza_widget(self, rareza: str):
        if rareza == "Común":
            text_color = ft.Colors.WHITE_70
            num_stars = 1
            weight = ft.FontWeight.BOLD
        elif rareza == "Raro":
            text_color = ft.Colors.BLUE_400
            num_stars = 2
            weight = ft.FontWeight.BOLD
        elif rareza == "Muy Raro":
            text_color = ft.Colors.PURPLE_400
            num_stars = 3
            weight = ft.FontWeight.W_900

        stars = [ft.Icon(ft.Icons.STAR, size=14, color=text_color) for _ in range(num_stars)]
        
        if rareza == "Muy Raro":
            grad_colors = [ft.Colors.PURPLE_300, ft.Colors.PURPLE_500, ft.Colors.DEEP_PURPLE_700]
            gradient = ft.LinearGradient(
                begin=ft.Alignment(-1.0, -1.0),
                end=ft.Alignment(1.0, 1.0),
                colors=grad_colors
            )
            return ft.ShaderMask(
                content=ft.Row([
                    ft.Text(rareza.upper(), size=12, weight=weight),
                    ft.Row(stars, spacing=0)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=4, tight=True),
                blend_mode=ft.BlendMode.SRC_IN,
                shader=gradient
            )
        else:
            return ft.Row([
                ft.Text(rareza.upper(), size=12, color=text_color, weight=weight),
                ft.Row(stars, spacing=0)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=4, tight=True)

    def on_comun_click(self, e):
        if not self.comun_text.value.startswith("5/"):
            dialog = ft.AlertDialog(
                bgcolor="#0C140C",
                title=ft.Row([
                    ft.Row([
                        ft.Image(src="grass_common.png", width=24, height=24, fit="contain"),
                        ft.Text("ENCUENTRO COMÚN", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD, size=16),
                    ], spacing=10),
                    ft.Text(self.comun_text.value, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD, size=16)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                content=ft.Column([
                    ft.Divider(height=1, color=ft.Colors.GREEN_900),
                    ft.Text(
                        "Completa 5 misiones de dificultad fácil para acceder a un encuentro con un pokémon:",
                        italic=True,
                        color=ft.Colors.WHITE_70,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Row([
                        self.get_rareza_widget("Común"),
                        ft.Text("o", size=12, color=ft.Colors.WHITE_54),
                        self.get_rareza_widget("Raro")
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True)
                ], tight=True, spacing=15),
                actions=[ft.TextButton("Cerrar", on_click=lambda ev: self.close_modal(ev, dialog))]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        else:
            def handle_proceed(ev):
                dialog.open = False
                self.page.update()
                
                from database import get_session
                from models import Estadisticas
                from sqlalchemy import select
                with get_session() as session:
                    stats = session.execute(select(Estadisticas)).scalars().first()
                    if stats:
                        stats.encuentro_comun_progreso = max(0, stats.encuentro_comun_progreso - 5)
                        session.commit()
                self.load_data()
                
                if hasattr(self, 'start_wild_encounter_fn'):
                    self.start_wild_encounter_fn("Común", lambda: self.on_encounter_finish("Común"))

            dialog = ft.AlertDialog(
                bgcolor="#0C140C",
                title=ft.Row([
                    ft.Row([
                        ft.Image(src="grass_common.png", width=24, height=24, fit="contain"),
                        ft.Text("ENCUENTRO LISTO", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD, size=16),
                    ], spacing=10),
                ]),
                content=ft.Text("Un Pokémon salvaje ha aparecido entre la hierba alta. ¿Quieres intentar capturarlo?", color=ft.Colors.WHITE_70),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda ev: self.close_modal(ev, dialog)),
                    ft.FilledButton("Proceder", on_click=handle_proceed, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700))
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
    def on_raro_click(self, e):
        if not self.raro_text.value.startswith("5/"):
            dialog = ft.AlertDialog(
                bgcolor="#170C1A",
                title=ft.Row([
                    ft.Row([
                        ft.Image(src="grass_rare.png", width=24, height=24, fit="contain"),
                        ft.Text("ENCUENTRO RARO", color=ft.Colors.PURPLE_400, weight=ft.FontWeight.BOLD, size=16),
                    ], spacing=10),
                    ft.Text(self.raro_text.value, color=ft.Colors.PURPLE_400, weight=ft.FontWeight.BOLD, size=16)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                content=ft.Column([
                    ft.Divider(height=1, color=ft.Colors.PURPLE_900),
                    ft.Text(
                        "Completa 5 misiones de dificultad normal o superior para acceder a un encuentro con un pokemon:",
                        italic=True,
                        color=ft.Colors.WHITE_70,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Row([
                        self.get_rareza_widget("Raro"),
                        ft.Text("o", size=12, color=ft.Colors.WHITE_54),
                        self.get_rareza_widget("Muy Raro")
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True)
                ], tight=True, spacing=15),
                actions=[ft.TextButton("Cerrar", on_click=lambda ev: self.close_modal(ev, dialog))]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        else:
            def handle_proceed(ev):
                dialog.open = False
                self.page.update()
                
                from database import get_session
                from models import Estadisticas
                from sqlalchemy import select
                with get_session() as session:
                    stats = session.execute(select(Estadisticas)).scalars().first()
                    if stats:
                        stats.encuentro_raro_progreso = max(0, stats.encuentro_raro_progreso - 5)
                        session.commit()
                self.load_data()
                
                if hasattr(self, 'start_wild_encounter_fn'):
                    self.start_wild_encounter_fn("Raro", lambda: self.on_encounter_finish("Raro"))

            dialog = ft.AlertDialog(
                bgcolor="#170C1A",
                title=ft.Row([
                    ft.Row([
                        ft.Image(src="grass_rare.png", width=24, height=24, fit="contain"),
                        ft.Text("ENCUENTRO LISTO", color=ft.Colors.PURPLE_400, weight=ft.FontWeight.BOLD, size=16),
                    ], spacing=10),
                ]),
                content=ft.Text("Un Pokémon inusual ha aparecido. ¿Estás preparado?", color=ft.Colors.WHITE_70),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda ev: self.close_modal(ev, dialog)),
                    ft.FilledButton("Proceder", on_click=handle_proceed, style=ft.ButtonStyle(bgcolor=ft.Colors.PURPLE_700))
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
    def close_modal(self, e, dialog):
        dialog.open = False
        self.page.update()

    def on_encounter_finish(self, tipo_encuentro):
        self.load_data()
        self.page.update()

    def did_mount(self):
        self.load_data()

    def set_filter(self, lista_id):
        self.filtro_lista_id = lista_id
        self.load_data()

    def load_data(self):
        self.misiones_list.controls.clear()
        
        with get_session() as session:
            stats = session.execute(select(Estadisticas)).scalars().first()
            progreso_comun = stats.encuentro_comun_progreso if stats else 0
            progreso_raro = stats.encuentro_raro_progreso if stats else 0
            
            self.comun_text.value = f"{progreso_comun}/5"
            self.raro_text.value = f"{progreso_raro}/5"
            
            if progreso_comun >= 5:
                self.encuentro_comun_btn.bgcolor = "#1A2E1A"
                self.encuentro_comun_btn.border = ft.Border.all(1, ft.Colors.GREEN_700)
            else:
                self.encuentro_comun_btn.bgcolor = ft.Colors.GREY_900
                self.encuentro_comun_btn.border = ft.Border.all(1, ft.Colors.GREY_800)
                
            if progreso_raro >= 5:
                self.encuentro_raro_btn.bgcolor = "#2E1A3C"
                self.encuentro_raro_btn.border = ft.Border.all(1, ft.Colors.PURPLE_700)
            else:
                self.encuentro_raro_btn.bgcolor = ft.Colors.GREY_900
                self.encuentro_raro_btn.border = ft.Border.all(1, ft.Colors.GREY_800)
                
            if self.filtro_lista_id is None:
                self.is_system_list = False
                self.list_options_menu.visible = False
                self.title_text.value = "Misiones de Hoy"
                misiones_activas = session.execute(
                    select(MisionRegular).where(
                        and_(
                            MisionRegular.completada == False,
                            MisionRegular.fecha_limite != None,
                            MisionRegular.fecha_limite <= date.today()
                        )
                    ).order_by(MisionRegular.orden)
                ).scalars().all()
                
                # Se ha desactivado la autogeneración de 3 misiones diarias al abrir la app.
                # diarias_hoy = [m for m in misiones_activas if m.fecha_asignacion == hoy]
                def render_mission(m):
                    card = MisionCard(m, on_complete=self.on_mission_complete, on_edit=self.on_mission_edit)
                    draggable = ft.Draggable(group="dnd", content=card, data={"type": "mission", "id": m.id})
                    dt = ft.DragTarget(group="dnd", content=draggable, on_accept=self.drag_accept, data={"type": "mission", "id": m.id})
                    return dt
                    
                for m in misiones_activas:
                    self.misiones_list.controls.append(render_mission(m))
                    
            else:
                lista = session.get(ListaTareas, self.filtro_lista_id)
                self.title_text.value = lista.nombre if lista else "Misiones"
                
                self.is_system_list = False
                if lista and lista.nombre in ["Misiones Diarias", "Misiones Semanales"]:
                    self.is_system_list = True
                    
                self.list_options_menu.visible = True
                if self.is_system_list:
                    self.list_options_menu.items = [
                        ft.PopupMenuItem(
                            content=ft.Text("Editar misiones " + ("Diarias" if lista.nombre == "Misiones Diarias" else "Semanales")), 
                            icon=ft.Icons.EDIT_DOCUMENT, 
                            on_click=self.open_edit_system_bank
                        )
                    ]
                else:
                    self.list_options_menu.items = [
                        ft.PopupMenuItem(content=ft.Text("Añadir Sección"), icon=ft.Icons.ADD, on_click=self.open_add_section),
                        ft.PopupMenuItem(content=ft.Text("Editar Nombre"), icon=ft.Icons.EDIT, on_click=self.open_edit_list),
                        ft.PopupMenuItem(content=ft.Text("Eliminar Lista"), icon=ft.Icons.DELETE, on_click=self.open_delete_list),
                    ]
                
                secciones = session.execute(
                    select(Seccion).where(Seccion.lista_id == self.filtro_lista_id).order_by(Seccion.orden)
                ).scalars().all()
                
                misiones_activas = session.execute(
                    select(MisionRegular).join(BancoMisiones).where(
                        and_(
                            MisionRegular.completada == False,
                            BancoMisiones.lista_id == self.filtro_lista_id
                        )
                    ).order_by(MisionRegular.orden)
                ).scalars().all()
                
                misiones_por_seccion = {None: []}
                for sec in secciones:
                    misiones_por_seccion[sec.id] = []
                    
                for m in misiones_activas:
                    sec_id = m.banco_mision.seccion_id
                    if sec_id in misiones_por_seccion:
                        misiones_por_seccion[sec_id].append(m)
                    else:
                        misiones_por_seccion[None].append(m)
                        
                def render_mission(m):
                    card = MisionCard(m, on_complete=self.on_mission_complete, on_edit=self.on_mission_edit)
                    draggable = ft.Draggable(group="dnd", content=card, data={"type": "mission", "id": m.id})
                    dt = ft.DragTarget(group="dnd", content=draggable, on_accept=self.drag_accept, data={"type": "mission", "id": m.id})
                    return dt
                    
                # Si hay secciones, proveer un espacio de dropzone explícito al inicio para "quitar sección"
                if secciones:
                    header_sin_sec = ft.Container(
                        content=ft.Text("Misiones Generales (arrastra aquí para quitar sección)", color=ft.Colors.WHITE_54, italic=True),
                        padding=10, margin=ft.Margin.only(top=5, bottom=5)
                    )
                    dt_sin_sec = ft.DragTarget(
                        group="dnd",
                        content=header_sin_sec,
                        on_accept=self.drag_accept,
                        data={"type": "section", "id": None}
                    )
                    self.misiones_list.controls.append(dt_sin_sec)
                    
                for m in misiones_por_seccion[None]:
                    self.misiones_list.controls.append(render_mission(m))
                    
                for sec in secciones:
                    header = ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DRAG_INDICATOR, color=ft.Colors.WHITE_54),
                            ft.Text(sec.nombre, weight=ft.FontWeight.BOLD, size=16, expand=True),
                            ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.WHITE_54, data=sec.id, on_click=self.delete_section)
                        ]),
                        padding=10,
                        bgcolor="#333333",
                        border_radius=5
                    )
                    
                    sec_dt = ft.DragTarget(
                        group="dnd",
                        content=ft.Draggable(group="dnd", content=header, data={"type": "section", "id": sec.id}),
                        on_accept=self.drag_accept,
                        data={"type": "section", "id": sec.id}
                    )
                    
                    # Agrupar visualmente con sombreado
                    sec_col = ft.Column([sec_dt], spacing=5)
                    for m in misiones_por_seccion[sec.id]:
                        sec_col.controls.append(render_mission(m))
                        
                    sec_container = ft.Container(
                        content=sec_col,
                        bgcolor=ft.Colors.WHITE_10,
                        padding=10,
                        border_radius=8,
                        margin=ft.Margin.only(top=10, bottom=10),
                        border=ft.Border.all(1, ft.Colors.WHITE_24)
                    )
                    
                    self.misiones_list.controls.append(sec_container)
                    
                if self.is_system_list and len(misiones_activas) == 0:
                    mensaje = ""
                    if lista.nombre == "Misiones Diarias":
                        mensaje = "¡Felicidades! Has completado todas las misiones diarias de hoy, vuelve mañana por más."
                    elif lista.nombre == "Misiones Semanales":
                        mensaje = "¡Felicidades! Has completado todas las misiones de esta semana, vuelve la próxima a por más."
                    
                    self.misiones_list.controls.append(
                        ft.Container(
                            content=ft.Text(mensaje, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE_54, size=16, italic=True),
                            padding=40,
                            alignment=ft.Alignment(0, 0)
                        )
                    )
                
                
        self.update()

    def on_mission_edit(self):
        self.load_data()
        if self.on_lists_changed_callback:
            self.on_lists_changed_callback()
            
    def drag_accept(self, e):
        src_id = e.src_id
        src_ctrl = self.page.get_control(src_id)
        if not src_ctrl: return
        
        drag_data = src_ctrl.data
        target_data = e.control.data
        
        if not isinstance(drag_data, dict) or not isinstance(target_data, dict): return
        if drag_data == target_data: return
        
        with get_session() as session:
            if drag_data["type"] == "section" and target_data["type"] == "section":
                secciones = session.execute(
                    select(Seccion).where(Seccion.lista_id == self.filtro_lista_id).order_by(Seccion.orden)
                ).scalars().all()
                sec_list = list(secciones)
                drag_idx = next((i for i, s in enumerate(sec_list) if s.id == drag_data["id"]), -1)
                target_idx = next((i for i, s in enumerate(sec_list) if s.id == target_data["id"]), -1)
                if drag_idx != -1 and target_idx != -1:
                    item = sec_list.pop(drag_idx)
                    sec_list.insert(target_idx, item)
                    for idx, s in enumerate(sec_list):
                        s.orden = idx
                    session.commit()
            
            elif drag_data["type"] == "mission" and target_data["type"] == "section":
                m = session.get(MisionRegular, drag_data["id"])
                if m:
                    m.banco_mision.seccion_id = target_data["id"] # if None it handles it
                    session.commit()
                    
            elif drag_data["type"] == "mission" and target_data["type"] == "mission":
                m_drag = session.get(MisionRegular, drag_data["id"])
                m_target = session.get(MisionRegular, target_data["id"])
                if m_drag and m_target:
                    m_drag.banco_mision.seccion_id = m_target.banco_mision.seccion_id
                    
                    if self.filtro_lista_id is None:
                        misiones = session.execute(
                            select(MisionRegular).where(
                                and_(
                                    MisionRegular.completada == False,
                                    MisionRegular.fecha_limite != None,
                                    MisionRegular.fecha_limite <= date.today()
                                )
                            ).order_by(MisionRegular.orden)
                        ).scalars().all()
                    else:
                        misiones = session.execute(
                            select(MisionRegular).join(BancoMisiones).where(
                                and_(
                                    MisionRegular.completada == False,
                                    BancoMisiones.lista_id == self.filtro_lista_id
                                )
                            ).order_by(MisionRegular.orden)
                        ).scalars().all()
                        
                    misiones_list = list(misiones)
                    d_idx = next((i for i, m in enumerate(misiones_list) if m.id == m_drag.id), -1)
                    t_idx = next((i for i, m in enumerate(misiones_list) if m.id == m_target.id), -1)
                    if d_idx != -1 and t_idx != -1:
                        item = misiones_list.pop(d_idx)
                        misiones_list.insert(t_idx, item)
                        for idx, ms in enumerate(misiones_list):
                            ms.orden = idx
                    session.commit()
                    
        self.load_data()
            
    def on_mission_complete(self, mision_id: int, card: MisionCard):
        with get_session() as session:
            exito, res = services.completar_mision(session, mision_id)
            
            if exito:
                self.load_data() # Recargamos UI
                if self.on_lists_changed_callback:
                    self.on_lists_changed_callback()
                
                if res.get('combo_diario'):
                    msg = f"¡Completada! +{res['xp_ganada']} XP (+{res.get('bonus_xp', 0)} Bonus Diario!)"
                elif res.get('combo_semanal'):
                    msg = f"¡Completada! +{res['xp_ganada']} XP (+{res.get('bonus_xp', 0)} Bonus Semanal!)"
                else:
                    msg = f"¡Completada! +{res['xp_ganada']} XP"
                if res.get('dano_jefe', 0) > 0:
                    msg += f" | Daño: {res['dano_jefe']}"
                    services.add_combat_log_message(f"Completaste una tarea y causaste {res['dano_jefe']} de daño al Jefe.")
                if res.get('loot'):
                    msg += f" | Botín: {res['loot']}"
                    
                bgcolor = ft.Colors.RED_900
                duration = 3000
                
                if res.get("nivel_usuario_subido"):
                    bgcolor = ft.Colors.BLUE_900
                    duration = 6000
                    msg += f"\n\n⬆️ ¡Nivel de Entrenador {res['nuevo_nivel_usuario']} alcanzado! +{res['monedas_bonus_nivel']} Monedas 🪙"
                    if res.get("objeto_nivel"):
                        msg += f"\n🎁 ¡Has recibido: {res['objeto_nivel']}!"
                        
                snack = ft.SnackBar(
                    content=ft.Text(msg, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    bgcolor=bgcolor,
                    duration=duration
                )
                self.page.overlay.append(snack)
                snack.open = True
                
                try:
                    self.page.update()
                except:
                    pass
                
                dialog_queue = []
                
                # Eclosión de Huevo
                huevo_res = res.get("huevo_progreso", {})
                if huevo_res.get("eclosionado"):
                    pk_id = huevo_res.get("pokemon_id")
                    if pk_id:
                        info = pokeapi.get_pokemon_info(pk_id)
                        nombre = info["name"].capitalize() if info else f"#{pk_id}"
                        sprite_url = info["sprites"].get("other", {}).get("official-artwork", {}).get("front_default") or info["sprites"].get("front_default")
                        
                        hatch_content = ft.Column([
                            ft.Image(src=sprite_url, width=150, height=150, fit="contain"),
                            ft.Text(f"¡Un {nombre} ha salido del cascarón!", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True, spacing=10)
                    else:
                        hatch_content = ft.Column([
                            ft.Icon(ft.Icons.MONETIZATION_ON, size=100, color=ft.Colors.AMBER_400),
                            ft.Text(f"¡El huevo contenía {huevo_res.get('monedas_compensacion')} monedas!\n(Ya tienes a todos los Pokémon de este tipo)", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True, spacing=10)
                        
                    hatch_dialog = ft.AlertDialog(
                        title=ft.Text("✨ ¡ECLOSIÓN! ✨", color=ft.Colors.GREEN_400, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
                        content=ft.Container(hatch_content, padding=20),
                        actions=[ft.TextButton("¡Increíble!")],
                        actions_alignment=ft.MainAxisAlignment.CENTER,
                        shape=ft.RoundedRectangleBorder(radius=15),
                        bgcolor="#1A2A1A"
                    )
                    dialog_queue.append(hatch_dialog)
                
                # Nivel Superior Dialog
                if res.get("pokemon_subidas"):
                    pk_cols = []
                    for pk_subida in res["pokemon_subidas"]:
                        evolucion = pk_subida.get("evolucion")
                        
                        if evolucion:
                            info_viejo = pokeapi.get_pokemon_info(evolucion["viejo_id"])
                            info_nuevo = pokeapi.get_pokemon_info(evolucion["nuevo_id"])
                            nombre_viejo = info_viejo["name"].capitalize() if info_viejo else ""
                            nombre_nuevo = info_nuevo["name"].capitalize() if info_nuevo else ""
                            sprite_viejo = info_viejo["sprites"].get("front_default") if info_viejo else None
                            sprite_nuevo = info_nuevo["sprites"].get("front_default") if info_nuevo else None
                            
                            pk_cols.append(
                                ft.Column([
                                    ft.Row([
                                        ft.Image(src=sprite_viejo, width=60, height=60) if sprite_viejo else ft.Container(),
                                        ft.Icon(ft.Icons.ARROW_FORWARD, color=ft.Colors.WHITE),
                                        ft.Image(src=sprite_nuevo, width=80, height=80) if sprite_nuevo else ft.Container()
                                    ], alignment=ft.MainAxisAlignment.CENTER),
                                    ft.Text(f"¡{nombre_viejo} ha evolucionado a {nombre_nuevo}!", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                                    ft.Text(f"Nvl. {pk_subida['nivel']}", color=ft.Colors.AMBER_400)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)
                            )
                        else:
                            info = pokeapi.get_pokemon_info(pk_subida["pokeapi_id"])
                            nombre = info["name"].capitalize() if info else f"#{pk_subida['pokeapi_id']}"
                            sprite_url = info["sprites"].get("front_default") if info else None
                            
                            pk_cols.append(
                                ft.Column([
                                    ft.Image(src=sprite_url, width=70, height=70) if sprite_url else ft.Container(),
                                    ft.Text(f"{nombre}", weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Nvl. {pk_subida['nivel']}", color=ft.Colors.AMBER_400)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)
                            )
                    
                    lvl_dialog = ft.AlertDialog(
                        title=ft.Text("¡Nivel Superior!", color=ft.Colors.AMBER_400, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
                        content=ft.Row(pk_cols, alignment=ft.MainAxisAlignment.CENTER, tight=True, spacing=15),
                        actions=[ft.TextButton("¡Genial!")],
                        actions_alignment=ft.MainAxisAlignment.CENTER,
                        shape=ft.RoundedRectangleBorder(radius=15),
                        bgcolor="#1A1A1A"
                    )
                    dialog_queue.append(lvl_dialog)
                    
                def show_next_dialog():
                    if dialog_queue:
                        dlg = dialog_queue.pop(0)
                        
                        def on_close(e):
                            try:
                                self.page.close(dlg)
                            except Exception:
                                dlg.open = False
                                self.page.update()
                            show_next_dialog()
                            
                        if dlg.actions:
                            dlg.actions[0].on_click = on_close
                        
                        try:
                            self.page.open(dlg)
                        except Exception:
                            if dlg not in self.page.overlay:
                                self.page.overlay.append(dlg)
                            dlg.open = True
                            self.page.update()
                            
                if dialog_queue:
                    show_next_dialog()

    def open_add_section(self, e):
        section_name_field = ft.TextField(label="Nombre de la Sección", autofocus=True)
        
        def save_section(e):
            if section_name_field.value:
                with get_session() as session:
                    max_orden = session.execute(
                        select(func.max(Seccion.orden)).where(Seccion.lista_id == self.filtro_lista_id)
                    ).scalar() or 0
                    
                    nueva_seccion = Seccion(
                        nombre=section_name_field.value,
                        lista_id=self.filtro_lista_id,
                        orden=max_orden + 1
                    )
                    session.add(nueva_seccion)
                    session.commit()
                dialog.open = False
                self.page.update()
                self.load_data()
                
        def cancel_dialog(e):
            dialog.open = False
            self.page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text("Nueva Sección"),
            content=section_name_field,
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_dialog),
                ft.FilledButton("Crear", on_click=save_section)
            ]
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def open_edit_system_bank(self, e):
        def close_dlg(e):
            dialog.open = False
            self.page.update()

        def add_to_bank(e):
            if not new_mission_field.value:
                return
            with get_session() as session:
                lista = session.get(ListaTareas, self.filtro_lista_id)
                cooldown = 1 if lista.nombre == "Misiones Diarias" else 7
                nueva = BancoMisiones(
                    titulo=new_mission_field.value,
                    lista_id=self.filtro_lista_id,
                    cooldown_dias=cooldown,
                    dificultad=Dificultad.NORMAL
                )
                session.add(nueva)
                session.commit()
            new_mission_field.value = ""
            refresh_list()

        def delete_from_bank(b_id):
            from sqlalchemy import delete
            with get_session() as session:
                b = session.get(BancoMisiones, b_id)
                if b:
                    session.execute(delete(MisionRegular).where(MisionRegular.banco_mision_id == b_id))
                    session.delete(b)
                    session.commit()
            refresh_list()

        def refresh_list():
            with get_session() as session:
                bancos = session.execute(
                    select(BancoMisiones).where(BancoMisiones.lista_id == self.filtro_lista_id)
                ).scalars().all()
                
            bank_list.controls.clear()
            for b in bancos:
                bank_list.controls.append(
                    ft.Row([
                        ft.Text(b.titulo, expand=True, color=ft.Colors.WHITE, size=13),
                        ft.IconButton(ft.Icons.DELETE, on_click=lambda e, bid=b.id: delete_from_bank(bid), icon_color=ft.Colors.RED_400)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            self.page.update()

        new_mission_field = ft.TextField(label="Nueva misión base...", expand=True, text_size=13)
        bank_list = ft.ListView(expand=True, spacing=5)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Editar Banco de Sistema"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Estas misiones rotarán aleatoriamente.", size=12, color=ft.Colors.WHITE_54),
                    ft.Row([new_mission_field, ft.IconButton(ft.Icons.ADD, on_click=add_to_bank, icon_color=ft.Colors.GREEN_400)]),
                    ft.Divider(),
                    bank_list
                ]),
                width=350,
                height=450
            ),
            actions=[ft.TextButton("Cerrar", on_click=close_dlg)]
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        refresh_list()

    def delete_section(self, e):
        sec_id = e.control.data
        def confirm_delete(e):
            with get_session() as session:
                sec = session.get(Seccion, sec_id)
                if sec:
                    misiones = session.execute(select(BancoMisiones).where(BancoMisiones.seccion_id == sec_id)).scalars().all()
                    for m in misiones:
                        m.seccion_id = None
                    session.delete(sec)
                    session.commit()
            dialog.open = False
            self.page.update()
            self.load_data()
            
        def cancel_delete(e):
            dialog.open = False
            self.page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text("¿Eliminar Sección?"),
            content=ft.Text("Las tareas de esta sección quedarán 'Sin sección'. La sección desaparecerá."),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_delete),
                ft.FilledButton("Eliminar", on_click=confirm_delete, bgcolor=ft.Colors.RED)
            ]
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def open_edit_list(self, e):
        with get_session() as session:
            lista = session.get(ListaTareas, self.filtro_lista_id)
            if not lista: return
            current_name = lista.nombre
            current_icon = lista.icono or "FOLDER"
            
        name_field = ft.TextField(label="Nombre", value=current_name, autofocus=True)
        selected_icon = [current_icon]
        
        icons_to_choose = [
            "FOLDER", "HOME", "WORK", "SCHOOL", "SHOPPING_CART",
            "FAVORITE", "STAR", "FITNESS_CENTER", "FLIGHT",
            "VIDEOGAME_ASSET", "BOOK", "RESTAURANT",
            "MUSIC_NOTE", "ROCKET_LAUNCH", "CAKE", "LIGHTBULB",
            "PETS", "BRUSH", "CODE", "NATURE"
        ]

        def icon_clicked(e, icon_name):
            selected_icon[0] = icon_name
            for btn in icon_row.controls:
                btn.icon_color = ft.Colors.RED_ACCENT_400 if btn.data == icon_name else ft.Colors.WHITE
            icon_row.update()

        icon_row = ft.Row(wrap=True, alignment=ft.MainAxisAlignment.CENTER)
        for ic in icons_to_choose:
            icon_row.controls.append(
                ft.IconButton(
                    icon=getattr(ft.Icons, ic, ft.Icons.STAR),
                    data=ic,
                    icon_color=ft.Colors.RED_ACCENT_400 if ic == selected_icon[0] else ft.Colors.WHITE,
                    on_click=lambda e, name=ic: icon_clicked(e, name)
                )
            )
            
        content_col = ft.Column([
            name_field,
            ft.Text("Selecciona un icono:", color=ft.Colors.WHITE_54, size=12),
            icon_row
        ], tight=True)
        
        def save_edit(e):
            if not name_field.value: return
            with get_session() as save_session:
                lista_edit = save_session.get(ListaTareas, self.filtro_lista_id)
                if lista_edit:
                    lista_edit.nombre = name_field.value
                    lista_edit.icono = selected_icon[0]
                    save_session.commit()
            
            dialog.open = False
            self.load_data()
            if self.on_lists_changed_callback:
                self.on_lists_changed_callback()
            self.page.update()
            
        def cancel_edit(e):
            dialog.open = False
            self.page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text("Editar Lista"),
            content=content_col,
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_edit),
                ft.FilledButton("Guardar", on_click=save_edit)
            ]
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def open_delete_list(self, e):
        def confirm_delete(e):
            with get_session() as del_session:
                bancos = del_session.execute(select(BancoMisiones).where(BancoMisiones.lista_id == self.filtro_lista_id)).scalars().all()
                banco_ids = [b.id for b in bancos]
                
                if banco_ids:
                    del_session.execute(delete(MisionRegular).where(MisionRegular.banco_mision_id.in_(banco_ids)))
                    del_session.execute(delete(BancoMisiones).where(BancoMisiones.lista_id == self.filtro_lista_id))
                
                del_session.execute(delete(Seccion).where(Seccion.lista_id == self.filtro_lista_id))
                del_session.execute(delete(ListaTareas).where(ListaTareas.id == self.filtro_lista_id))
                del_session.commit()
                
            dialog.open = False
            self.filtro_lista_id = None
            self.load_data()
            if self.on_lists_changed_callback:
                self.on_lists_changed_callback()
            self.page.update()
            
        def cancel_delete(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("¿Eliminar Lista?"),
            content=ft.Text("Se eliminarán todas las misiones y secciones de esta lista. Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_delete),
                ft.FilledButton("Eliminar", on_click=confirm_delete, bgcolor=ft.Colors.RED)
            ]
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def open_add_mission_form(self):
        title_field = ft.TextField(label="Título de la tarea", bgcolor="#252525")
        cat_dropdown = ft.Dropdown(
            label="Lista",
            bgcolor="#252525"
        )
        seccion_dropdown = ft.Dropdown(
            label="Sección",
            bgcolor="#252525",
            options=[ft.dropdown.Option("", "Sin sección")],
            value=""
        )
        
        with get_session() as session:
            listas = session.execute(select(ListaTareas)).scalars().all()
            cat_dropdown.options = [ft.dropdown.Option(key=str(l.id), text=l.nombre) for l in listas]
            if listas:
                cat_dropdown.value = str(self.filtro_lista_id) if self.filtro_lista_id else str(listas[0].id)
                secs = session.execute(select(Seccion).where(Seccion.lista_id == int(cat_dropdown.value)).order_by(Seccion.orden)).scalars().all()
                for s in secs:
                    seccion_dropdown.options.append(ft.dropdown.Option(str(s.id), s.nombre))
        
        def update_secciones(e):
            if cat_dropdown.value:
                with get_session() as s_session:
                    secs = s_session.execute(select(Seccion).where(Seccion.lista_id == int(cat_dropdown.value)).order_by(Seccion.orden)).scalars().all()
                    seccion_dropdown.options = [ft.dropdown.Option("", "Sin sección")] + [ft.dropdown.Option(str(s.id), s.nombre) for s in secs]
                    seccion_dropdown.value = ""
                    sheet.update()
                    
        cat_dropdown.on_change = update_secciones
                
        dificultad_dropdown = ft.Dropdown(
            label="Dificultad",
            bgcolor="#252525",
            options=[ft.dropdown.Option(d.value) for d in Dificultad],
            value=Dificultad.NORMAL.value
        )
        prioridad_dropdown = ft.Dropdown(
            label="Prioridad",
            bgcolor="#252525",
            options=[ft.dropdown.Option(p.value) for p in Prioridad],
            value=Prioridad.SIN_PRIORIDAD.value
        )
        
        fecha_limite_val = [None]
        
        date_picker = ft.DatePicker(
            on_change=lambda e: on_date_change(e),
            on_dismiss=lambda e: on_date_change(e)
        )
        self.page.overlay.append(date_picker)

        def on_date_change(e):
            if date_picker.value:
                from datetime import timedelta
                fecha_limite_val[0] = (date_picker.value + timedelta(hours=12)).date()
                fecha_btn.content = ft.Text(fecha_limite_val[0].strftime("%d/%m/%Y"))
            else:
                fecha_limite_val[0] = None
                fecha_btn.content = ft.Text("Sin fecha límite")
            self.page.update()
            
        def open_dp_add(e):
            date_picker.open = True
            self.page.update()
            
        fecha_btn = ft.OutlinedButton(
            content="Sin fecha límite",
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=open_dp_add
        )
        
        notas_input = ft.TextField(
            label="Notas (opcional)",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=ft.Colors.GREY_800
        )
        
        recurrencia_input = ft.TextField(
            label="Repetir cada X días (0 = no repetir)",
            value="0",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREY_800
        )
        
        def save_mission(e):
            if not title_field.value or not cat_dropdown.value:
                return
            
            with get_session() as session:
                nueva_mision = BancoMisiones(
                    titulo=title_field.value,
                    lista_id=int(cat_dropdown.value),
                    cooldown_dias=1,
                    dificultad=Dificultad(dificultad_dropdown.value),
                    prioridad=Prioridad(prioridad_dropdown.value),
                    notas=notas_input.value,
                    seccion_id=int(seccion_dropdown.value) if seccion_dropdown.value else None,
                    recurrencia_dias=int(recurrencia_input.value) if recurrencia_input.value and recurrencia_input.value.isdigit() else 0
                )
                session.add(nueva_mision)
                session.commit()
                
                max_orden = session.execute(
                    select(func.max(MisionRegular.orden))
                ).scalar() or 0
                
                mision_activa = MisionRegular(
                    banco_mision_id=nueva_mision.id,
                    tipo=MissionType.DIARIA,
                    completada=False,
                    fecha_asignacion=date.today(),
                    fecha_limite=fecha_limite_val[0],
                    orden=max_orden + 1
                )
                session.add(mision_activa)
                session.commit()
            
            sheet.open = False
            self.load_data()
            if self.on_lists_changed_callback:
                self.on_lists_changed_callback()
            self.page.update()
            
        sheet = ft.BottomSheet(
            content=ft.Container(
                padding=20,
                bgcolor="#1E1E1E",
                height=self.page.height * 0.8 if self.page else 600,
                content=ft.Column([
                    ft.Text("Añadir Nueva Misión", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_ACCENT_400),
                    title_field,
                    cat_dropdown,
                    seccion_dropdown,
                    ft.Row([dificultad_dropdown, prioridad_dropdown]),
                    fecha_btn,
                    recurrencia_input,
                    notas_input,
                    ft.FilledButton("Guardar Tarea", on_click=save_mission, bgcolor=ft.Colors.RED_ACCENT_400, color=ft.Colors.WHITE)
                ], tight=False, scroll=ft.ScrollMode.AUTO)
            )
        )
        self.page.overlay.append(sheet)
        sheet.open = True
        self.page.update()
