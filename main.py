import json
from __init__ import MLB_API

def display(data):
    print(data)

def parse_config_file():
    with open("config.json", "r") as fid:
        return json.load(fid)
    
def main():
    
    config_data = parse_config_file()

    mlb_api = MLB_API(team=config_data["Team"], time_zone=config_data["Time Zone"])
    
    while True:

        games_info = mlb_api.get_info_on_todays_games()
                
        for game_info in games_info:
              
            if game_info["State"] == "In Progress":
                                
                display(mlb_api.get_live_score(link=game_info["Link"]))

            else:

                display(mlb_api.get_standings(filter="Divison"))
    
if __name__ == "__main__":
    main()
