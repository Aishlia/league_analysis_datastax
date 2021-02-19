import requests
from bs4 import BeautifulSoup
import re
import html
from database import get_session
import uuid

class Summoner:
    def __init__(self, summoner_name: str):
        self.name = summoner_name

        self.summoner_id = None
        self.url = None
        self.rank = None
        self.id_url_rank()

    def __str__(self):
        output = f"{self.name} {self.rank} {self.summoner_id}"
        return output

    def id_url_rank(self):
        url = 'https://na.op.gg/summoner/userName=' + self.name.replace(' ','+')
        data = requests.get(url).text
        soup = BeautifulSoup(data, 'html.parser')
        mydiv = soup.find("div", {"class": "MostChampionContent"})
        child_div = mydiv.find("div", {"class": "MostChampionContent"})
        summ_id = child_div['data-summoner-id']

        self.url = url
        self.summoner_id = summ_id

        rank = soup.find("div", {"class": "TierRank"}).string

        self.rank = rank

    def to_dict(self) -> dict:
        summoner = {
            "name": self.name,
            "summoner_id": self.summoner_id,
            "url": self.url,
            "rank": self.rank,
        }
        return summoner

class Player:
    def __init__(self, champion: str, summoner: Summoner):
        self.champion = champion
        self.summoner = summoner

    def __str__(self):
        output = f"{self.champion} {self.summoner}"
        return output

    def to_dict(self) -> dict:
        player = {
            "champion": self.champion,
            "summoner": self.summoner.to_dict(),
        }
        return player

class Match:
    def __init__(self):
        self.teams = []
        self.match_id = str(uuid.uuid4())

    def add_team(self, team):
        self.teams.append(team)

    def print_team(self, team_num):
        for i in self.teams[team_num]:
            print(i)

    def to_dict(self) -> dict:
        match = {
            "match_id": self.match_id,
            "teams": [],
        }
        for team in teams:
            match["teams"].append(team.to_dict())

        return match

def summ_id(summ_name):
    url = 'https://na.op.gg/summoner/userName=' + summ_name.replace(' ','+')
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    mydivs = soup.find("div", {"class": "MostChampionContent"})
    mydivs = mydivs.find("div", {"class": "MostChampionContent"})
    summ_id = mydivs['data-summoner-id']
    return summ_id

def parse_team(team):
    team_list = []
    team = team.split('\n')
    for i in range(len(team)):
        team[i] = team[i].strip()

    team = list(filter(None, team))  # Get rid of empty indexes

    for index in range(0,len(team), 3):  # The champ name is always listed twice
        champion = str(team[index])
        summoner_name = team[index+2]
        summoner = Summoner(summoner_name)

        new_entry = Player(champion, summoner)

        team_list.append(new_entry)
    return team_list

def get_team_data(summoner_name):
    summoner_id = summ_id(summoner_name)
    url = 'https://na.op.gg/summoner/matches/ajax/averageAndList/startInfo=0&summonerId=' + str(summoner_id) + '&type=soloranked'

    data = requests.get(url).json()
    soup = BeautifulSoup(data['html'], 'html.parser').decode('unicode_escape')
    soup = BeautifulSoup(soup, 'html.parser')
    win_loss = soup.findAll("div", {"class": "GameResult"})
    teams = [a.get_text() for a in soup.find_all("div", {"class": "Team"})]
    return teams

def persist_match(match: Match):
    ...

def two_matches(summoner_name: str):
    """
    Pulls game info for a player's most recent two ranked matches.

    Return: List of most recent 2 matches
    """
    teams = get_team_data(summoner_name)
    matches = []

    itr = 0
    for m in range(2):  # Pull 2 matches
        match = Match()
        for t in range(2):  # Pull both teams for each math
            team = parse_team(teams[itr])
            match.add_team(team)

            itr += 1

        matches.append(match)

    return matches
