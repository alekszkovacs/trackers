from configparser import ConfigParser

from __init__ import PROJECT_ROOT


class Config:
    @staticmethod
    def get_config():
        config_object = ConfigParser()
        config_object.read(f"{PROJECT_ROOT}/config.ini")
        DEFAULT = config_object["DEFAULT"]

        config = {
            "feeder_folder": DEFAULT["feeder_folder"],
            "database_folder": f'{DEFAULT["data_folder"]}/{DEFAULT["current_year"]}',
            "current_year": DEFAULT["current_year"],
            "sum_folder": DEFAULT["sum_folder"],
            "results_folder": DEFAULT["results_folder"],
            "occasions_folder": DEFAULT["occasions_folder"],
        }

        config = type("config", (object,), config)
        return config
