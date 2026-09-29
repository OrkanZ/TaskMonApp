import random

def simular_recompensas_nivel_5(n=100):
    resultados = {
        "Huevo": 0,
        "Fosil Pluma": 0,
        "Fosil Tapa": 0
    }
    
    for _ in range(n):
        r = random.random()
        if r < 0.90:
            resultados["Huevo"] += 1
        elif r < 0.95:
            resultados["Fosil Pluma"] += 1
        else:
            resultados["Fosil Tapa"] += 1
            
    print(f"--- Resultados de {n} simulaciones de recompensa de Nivel 5 ---")
    print(f"Huevos obtenidos: {resultados['Huevo']} (Esperado: ~{n * 0.90:.0f})")
    print(f"Fosil Pluma obtenidos: {resultados['Fosil Pluma']} (Esperado: ~{n * 0.05:.0f})")
    print(f"Fosil Tapa obtenidos: {resultados['Fosil Tapa']} (Esperado: ~{n * 0.05:.0f})")
    print("----------------------------------------------------------------")

if __name__ == "__main__":
    simular_recompensas_nivel_5(100)
