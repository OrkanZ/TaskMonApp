import flet as ft

def main(page):
    try:
        s = ft.Scale(scale_y=0.25)
        print("Success Scale!")
    except Exception as e:
        print("Scale error:", type(e).__name__)

if __name__ == "__main__":
    main(None)
