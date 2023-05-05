import time

try:
    import adafruit_requests as requests
except ImportError:
    import requests
    
live_game_info_fields = [
    "gameData",
    "datetime",
    "dateTime",
    "status",
    "detailedState",
    "teams",
    "abbreviation",
    "liveData",
    "plays",
    "currentPlay",
    "result",
    "awayScore",
    "homeScore",
    "about",
    "halfInning",
    "inning",
    "pitcher",
    "batter",
    "link",
    "isComplete",
    "matchup",
    "postOnFirst",
    "postOnSecond",
    "postOnThird",
    "count",
    "outs",
    "balls",
    "strikes",
]

scheduled_game_info_fields = [
    "gameData",
    "datetime",
    "dateTime",
    "probablePitchers",
    "away",
    "home",
    "link",
    "teams",
    "abbreviation",
]

standings_fields = [
    "records",
    "teamRecords",
    "team",
    "name",
    "link",
    "wins",
    "losses",
    "gamesBack",
]

team_fields = [
    "teams",
    "abbreviation",
]

people_fields = [
    "people",
    "lastName",
]
    
class MLB_API:

    def __init__(self, team, time_zone, request_lib=requests):
        self.__team = team
        self.__time_zone = time_zone
        
        self.__requests = request_lib

        self.__mlb_api_url = "https://statsapi.mlb.com"
        self.__date_time_url = "http://worldtimeapi.org/api"
        
        self.__date_time = None
        self.update_date_time()
        
    def update_date_time(self):
        time.sleep(1.0)
        url = "%s/timezone/%s" % (self.__date_time_url, self.__time_zone)
        response = self.__requests.get(url)
        self.__date_time = response.json()["datetime"]
        response.close()

    def get_date(self):
        return self.__date_time.split("T")[0]
    
    def get_time(self):
        return self.__date_time.split("T")[1][:-6]
    
    def get_timezone_offset(self):
        return int(self.__date_time[-6:-3])
    
    def __get_todays_schedule(self):
        self.update_date_time()
        time.sleep(1.0)
        url = "%s/api/v1/schedule?date=%s&sportId=1" % (self.__mlb_api_url, self.get_date())
        response = self.__requests.get(url)
        data = response.json()
        response.close()
        return data
    
    def __get_live_game_info(self, link):
        time.sleep(1.0)
        url = "%s%s?fields=%s" % (self.__mlb_api_url, link, ",".join(live_game_info_fields))
        response = self.__requests.get(url)
        data = response.json()
        response.close()
        return data
    
    def __get_scheduled_game_info(self, link):
        time.sleep(1.0)
        url = "%s%s?fields=%s" % (self.__mlb_api_url, link, ",".join(scheduled_game_info_fields))
        response = self.__requests.get(url)
        data = response.json()
        response.close()
        return data
    
    def __get_standings(self, league):
        
        if league in ["AL", "American League"]:
            league_id = "103"
        elif league in ["NL", "National League"]:
            league_id = "104"
        elif league == "All":
            league_id = "103,104"
        else:
            print("Cannt determine league of type '%s'" % league)
        
        time.sleep(1.0)
        url = "%s/api/v1/standings?standingsTypes=regularSeason&leagueId=%s&fields=%s" % (
            self.__mlb_api_url, league_id, ",".join(standings_fields))
        print(url)
        response = self.__requests.get(url)
        data = response.json()
        response.close()
        return data
    
    def __get_abbrivation(self, link):
        time.sleep(1.0)
        url = "%s%s?fields=%s" % (self.__mlb_api_url, link, ",".join(team_fields))
        response = self.__requests.get(url)
        data = response.json()["teams"][0]["abbreviation"]
        response.close()
        return data
    
    def __get_last_name(self, link):
        time.sleep(1.0)
        url = "%s%s?fields=%s" % (self.__mlb_api_url, link, ",".join(people_fields))
        response = self.__requests.get(url)
        data = response.json()["people"][0]["lastName"]
        response.close()
        return data

    def get_info_on_todays_games(self):
        
        payload = []
        
        schedule = self.__get_todays_schedule()
        for game in schedule["dates"][0]["games"]:
            away_team = game["teams"]["away"]["team"]["name"]
            home_team = game["teams"]["home"]["team"]["name"]

            if self.__team in away_team or self.__team in home_team:

                payload.append({
                    "State": game["status"]["detailedState"],
                    "Link": game["link"],
                })

        return payload
    
    def get_standings(self):
        
        # TODO: Need to do this better. Running into memory issues.
        
        for league in ["AL", "NL"]:
            
            standings = self.__get_standings(league)
            
            payload = {
                "Type": "Division Standings",
                "Data": []
                }
            
            for record in standings["records"]:
                if any([self.__team in team_record["team"]['name'] for team_record in record["teamRecords"]]):
                    for team_record in record["teamRecords"]:
                        payload["Data"].append({
                            "Team": self.__get_abbrivation(team_record["team"]["link"]),
                            "Wins": team_record["wins"],
                            "Losses": team_record["losses"],
                            "Games Back": team_record["gamesBack"],
                        })
                        
        return payload             
        
    def get_live_score(self, link):
        
        game_info = self.__get_live_game_info(link)

        payload = {
            "Type": "Live Score",
            "State": game_info["gameData"]["status"]["detailedState"],
            "Date Time": game_info["gameData"]["datetime"]["dateTime"],
            "Away Team": game_info["gameData"]["teams"]["away"]["abbreviation"],
            "Home Team": game_info["gameData"]["teams"]["home"]["abbreviation"],
            "Away Score": game_info["liveData"]["plays"]["currentPlay"]["result"]["awayScore"],
            "Home Score": game_info["liveData"]["plays"]["currentPlay"]["result"]["homeScore"],
            "Half Inning": game_info["liveData"]["plays"]["currentPlay"]["about"]["halfInning"],
            "Inning": game_info["liveData"]["plays"]["currentPlay"]["about"]["inning"],
            "Is Inning Complete": game_info["liveData"]["plays"]["currentPlay"]["about"]["isComplete"],
            "Pitcher": self.__get_last_name(game_info["liveData"]["plays"]["currentPlay"]["matchup"]["pitcher"]["link"]),
            "Batter": self.__get_last_name(game_info["liveData"]["plays"]["currentPlay"]["matchup"]["batter"]["link"]),
            "Man On First": game_info["liveData"]["plays"]["currentPlay"]["matchup"].get("postOnFirst") != None,
            "Man On Second": game_info["liveData"]["plays"]["currentPlay"]["matchup"].get("postOnSecond") != None,
            "Man On Third": game_info["liveData"]["plays"]["currentPlay"]["matchup"].get("postOnThird") != None,
            "Outs": game_info["liveData"]["plays"]["currentPlay"]["count"]["outs"],
            "Balls": game_info["liveData"]["plays"]["currentPlay"]["count"]["balls"],
            "Strikes": game_info["liveData"]["plays"]["currentPlay"]["count"]["strikes"],
        }
        
        return payload
    
    def get_scheduled_game_info(self, link):
        
        game_info = self.__get_scheduled_game_info(link)

        payload = {
            "Type": "Scheduled",
            "Date Time": game_info["gameData"]["datetime"]["dateTime"],
            "Away Team": game_info["gameData"]["teams"]["away"]["abbreviation"],
            "Home Team": game_info["gameData"]["teams"]["home"]["abbreviation"],
            "Away Score": 0,
            "Home Score": 0,
            "Away Pitcher": self.__get_last_name(game_info["gameData"]["probablePitchers"]["away"]["link"]),
            "Home Pitcher": self.__get_last_name(game_info["gameData"]["probablePitchers"]["home"]["link"]),
        }
        
        return payload