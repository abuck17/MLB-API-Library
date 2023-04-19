import json
from __init__ import MLB_API

def parse_config_file():
    with open("config.json", "r") as fid:
        return json.load(fid)
    
def main():
    
    config_data = parse_config_file()

    mlb_api = MLB_API(team=config_data["Team"])

    game_info = mlb_api.get_game_info()

    if game_info["Link"]:

        print(mlb_api.get_live_score(link=game_info["Link"]))

    else:

        print(mlb_api.get_standings(type="Divison"))
        print(mlb_api.get_standings(type="Wildcard"))
    
if __name__ == "__main__":
    
    main()







