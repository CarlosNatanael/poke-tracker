from flask import Flask, render_template
import requests
from games_data import POKEMON_GAMES

app = Flask(__name__)

RA_USER = "CarlosNatanael"
RA_API_KEY = "Oy6GOQ5nOO3l8H3TkvFMw2QABo7Kw1Mn"

@app.route('/')
def index():
    url = "https://retroachievements.org/API/API_GetUserCompletedGames.php"
    params = {
        'z': RA_USER,
        'y': RA_API_KEY,
        'u': RA_USER
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
    except Exception as e:
        return f"Erro na API: {e}"
    
    progress_list = []
    platinados_count = 0
    
    # URL base onde ficam as imagens do RetroAchievements
    RA_IMG_BASE = "https://media.retroachievements.org"
    # Imagem padrão para jogos não iniciados (Pokébola)
    DEFAULT_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Pok%C3%A9_Ball_icon.svg/64px-Pok%C3%A9_Ball_icon.svg.png"

    user_games_map = {str(game['GameID']): game for game in data}

    for game_id, game_name in POKEMON_GAMES.items():
        status = "Não iniciado"
        css_class = "not-started"
        image_url = DEFAULT_IMG # Começa com a Pokébola padrão
        
        str_game_id = str(game_id)
        
        if str_game_id in user_games_map:
            user_game = user_games_map[str_game_id]
            
            # Se a API trouxe uma imagem, usamos ela
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
            "image": image_url  # Passamos a imagem para o HTML
        })

    return render_template('index.html', games=progress_list, count=platinados_count, total=len(POKEMON_GAMES))

if __name__ == '__main__':
    app.run(debug=True)