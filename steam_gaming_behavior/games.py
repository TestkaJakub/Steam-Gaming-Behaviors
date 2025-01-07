import urllib3
import json

def get_games(steam_api_key, steam_id, get_all_owned_games = False):

    # request for recently played games
    request = "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={}&steamid={}&format=json".format(steam_api_key, steam_id)
    
    # request for all owned games
    if get_all_owned_games:
        request = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&format=json".format(steam_api_key, steam_id)
        
    response = urllib3.request("GET", request).data
    decoded_response = response.decode('utf-8')
    response_json = json.loads(decoded_response)
    games = response_json.get('response', []).get('games', [])

    game_objects  = []

    for game in games:
        g = Game(game['appid'], game['playtime_forever'])
        if not get_all_owned_games:
            g.name = game['name']
            g.icon_hash = game['img_icon_url']
            g.recently_played = game['playtime_2weeks']
        game_objects.append(g)

    return game_objects

class Game:
    def __init__(self, appid, playtime_minutes, recently_played = None, icon_hash = None, name = None):
        self.name = name # only accessible via recently played endpoint
        self.appid = appid
        self.playtime_minutes = playtime_minutes
        self.recently_played = recently_played # only accessible via recently played endpoint
        self.icon_hash = icon_hash # only accessible via recently played endpoint