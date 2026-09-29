import flet as ft

import asyncio
from services import update_system_missions
from views.quest_log import QuestLogView
from views.team import TeamView
from views.pokedex import PokedexView
from views.inventory import InventoryView
from views.shop import ShopView
from views.profile_widget import ProfileWidget
from views.boss_screen import BossView

from database import get_session
from models import ListaTareas, MisionRegular, BancoMisiones
from sqlalchemy import select, func, and_, or_
from datetime import date

def main(page: ft.Page):
    page.title = "TaskMon - MVP"
    page.window.width = 393
    page.window.height = 851
    page.padding = 0
    
    profile_widget = ProfileWidget()
    
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.RED,
    )
    page.bgcolor = "#121212"

    views = {
        0: QuestLogView(),
        1: TeamView(),
        2: PokedexView(),
        3: InventoryView(),
        4: ShopView(),
        5: BossView()
    }

    content_area = ft.Container(
        content=views[0],
        expand=True,
        padding=20
    )

    appbar_title_text = ft.Text("Misiones", weight=ft.FontWeight.BOLD)

    def on_nav_change(e):
        index = e.control.selected_index
        content_area.content = views[index]
        
        if index == 1:
            content_area.padding = 0
        else:
            content_area.padding = 20
        
        view_titles = {
            0: "Misiones",
            1: "Equipo",
            2: "Pokédex",
            3: "Inventario",
            4: "Tienda"
        }
        appbar_title_text.value = view_titles.get(index, "Misiones")
        
        # Ocultar o mostrar el FAB (solo en la pestaña de Misiones, index 0, y si no es lista del sistema)
        if index == 0:
            page.floating_action_button.visible = not getattr(views[0], 'is_system_list', False)
        else:
            page.floating_action_button.visible = False
        
        page.update()

    bottom_nav = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.FORMAT_LIST_BULLETED, label="Misiones"),
            ft.NavigationBarDestination(icon=ft.Icons.PEOPLE, label="Equipo"),
            ft.NavigationBarDestination(icon=ft.Icons.CATCHING_POKEMON, label="Pokédex"),
            ft.NavigationBarDestination(icon=ft.Icons.BACKPACK, label="Inventario"),
            ft.NavigationBarDestination(icon=ft.Icons.STOREFRONT, label="Tienda"),
        ],
        on_change=on_nav_change,
        selected_index=0,
        bgcolor="#1E1E1E"
    )

    main_layout = ft.Column(
        controls=[content_area],
        expand=True
    )

    page.add(main_layout)
    page.navigation_bar = bottom_nav
    
    def start_wild_encounter(rareza, on_finish_callback):
        from views.encounter import EncounterView
        
        def finish_encounter():
            page.controls.remove(battle_view)
            main_layout.visible = True
            page.navigation_bar.visible = True
            if hasattr(page, 'appbar') and page.appbar:
                page.appbar.visible = True
            
            # Solo mostrar FAB si estamos en la pestaña Misiones y no en lista de sistema
            is_system = getattr(views[0], 'is_system_list', False)
            page.floating_action_button.visible = (bottom_nav.selected_index == 0 and not is_system)
            
            page.update()
            on_finish_callback()
            
        battle_view = EncounterView(rareza=rareza, on_finish=finish_encounter)
        
        main_layout.visible = False
        page.navigation_bar.visible = False
        if hasattr(page, 'appbar') and page.appbar:
            page.appbar.visible = False
        page.floating_action_button.visible = False
        
        page.add(battle_view)
        page.update()
        
    def start_boss_encounter(pokemon_id, level, boss_id, on_finish_callback):
        from views.encounter import EncounterView
        def finish_encounter():
            page.controls.remove(battle_view)
            main_layout.visible = True
            page.navigation_bar.visible = True
            if hasattr(page, 'appbar') and page.appbar:
                page.appbar.visible = True
            is_system = getattr(views[0], 'is_system_list', False)
            page.floating_action_button.visible = (bottom_nav.selected_index == 0 and not is_system)
            page.update()
            on_finish_callback()
            
        battle_view = EncounterView(rareza="Legendario", on_finish=finish_encounter, forced_pokemon_id=pokemon_id, forced_level=level, is_boss=True, boss_id=boss_id)
        
        main_layout.visible = False
        page.navigation_bar.visible = False
        if hasattr(page, 'appbar') and page.appbar:
            page.appbar.visible = False
        page.floating_action_button.visible = False
        
        page.add(battle_view)
        page.update()
        
    views[0].start_wild_encounter_fn = start_wild_encounter
    views[5].start_boss_encounter_fn = start_boss_encounter
    
    # Añadir FAB
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.RED_ACCENT_400,
        on_click=lambda e: views[0].open_add_mission_form()
    )
    
    # Drawer y AppBar para Listas
    drawer_list_ids = []
    
    async def open_add_list_dialog_async():
        await page.close_drawer()
        
        name_field = ft.TextField(label="Nombre de la Lista", autofocus=True)
        selected_icon = ["FOLDER"]
        
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
        
        def save_list(e):
            if not name_field.value:
                return
            with get_session() as session:
                nueva = ListaTareas(nombre=name_field.value, icono=selected_icon[0], color="#FFFFFF")
                session.add(nueva)
                session.commit()
            dialog.open = False
            rebuild_drawer()
            
        def cancel_dialog(e):
            dialog.open = False
            page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text("Nueva Lista"),
            content=content_col,
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_dialog),
                ft.FilledButton("Guardar", on_click=save_list)
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def handle_drawer_change(e):
        idx = e.control.selected_index
        if idx < len(drawer_list_ids):
            list_id = drawer_list_ids[idx]
            if list_id == "ADD_LIST":
                page.run_task(open_add_list_dialog_async)
            else:
                page.run_task(close_drawer_and_filter_async, list_id)

    drawer = ft.NavigationDrawer(on_change=handle_drawer_change)
    page.drawer = drawer
    
    async def close_drawer_and_filter_async(list_id):
        views[0].set_filter(list_id)
        if hasattr(views[0], 'is_system_list') and views[0].is_system_list:
            page.floating_action_button.visible = False
        else:
            # Solo visible si estamos en la pestaña 0
            page.floating_action_button.visible = (bottom_nav.selected_index == 0)
        await page.close_drawer()
        page.update()
    
    def build_drawer():
        drawer.controls.clear()
        drawer_list_ids.clear()
        
        with get_session() as session:
            hoy_count = session.execute(
                select(func.count(MisionRegular.id))
                .where(and_(
                    MisionRegular.completada == False,
                    MisionRegular.fecha_limite != None,
                    MisionRegular.fecha_limite <= date.today()
                ))
            ).scalar()
            
            drawer.controls.append(
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.CALENDAR_TODAY,
                    label=f"Hoy ({hoy_count})"
                )
            )
            drawer_list_ids.append(None)
            
            listas = session.execute(select(ListaTareas)).scalars().all()
            
            def list_sort_key(l):
                if l.nombre == "Misiones Diarias": return 0
                if l.nombre == "Misiones Semanales": return 1
                return 2
                
            listas = sorted(listas, key=list_sort_key)
            
            for l in listas:
                list_count = session.execute(
                    select(func.count(MisionRegular.id))
                    .join(BancoMisiones, MisionRegular.banco_mision_id == BancoMisiones.id)
                    .where(and_(
                        BancoMisiones.lista_id == l.id,
                        MisionRegular.completada == False
                    ))
                ).scalar()
                
                icon_data = getattr(ft.Icons, l.icono, ft.Icons.STAR)
                drawer.controls.append(
                    ft.NavigationDrawerDestination(
                        icon=icon_data,
                        label=f"{l.nombre} ({list_count})"
                    )
                )
                drawer_list_ids.append(l.id)
                
        # Añadir Lista Nueva
        drawer.controls.append(
            ft.NavigationDrawerDestination(
                icon=ft.Icons.ADD,
                label="Añadir Lista Nueva"
            )
        )
        drawer_list_ids.append("ADD_LIST")

    def rebuild_drawer():
        build_drawer()
        current_filter = views[0].filtro_lista_id
        if current_filter in drawer_list_ids:
            drawer.selected_index = drawer_list_ids.index(current_filter)
        else:
            drawer.selected_index = 0
            views[0].set_filter(None)
        
        drawer.update()
        page.update()
        
    def update_global_state():
        rebuild_drawer()
        profile_widget.update_data()
        views[4].load_data()
        views[5].load_data()
        
    views[0].on_lists_changed_callback = update_global_state
    views[3].on_item_used_callback = update_global_state
    views[4].on_buy_callback = update_global_state

    build_drawer()
    
    async def open_drawer(e):
        await page.show_drawer()
        page.update()
    
    def go_to_boss(e):
        content_area.content = views[5]
        content_area.padding = 0
        appbar_title_text.value = "BOSS"
        page.floating_action_button.visible = False
        page.update()

    boss_button = ft.Container(
        content=ft.Image(src="boss_icon.png", color=ft.Colors.RED_ACCENT_400, width=32, height=32, fit="contain"),
        on_click=go_to_boss, 
        tooltip="Boss",
        padding=8,
        ink=True,
        border_radius=20
    )

    page.appbar = ft.AppBar(
        leading=ft.IconButton(ft.Icons.MENU, on_click=open_drawer),
        leading_width=50,
        title=appbar_title_text,
        actions=[profile_widget, boss_button],
        bgcolor="#1E1E1E"
    )

    async def system_missions_loop():
        last_checked_day = date.today()
        # Actualizar al inicio
        with get_session() as session:
            update_system_missions(session)
            session.commit()
            
        while True:
            await asyncio.sleep(60)
            now = date.today()
            if now > last_checked_day:
                last_checked_day = now
                with get_session() as session:
                    update_system_missions(session)
                    session.commit()
                # Actualizar UI si estamos en misiones
                update_global_state()
                page.update()

    def check_starter():
        from models import PokemonCapturado, RegistroPokedex
        from pokeapi import get_pokemon_info
        
        with get_session() as session:
            count = session.execute(select(func.count(PokemonCapturado.id))).scalar()
            
        if count == 0:
            def pick_starter(pid):
                with get_session() as session:
                    session.add(PokemonCapturado(pokeapi_id=pid, nivel=1, en_equipo=True))
                    if not session.execute(select(RegistroPokedex).where(RegistroPokedex.pokeapi_id == pid)).scalars().first():
                        session.add(RegistroPokedex(pokeapi_id=pid))
                    session.commit()
                dialog.open = False
                page.update()
                update_global_state()
            
            s_info = get_pokemon_info(495)
            t_info = get_pokemon_info(498)
            o_info = get_pokemon_info(501)
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("¡Bienvenido!\nElige tu Pokémon inicial", text_align=ft.TextAlign.CENTER, size=20),
                content=ft.Column([
                    ft.Row([
                        ft.Image(src=s_info["sprites"]["front_default"], width=80, height=80),
                        ft.FilledButton("Snivy", on_click=lambda _: pick_starter(495), style=ft.ButtonStyle(color=ft.Colors.GREEN_400, bgcolor=ft.Colors.GREEN_900))
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                    
                    ft.Row([
                        ft.Image(src=t_info["sprites"]["front_default"], width=80, height=80),
                        ft.FilledButton("Tepig", on_click=lambda _: pick_starter(498), style=ft.ButtonStyle(color=ft.Colors.RED_400, bgcolor=ft.Colors.RED_900))
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                    
                    ft.Row([
                        ft.Image(src=o_info["sprites"]["front_default"], width=80, height=80),
                        ft.FilledButton("Oshawott", on_click=lambda _: pick_starter(501), style=ft.ButtonStyle(color=ft.Colors.BLUE_400, bgcolor=ft.Colors.BLUE_900))
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ], tight=True, spacing=20)
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

    check_starter()
    
    page.run_task(system_missions_loop)
    page.update()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
