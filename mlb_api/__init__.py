import requests
from datetime import datetime

class MLB_API:

    def __init__(self, team):
        self.__team = team

        self.__url = "https://statsapi.mlb.com"

    def __get_date(self):
        return datetime.today().strftime("%Y-%m-%d")
    
    def __get_todays_schedule(self):
        url = "%s/api/v1/schedule?date=%s&sportId=1" % (self.__url, self.__get_date())
        response = requests.get(url)
        return response.json()

    def get_game_link(self):
        schedule = self.__get_todays_schedule()
        for game in schedule["dates"][0]["games"]:
            away_team = game["teams"]["away"]["team"]["name"]
            home_team = game["teams"]["home"]["team"]["name"]

            if self.__team in away_team or self.__team in home_team:
                game_state = game["status"]["detailedState"]
                if game_state == "In Progress":
                    return game["link"]
        return None
    
    def get_standings(self, type):
        pass

    def get_live_score(self, link):
        pass

        