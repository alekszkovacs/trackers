import os
import sys
import pandas as pd
from configparser import ConfigParser

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = f"{CURRENT_DIR}/../.."


class Summarizer:
    def __init__(self):
        config_object = ConfigParser()
        config_object.read(f"{PROJECT_ROOT}/config.ini")
        self._source_folder = config_object["DEFAULT"]["_source_folder"]
        self.database_folder = config_object["DEFAULT"]["database_folder"]
        self.sum_folder = config_object["DEFAULT"]["sum_folder"]
        self._acc_db_map = self._get_account_database_mapping()

    def _get_account_database_mapping(self) -> dict:
        return {
            "otp": "c_otp.xlsx",
            "revolut": "c_revolut.xlsx",
            "szep": "c_szep.xlsx",
            "wise": "c_wise.xlsx",
        }

    def _get_account_database(self, month: int, account: str) -> pd.DataFrame:
        file = self._acc_db_map.get(account, None)
        if not file:
            raise Exception(f"invalid account! {account}")

        path = f"{PROJECT_ROOT}/{self.database_folder}/{file}"
        db = pd.read_excel(path, f"{month}", header=1)
        return pd.DataFrame(db)

    def summarize_per_account(self, month: int, account: str):
        df = self._get_account_database(month, account)
        sum_per_category = df.groupby("category")["sum"].sum()
        sum_per_category.to_excel(
            f"{self.sum_folder}/_per_account/{account}_summary.xlsx",
            sheet_name=f"{month}",
        )
        return sum_per_category

    def summarize(self, month: int):
        summaries = {}
        for acc in self._acc_db_map.keys():
            summaries[acc] = self.summarize_per_account(month, acc)

    def _monthly_summary(self, month: int):
        pass


def main(month: int, account: str = None):
    summarizer = Summarizer()
    if not account:
        summarizer.summarize(month)
    else:
        summarizer.summarize_per_account(month, account)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(int(sys.argv[1]), str(sys.argv[2]))
    else:
        main(int(sys.argv[1]))
