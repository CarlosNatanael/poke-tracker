# Crie um arquivo teste_api.py e rode ele
import requests

RA_USER = "CarlosNatanael"
RA_API_KEY = "Oy6GOQ5nOO3l8H3TkvFMw2QABo7Kw1Mn"

url = "https://retroachievements.org/API/API_GetUserCompletedGames.php"
params = {'z': RA_USER, 'y': RA_API_KEY, 'u': RA_USER}

response = requests.get(url, params=params)
data = response.json()

print("--- SEUS JOGOS COMPLETOS ---")
for game in data:
    # Imprime ID e Título de tudo que tem "Pok" no nome (com ou sem acento)
    if "Pok" in game['Title']: 
        print(f"ID: {game['GameID']}  | Título: {game['Title']} | Hardcore: {game['HardcoreMode']}")