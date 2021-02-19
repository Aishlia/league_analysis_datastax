import requests
from bs4 import BeautifulSoup
import re
import html
from database import get_session, init_db
import uuid
import random

session = get_session()
init_db(session)

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
        self.win = False

    def __str__(self):
        output = f"{self.champion} {self.summoner}"
        return output

    def to_dict(self) -> dict:
        player = {
            "champion": self.champion,
            "summoner": self.summoner.to_dict(),
        }
        return player

    def winloss(self, win_bool):
        self.win = win_bool

class Match:
    def __init__(self, match_id):
        self.teams = []
        self.match_id = match_id

    def add_team(self, team):
        self.teams.append(team)

    def print_team(self, team_num):
        for i in self.teams[team_num]:
            print(i)

    def winloss(self, summoner_id: str, win: bool):
        team_num = 1
        for player in self.teams[0]:
            if player.summoner.summoner_id == summoner_id:
                team_num = 0
                break

        for player in self.teams[team_num]:
            player.win = win
            print(player.win)

        other_team = team_num ^ 1
        for player in self.teams[other_team]:
            player.win = not win
            print(player.win)

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

def get_teams_data(page_info):
    teams = [a.get_text() for a in page_info.find_all("div", {"class": "Team"})]
    return teams

def get_page_info(summoner_name):
    summoner_id = summ_id(summoner_name)
    url = 'https://na.op.gg/summoner/matches/ajax/averageAndList/startInfo=0&summonerId=' + str(summoner_id) + '&type=soloranked'

    data = requests.get(url).json()
    soup = BeautifulSoup(data['html'], 'html.parser').decode('unicode_escape')
    page_info = BeautifulSoup(soup, 'html.parser')
    return page_info

def get_match_ids(page_info):
    game_area = page_info.find("div", {"class": "GameItemList"})
    games = game_area.find_all("div", {"class": "GameItem"})
    match_ids = [a['data-game-id'] for a in games]
    return match_ids

def get_win_loss(page_info):
    game_area = page_info.find("div", {"class": "GameItemList"})
    games = game_area.find_all("div", {"class": "GameItem"})
    winlosses = [a['data-game-result'] for a in games]
    win = lambda x : True if (x == 'win') else False
    winlosses = list(map(win, winlosses))
    return winlosses

def persist_matches(matches: Match):
    for match in matches:
        match_id = match.match_id
        for team in match.teams:
            for player in team:
                player_data = dict(
                    match_id = match_id,
                    summoner_id = player.summoner.summoner_id,
                    name = player.summoner.name,
                    rank = str(player.summoner.rank),
                    champion = player.champion,
                    win = str(player.win),
                    url = player.summoner.url,
                )
                print(player_data)
                session.execute("""
                    INSERT INTO match (
                        match_id,
                        summoner_id,
                        name,
                        rank,
                        champion,
                        win,
                        url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    IF NOT EXISTS
                """, player_data.values())

def two_matches(summoner_name: str):
    """
    Pulls game info for a player's most recent two ranked matches.

    Return: List of most recent 2 matches
    """
    page_info = get_page_info(summoner_name)
    teams = get_teams_data(page_info)
    match_ids = get_match_ids(page_info)
    matches = []

    summoner_id = summ_id(summoner_name)
    win_losses = get_win_loss(page_info)
    print(win_losses)

    itr = 0
    for m in range(2):  # Pull 2 matches
        match_id = match_ids[m]
        match = Match(match_id)
        for t in range(2):  # Pull both teams for each math
            team = parse_team(teams[itr])
            match.add_team(team)
            itr += 1

        match.winloss(summoner_id, win_losses[m])
        matches.append(match)

    persist_matches(matches)
    return matches

def get_matches(iters: int, seed_summoner: str):
    seed = two_matches(seed_summoner)
    for _ in range(iters):
        next_summoner = seed[1].teams[1][random.randint(0, 4)].summoner.name  # Pull a random player from the game as new seed
        print(next_summoner)
        seed = two_matches(next_summoner)

if __name__ == "__main__":
    iters = int(input("Iterations: "))
    seed_summoner = input("Seed summoner: ")
    # iters = 1
    # seed_summoner = "Rito Torchic"
    get_matches(iters, seed_summoner)
