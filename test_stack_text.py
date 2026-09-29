import flet as ft

def main(page):
    try:
        t = ft.Stack([
            ft.Text(
                "Outline", 
                style=ft.TextStyle(
                    foreground=ft.Paint(
                        style=ft.PaintingStyle.STROKE,
                        stroke_width=3,
                        color=ft.colors.BLACK
                    )
                )
            ),
            ft.Text("Outline", color="white"),
        ])
        print("Success Paint Stroke!")
    except Exception as e:
        print("Paint Stroke Error:", type(e).__name__)

if __name__ == "__main__":
    main(None)
