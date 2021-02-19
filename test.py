from parsing import two_matches
import csv
from database import get_session, init_db
import uuid

def test():
    target = 'Rito Torchic'
    matches = two_matches(target)

    with open("test.csv", "w") as f:
        fieldnames = ["record_id", "match_id", "summoner_id", "name", "rank", "champion", "url"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for match in matches:
            match_id = match.match_id
            for team in match.teams:
                for player in team:
                    record_id = str(uuid.uuid4())
                    player_data = dict(
                        record_id = record_id,
                        match_id = match_id,
                        summoner_id = player.summoner.summoner_id,
                        name = player.summoner.name,
                        rank = player.summoner.rank,
                        champion = player.champion,
                        url = player.summoner.url,
                    )
                    writer.writerow(player_data)

def persist_csv_to_db(filename):
    session = get_session()
    init_db(session)
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            session.execute("""
                INSERT INTO match (
                    id,
                    match_id,
                    summoner_id,
                    name,
                    rank,
                    champion,
                    url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, row.values())

test()
# persist_csv_to_db("test.csv")
