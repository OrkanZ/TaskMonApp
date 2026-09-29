import flet as ft

def main(page):
    try:
        p = ft.Padding(left=15, top=5, right=40, bottom=5)
        m = ft.Margin(left=20, top=20, right=0, bottom=0)
        br = ft.border_radius.all(8)
        print("Success basic padding/margin")
    except Exception as e:
        print("Error 1:", type(e).__name__, e)

if __name__ == "__main__":
    main(None)
