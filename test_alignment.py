import flet as ft

def main(page):
    try:
        print("top_center?", hasattr(ft.alignment, "top_center"))
        print("center_top?", hasattr(ft.alignment, "center_top"))
        print("Alignment?", hasattr(ft, "Alignment"))
        print("top_center is:", ft.alignment.top_center if hasattr(ft.alignment, "top_center") else "missing")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main(None)
