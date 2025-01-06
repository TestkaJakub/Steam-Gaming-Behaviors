import urllib3
import json

def get_games(api_key, steam_id, get_all = False):

    if get_all:
        request = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&format=json".format(api_key, steam_id)
    else:
        request = "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={}&steamid={}&format=json".format(api_key, steam_id)
    response = urllib3.request("GET", request).data
    decoded_response = response.decode('utf-8')
    response_dict = json.loads(decoded_response)
    recently_played = response_dict.get('response', {}).get('games', [])

    game_objects  = []

    for game in recently_played:
        g = Game(game['appid'], game['playtime_forever'])
        if not get_all:
            g.name = game['name']
            g.icon = game['img_icon_url']
            g.recently_played = game['playtime_2weeks']
        game_objects.append(g)

    return game_objects

class Game:
    def __init__(self, appid, playtime_minutes, recently_played = None, icon = None, name = None):
        self.name = name
        self.appid = appid
        self.playtime_minutes = playtime_minutes
        self.recently_played = recently_played
        self.icon = icon