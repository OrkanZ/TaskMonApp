import flet as ft

def main(page):
    print("BorderRadius?", hasattr(ft, "BorderRadius"))
    print("border_radius?", hasattr(ft, "border_radius"))
    if hasattr(ft, "border_radius"):
        print("border_radius.only?", hasattr(ft.border_radius, "only"))
    print("Padding?", hasattr(ft, "Padding"))
    print("padding?", hasattr(ft, "padding"))
    if hasattr(ft, "padding"):
        print("padding.only?", hasattr(ft.padding, "only"))
    print("Margin?", hasattr(ft, "Margin"))
    print("margin?", hasattr(ft, "margin"))

if __name__ == "__main__":
    main(None)
