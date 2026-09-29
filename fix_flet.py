import os

files = [
    r"c:\Users\pablo\Documents\TaskMonApp\main.py",
    r"c:\Users\pablo\Documents\TaskMonApp\views\quest_log.py",
    r"c:\Users\pablo\Documents\TaskMonApp\views\team.py",
    r"c:\Users\pablo\Documents\TaskMonApp\views\pokedex.py",
    r"c:\Users\pablo\Documents\TaskMonApp\views\inventory.py"
]

for fpath in files:
    if not os.path.exists(fpath): continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace("ft.colors.", "ft.Colors.")
    content = content.replace("ft.icons.", "ft.Icons.")
    content = content.replace("WHITE70", "WHITE_70")
    content = content.replace("WHITE54", "WHITE_54")
    
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
