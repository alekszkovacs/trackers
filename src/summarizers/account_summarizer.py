import sys
import pandas as pd

from config import Config
from excel_handler import ExcelHandler

from __init__ import PROJECT_ROOT


class InvalidCharacterException(Exception):
    pass


class AccountSummarizer:
    def __init__(self, month: int):
        self.config = Config.get_config()
        self.month = month
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

        path = f"{PROJECT_ROOT}/{self.config.database_folder}/{file}"
        db = pd.read_excel(path, f"{self.month}", header=1)
        return pd.DataFrame(db)

    def summarize_per_account(self, account: str) -> dict[str, pd.DataFrame]:
        df = self._get_account_database(account)

        sum_df = df.groupby("category")["sum"].sum().reset_index()
        occasion_df = df.groupby("occasion group")["sum"].sum().reset_index()

        # if any of the groups' name in occasion_df contains special characters, throw an exception
        for group in occasion_df["occasion group"]:
            if not all(char.isalnum() or char in ["_", "-"] for char in group):
                raise InvalidCharacterException(
                    f'invalid character in occasion group name: "{group}"\nonly alphanumeric characters, _ and - are allowed!'
                )

        num_empty_cols = 3
        empty_cols = pd.DataFrame(
            "",
            index=sum_df.index,
            columns=["" for _ in range(num_empty_cols)],
        )

        result_df = pd.concat([sum_df, empty_cols, occasion_df], axis=1)
        result_dict = {"sum": sum_df, "occasion": occasion_df}

        file = f"{self.config.sum_folder}/_per_account/{self.config.current_year}/{account}_summary.xlsx"
        ExcelHandler.add_df_to_excel(result_df, self.month, file)

        return result_dict

    def summarize_all_accounts(self) -> dict[str, dict[str, pd.DataFrame]]:
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
