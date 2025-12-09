from flask import Flask, render_template
import requests
from datetime import datetime
import pytz
from games_data import POKEMON_GAMES

try:
    from config import RA_USER, RA_API_KEY
except ImportError:
    RA_USER = None
    RA_API_KEY = None

app = Flask(__name__)

RA_BASE_URL = "https://retroachievements.org/API"
RA_IMG_BASE = "https://media.retroachievements.org"

def format_ra_date(date_str):
    if not date_str: return None
    try:
        utc_dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        br_tz = pytz.timezone('America/Sao_Paulo')
        br_dt = utc_dt.astimezone(br_tz)
        return br_dt.strftime('%d/%m/%Y')
    except:
        return date_str

@app.route('/')
def index():
    if not RA_USER or not RA_API_KEY:
        return "Erro: Configure o config.py"
    
    params = {'z': RA_USER, 'y': RA_API_KEY, 'u': RA_USER}
    user_data = {}
    try:
        user_data = requests.get(f"{RA_BASE_URL}/API_GetUserSummary.php", params=params).json()
    except: pass
    try:
        data_games = requests.get(f"{RA_BASE_URL}/API_GetUserCompletedGames.php", params=params).json()
        user_games_map = {str(game['GameID']): game for game in data_games}
    except:
        user_games_map = {}

    DEFAULT_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Pok%C3%A9_Ball_icon.svg/64px-Pok%C3%A9_Ball_icon.svg.png"

    progress_list = []
    platinados_count = 0

    for game_id, game_info in POKEMON_GAMES.items():
        game_title = game_info['title']
        
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
            "id": game_id,
            "name": game_title,
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

@app.route('/game/<int:game_id>')
def game_details(game_id):
    manual_data = POKEMON_GAMES.get(game_id, {})
    manual_date = manual_data.get('date')
    manual_hours = manual_data.get('hours')
    
    params = {'z': RA_USER, 'y': RA_API_KEY, 'u': RA_USER, 'g': game_id}
    game_api = {}
    try:
        game_api = requests.get(f"{RA_BASE_URL}/API_GetGameInfoAndUserProgress.php", params=params).json()
    except: pass

    completion_date = "Em progresso"
    if manual_date: 
        completion_date = manual_date
    elif game_api.get('UserCompletionHardcore') == '100.00%':
        completion_date = format_ra_date(game_api.get('HighestAwardDate'))
        
    hours_played = manual_hours if manual_hours else "---"

    earned = game_api.get('NumAwardedToUserHardcore', 0)
    total = game_api.get('NumAchievements', 0)
    
    game_data = {
        "title": game_api.get('Title', manual_data.get('title')),
        "console": game_api.get('ConsoleName', 'Console'),
        "image": RA_IMG_BASE + game_api.get('ImageIcon', ''),
        "box_art": RA_IMG_BASE + game_api.get('ImageBoxArt', ''),
        "completion": game_api.get('UserCompletionHardcore', '0%'),
        "achievements_count": f"{earned} / {total}",
        "completion_date": completion_date,
        "hours_played": hours_played
    }
    return render_template('game_details.html', game=game_data)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

if __name__ == '__main__':
    app.run(debug=True)