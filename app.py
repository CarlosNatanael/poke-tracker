from flask import Flask, render_template
import requests
from games_data import POKEMON_GAMES

app = Flask(__name__)

RA_USER = "CarlosNatanael"
RA_API_KEY = "Oy6GOQ5nOO3l8H3TkvFMw2QABo7Kw1Mn"
RA_BASE_URL = "https://retroachievements.org/API"
RA_IMG_BASE = "https://media.retroachievements.org"

@app.route('/')
def index():
    params = {'z': RA_USER, 'y': RA_API_KEY, 'u': RA_USER}
    user_data = {}
    try:
        resp_user = requests.get(f"{RA_BASE_URL}/API_GetUserSummary.php", params=params)
        user_data = resp_user.json()
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")

    progress_list = []
    platinados_count = 0
    
    try:
        resp_games = requests.get(f"{RA_BASE_URL}/API_GetUserCompletedGames.php", params=params)
        data_games = resp_games.json()
    except Exception as e:
        return f"Erro na API de jogos: {e}"

    user_games_map = {str(game['GameID']): game for game in data_games}
    DEFAULT_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Pok%C3%A9_Ball_icon.svg/64px-Pok%C3%A9_Ball_icon.svg.png"

    for game_id, game_name in POKEMON_GAMES.items():
        status = "Não iniciado"
        css_class = "not-started"
        image_url = DEFAULT_IMG
        
        str_game_id = str(game_id)
        
        if str_game_id in user_games_map:
            user_game = user_games_map[str_game_id]
            
            if user_game.get('ImageIcon'):
                image_url = RA_IMG_BASE + user_game.get('ImageIcon')

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
        
        progress_list.append({
            "name": game_name,
            "status": status,
            "class": css_class,
            "image": image_url
        })
    return render_template('index.html', 
                           games=progress_list, 
                           count=platinados_count, 
                           total=len(POKEMON_GAMES),
                           user=user_data,
                           img_base=RA_IMG_BASE)

if __name__ == '__main__':
    app.run(debug=True)