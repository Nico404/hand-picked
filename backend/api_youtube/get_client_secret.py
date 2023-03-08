import json
import os

parentdir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def get_client_secret():
    # Returns the path to the client secret file.
    return os.path.join(parentdir, "secret/client_secret.json")
