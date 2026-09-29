import flet as ft
import flet.canvas as cv

def main(page):
    try:
        c = cv.Canvas([
            cv.Oval(0, 0, 160, 40, paint=ft.Paint(color="#1A3311"))
        ], width=160, height=40)
        print("Success Canvas Oval!")
    except Exception as e:
        print("Canvas Error:", type(e).__name__)

if __name__ == "__main__":
    main(None)
