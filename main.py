import json
from __init__ import MLB_API

def display_sep():
    print("-" * 80)

def display(data):
    display_sep()
    for item in data:
        print(item)
    display_sep()

def parse_config_file():
    with open("config.json", "r") as fid:
        return json.load(fid)
    
def main():
    
    config_data = parse_config_file()

    mlb_api = MLB_API(team=config_data["Team"], time_zone=config_data["Time Zone"])
    
    while True:

        games_info = mlb_api.get_info_on_todays_games()
        
        if games_info:
            
            in_progess = [game_info["State"] == "In Progress" for game_info in games_info]
            
            if any(in_progess):
                
                display(mlb_api.get_live_score(link=games_info[in_progess.index(True)]))
                continue
            
        display(mlb_api.get_standings(filter="Division"))
    
if __name__ == "__main__":
    main()
