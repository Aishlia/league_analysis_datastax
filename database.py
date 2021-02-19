from dotenv import load_dotenv
load_dotenv()
import os

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


CASS_USER = os.environ["CASS_USER"]
CASS_PASS = os.environ["CASS_PASS"]
DATASTAX_BUNDLE_PATH = 'datastax_bundle.zip'

CLOUD_CONFIG = {
    'secure_connect_bundle': DATASTAX_BUNDLE_PATH
}

def get_session():
    auth_provider = PlainTextAuthProvider(CASS_USER, CASS_PASS)
    cluster = Cluster(cloud=CLOUD_CONFIG, auth_provider=auth_provider)
    session = cluster.connect("match")

    # row = session.execute("select release_version from system.local").one()
    # if row:
    #     print(row[0])
    # else:
    #     print("An error occurred.")
    return session

def init_db(session):
    # session.execute(("CREATE KEYSPACE IF NOT EXISTS matches "
    #                 "WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1' }"))
    session.execute("USE match")
    session.execute("CREATE TABLE IF NOT EXISTS match (match_id text, summoner_id text, name text, rank text, champion text, win text, url text, PRIMARY KEY (match_id, summoner_id))")
