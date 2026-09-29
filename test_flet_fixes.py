import flet as ft

def main(page):
    try:
        b = ft.Border(top=ft.BorderSide(3, "#424242"))
        print("Success Border!")
    except Exception as e:
        print("Border Error:", type(e).__name__)

    try:
        r = ft.border_radius.only(top_left=8)
        print("Success Border Radius!")
    except Exception as e:
        print("Border Radius Error:", type(e).__name__)
        
if __name__ == "__main__":
    main(None)
