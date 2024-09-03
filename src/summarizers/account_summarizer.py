import sys
import pandas as pd

from excel_handler import ExcelHandler
from configparser import ConfigParser

from __init__ import PROJECT_ROOT


class AccountSummarizer:
    def __init__(self, month: int):
        self.month = month

        config_object = ConfigParser()
        config_object.read(f"{PROJECT_ROOT}/config.ini")
        self.current_year = config_object["DEFAULT"]["current_year"]
        self.database_folder = (
            f'{config_object["DEFAULT"]["data_folder"]}/{self.current_year}'
        )
        self.output_folder = config_object["DEFAULT"]["output_folder"]

        self._acc_db_map = self._get_account_database_mapping()

    def _get_account_database_mapping(self) -> dict:
        return {
            "otp": "c_otp.xlsx",
            "unicredit": "c_unicredit.xlsx",
            "revolut": "c_revolut.xlsx",
            "szep": "c_szep.xlsx",
            # "wise": "c_wise.xlsx",
        }

    def _get_account_database(self, account: str) -> pd.DataFrame:
        file = self._acc_db_map.get(account, None)
        if not file:
            raise Exception(f"invalid account! {account}")

        path = f"{PROJECT_ROOT}/{self.database_folder}/{file}"
        db = pd.read_excel(path, f"{self.month}", header=1)
        return pd.DataFrame(db)

    def summarize_per_account(self, account: str) -> pd.DataFrame:
        df = self._get_account_database(account)
        df = df.groupby("category")["sum"].sum().reset_index()

        file = f"{self.output_folder}/_per_account/{self.current_year}/{account}_summary.xlsx"
        ExcelHandler.add_df_to_excel(df, self.month, file)
        return df

    def summarize_all_accounts(self) -> list[pd.DataFrame]:
        summaries = {}
        for acc in self._acc_db_map.keys():
            summaries[acc] = self.summarize_per_account(acc)

        return summaries


def main(month: int, account: str = None):
    summarizer = AccountSummarizer(month)
    if not account:
        summarizer.summarize_all_accounts()
    else:
        summarizer.summarize_per_account(account)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(int(sys.argv[1]), str(sys.argv[2]))
    else:
        main(int(sys.argv[1]))
