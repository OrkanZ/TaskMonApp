import pokeapi

def run():
    print("Testing Snivy (495) at level 16:")
    new_id_1 = pokeapi.check_evolution(495, 16)
    print(f"Result: {new_id_1}")
    
    print("Testing Snivy (495) at level 17:")
    new_id_2 = pokeapi.check_evolution(495, 17)
    print(f"Result: {new_id_2}")
    
    print("Testing Servine (496) at level 35:")
    new_id_3 = pokeapi.check_evolution(496, 35)
    print(f"Result: {new_id_3}")
    
    print("Testing Servine (496) at level 36:")
    new_id_4 = pokeapi.check_evolution(496, 36)
    print(f"Result: {new_id_4}")

if __name__ == "__main__":
    run()
