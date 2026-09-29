import flet as ft

def main(page):
    c = ft.Container(top=10, left=5)
    print("Success Container!")
    
    try:
        m = ft.margin.only(top=10)
        print("ft.margin.only works")
    except Exception as e:
        print("ft.margin.only Error:", type(e).__name__)

if __name__ == "__main__":
    main(None)
