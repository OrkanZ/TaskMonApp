import requests
import json

def test():
    # Snivy species
    res = requests.get("https://pokeapi.co/api/v2/pokemon-species/495/")
    data = res.json()
    evo_url = data["evolution_chain"]["url"]
    
    res2 = requests.get(evo_url)
    data2 = res2.json()
    
    with open("evo_chain_snivy.json", "w") as f:
        json.dump(data2, f, indent=2)
        
if __name__ == "__main__":
    test()
