import json
from mlb_api import MLB_API

with open("config.json", "r") as fid:
    config_data = json.load(fid)

mlb_api = MLB_API(team=config_data["Team"])

link = mlb_api.get_game_link()

if link:

    print(mlb_api.get_live_score(link=link))

else:

    print(mlb_api.get_standings(type="Divison"))
    print(mlb_api.get_standings(type="Wildcard"))






