import flet as ft

def main(page: ft.Page):
    snack = ft.SnackBar(ft.Text("Hello SnackBar!"))
    
    # Try overlay
    page.overlay.append(snack)
    snack.open = True
    page.update()
    
    print("Overlay append succeeded!")
    page.window.destroy()

ft.run(main)
