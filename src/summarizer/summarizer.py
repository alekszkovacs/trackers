import os
from configparser import ConfigParser

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = f"{CURRENT_DIR}/../.."


class Summarizer:
    def __init__(self):
        config_object = ConfigParser()
        config_object.read(f"{PROJECT_ROOT}/config.ini")
        self._source_folder = config_object["DEFAULT"]["_source_folder"]
        self.database_folder = config_object["DEFAULT"]["database_folder"]
        self.SUM_folder = config_object["DEFAULT"]["SUM_folder"]

    def summarize_per_account(self):
        pass
