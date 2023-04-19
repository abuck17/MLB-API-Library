import requests

class MLB_API:

    def __init__(self, team, time_zone, requests=requests):
        self.__team = team
        self.__time_zone = time_zone
        
        self.__requests= requests

        self.__mlb_api_url = "https://statsapi.mlb.com"
        self.__date_time_url = "http://worldtimeapi.org/api"

    def __get_date(self):
        url = "%s/timezone/%s" % (self.__date_time_url, self.__time_zone)
        response = self.__requests.get(url)
        return response.json()["datetime"].split("T")[0]
    
    def __get_todays_schedule(self):
        url = "%s/api/v1/schedule?date=%s&sportId=1" % (self.__mlb_api_url, self.__get_date())
        response = self.__requests.get(url)
        return response.json()

    def get_game_info(self):
        
        game_info = {
            "Link": None
        }
        
        schedule = self.__get_todays_schedule()
        for game in schedule["dates"][0]["games"]:
            away_team = game["teams"]["away"]["team"]["name"]
            home_team = game["teams"]["home"]["team"]["name"]

            if self.__team in away_team or self.__team in home_team:
                game_state = game["status"]["detailedState"]
                if game_state == "In Progress":
                    game_info["Link"] = game["link"]
        return game_info
    
    def get_standings(self, type):
        pass

    def get_live_score(self, link):
        url = "%s%s" % (self.__mlb_api_url, link)
        response = self.__requests.get(url)
        data = response.json()
        
        away_team = data["gameData"]["teams"]["away"]["abbreviation"]
        home_team = data["gameData"]["teams"]["home"]["abbreviation"]
        away_score = data["liveData"]["plays"]["currentPlay"]["result"]["awayScore"]
        home_score = data["liveData"]["plays"]["currentPlay"]["result"]["homeScore"]
        half_inning = data["liveData"]["plays"]["currentPlay"]["about"]["halfInning"]
        inning = data["liveData"]["plays"]["currentPlay"]["about"]["inning"]
        is_complete = data["liveData"]["plays"]["currentPlay"]["about"]["isComplete"]
        first = data["liveData"]["plays"]["currentPlay"]["matchup"].get("postOnFirst") != None
        second = data["liveData"]["plays"]["currentPlay"]["matchup"].get("postOnSeconds") != None
        third = data["liveData"]["plays"]["currentPlay"]["matchup"].get("postOnThird") != None
        outs = data["liveData"]["plays"]["currentPlay"]["count"]["outs"]
        balls = data["liveData"]["plays"]["currentPlay"]["count"]["balls"]
        strikes = data["liveData"]["plays"]["currentPlay"]["count"]["strikes"]
        
        payload = {
            "Away Team": away_team,
            "Home Team": home_team,
            "Away Score": away_score,
            "Home Score": home_score,
            "Half Inning": half_inning,
            "Inning": inning,
            "Is Inning Complete": is_complete,
            "Man On First": first,
            "Man On Seconds": second,
            "Man on Third": third,
            "Outs": outs,
            "Balls": balls,
            "Strikes": strikes,
        }
        
        print(payload)
        

        