import time

try:
    import adafruit_requests as requests
except ImportError:
    import requests
    
game_info_fields = [
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

standings_fields = [
    "records",
    "teamRecords",
    "team",
    "name",
    "link",
    "wins",
    "losses",
    "gamesBack",
    "wildCardGamesBack",
]
    
class MLB_API:

    def __init__(self, team, time_zone, request_lib=requests):
        self.__team = team
        self.__time_zone = time_zone
        
        self.__requests = request_lib

        self.__mlb_api_url = "https://statsapi.mlb.com"
        self.__date_time_url = "http://worldtimeapi.org/api"

    def __get_date(self):
        time.sleep(1.0)
        url = "%s/timezone/%s" % (self.__date_time_url, self.__time_zone)
        response = self.__requests.get(url)
        data = response.json()["datetime"].split("T")[0]
        response.close()
        return data
    
    def __get_todays_schedule(self):
        time.sleep(1.0)
        url = "%s/api/v1/schedule?date=%s&sportId=1" % (self.__mlb_api_url, self.__get_date())
        response = self.__requests.get(url)
        data = response.json()
        response.close()
        return data
    
    def __get_game_info(self, link):
        time.sleep(1.0)
        url = "%s%s?fields=%s" % (self.__mlb_api_url, link, ",".join(game_info_fields))
        response = self.__requests.get(url)
        data = response.json()
        response.close()
        return data
    
    def __get_standings(self):
        time.sleep(1.0)
        url = "%s/api/v1/standings?standingsTypes=regularSeason&leagueId=103,104&fields=%s" % (
            self.__mlb_api_url, ",".join(standings_fields))
        response = self.__requests.get(url)
        data = response.json()
        response.close()
        return data
    
    def __get_abbrivation(self, link):
        time.sleep(1.0)
        url = "%s%s" % (self.__mlb_api_url, link)
        response = self.__requests.get(url)
        data = response.json()["teams"][0]["abbreviation"]
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
    
    def get_standings(self, filter):
        
        standings = self.__get_standings()
        
        payload = []
        
        if filter == "Divison":
            for record in standings["records"]:
                if any([self.__team in team_record["team"]['name'] for team_record in record["teamRecords"]]):
                    for team_record in record["teamRecords"]:
                        payload.append({
                            "Team": self.__get_abbrivation(team_record["team"]["link"]),
                            "Wins": team_record["wins"],
                            "Losses": team_record["losses"],
                            "Games Back": team_record["gamesBack"],
                        })
            return payload             
        else:
            print("Cannot determine stadning for type '%s'" % filter)
        
    def get_live_score(self, link):
        
        game_info = self.__get_game_info(link)

        payload = {
            "State": game_info["gameData"]["status"]["detailedState"],
            "Date Time": game_info["gameData"]["datetime"]["dateTime"],
            "Away Team": game_info["gameData"]["teams"]["away"]["abbreviation"],
            "Home Team": game_info["gameData"]["teams"]["home"]["abbreviation"],
            "Away Score": game_info["liveData"]["plays"]["currentPlay"]["result"]["awayScore"],
            "Home Score": game_info["liveData"]["plays"]["currentPlay"]["result"]["homeScore"],
            "Half Inning": game_info["liveData"]["plays"]["currentPlay"]["about"]["halfInning"],
            "Inning": game_info["liveData"]["plays"]["currentPlay"]["about"]["inning"],
            "Is Inning Complete": game_info["liveData"]["plays"]["currentPlay"]["about"]["isComplete"],
            "Man On First": game_info["liveData"]["plays"]["currentPlay"]["matchup"].get("postOnFirst") != None,
            "Man On Second": game_info["liveData"]["plays"]["currentPlay"]["matchup"].get("postOnSecond") != None,
            "Man on Third": game_info["liveData"]["plays"]["currentPlay"]["matchup"].get("postOnThird") != None,
            "Outs": game_info["liveData"]["plays"]["currentPlay"]["count"]["outs"],
            "Balls": game_info["liveData"]["plays"]["currentPlay"]["count"]["balls"],
            "Strikes": game_info["liveData"]["plays"]["currentPlay"]["count"]["strikes"],
        }
        
        return payload
        

        