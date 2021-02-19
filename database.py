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
    session = cluster.connect()

    # row = session.execute("select release_version from system.local").one()
    # if row:
    #     print(row[0])
    # else:
    #     print("An error occurred.")

    return session
