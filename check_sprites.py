import requests

items = [
    "poke-ball", "rare-candy", "sun-stone", "fire-stone", "water-stone", 
    "leaf-stone", "thunder-stone", "moon-stone", "dawn-stone", "dusk-stone", 
    "shiny-stone", "pecha-berry", "lucky-egg", "linking-cord", 
    "cover-fossil", "plume-fossil", "egg"
]

base_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/{}.png"

for item in items:
    url = base_url.format(item)
    res = requests.head(url)
    print(f"{item}: {res.status_code}")
