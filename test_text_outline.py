import flet as ft

def main(page):
    try:
        t = ft.Text(
            "Hello Outline", 
            style=ft.TextStyle(
                shadow=ft.BoxShadow(
                    blur_radius=2, 
                    color=ft.colors.BLACK, 
                    offset=ft.Offset(1, 1)
                )
            )
        )
        print("Success Text Shadow!")
    except Exception as e:
        print("Text Shadow Error:", type(e).__name__)

if __name__ == "__main__":
    main(None)
