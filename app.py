from flask import Flask, render_template
import requests
from games_data import POKEMON_GAMES

app = Flask(__name__)

RA_USER = "CarlosNatanael"
RA_API_KAY = "Oy6GOQ5nOO3l8H3TkvFMw2QABo7Kw1Mn"

@app.route('/')
def index():
    url = "https://retroachievements.org/API/API_GetUserCompletedGames.php"
    params = {
        'z': RA_USER,
        'y': RA_API_KAY,
        'u': RA_USER
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()

    except Exception as e:
        return f"Erro na API: {e}"
    
    progress_list = []
    platinados_count = 0

    user_games_map = {game['GameID']: game for game in data}

    for game_id, game_name in POKEMON_GAMES.items():
        status = "Não iniciado"
        css_class = "not-started"
        str_game_id = str(game_id)
        
        if str_game_id in user_games_map:
            user_game = user_games_map[str_game_id]
            hardcore = str(user_game.get('HardcoreMode', '0'))
            pct_won = float(user_game.get('PctWon', 0.0))
            if hardcore == '1' and pct_won == 1.0:
                status = "Platinado"
                css_class = "completed"
                platinados_count += 1
            elif pct_won == 1.0:
                status = "Softcore 100%"
                css_class = "softcore"
            else:
                progress = pct_won * 100
                status = f"Jogando ({progress:.1f}%)"
                css_class = "in-progress"
                
        elif game_id in user_games_map:
             pass 
        progress_list.append({
            "name": game_name,
            "status": status,
            "class": css_class
        })
    return render_template('index.html', games=progress_list, count=platinados_count, total=len(POKEMON_GAMES))

if __name__ == '__main__':
    app.run(debug=True)