import sys
import os
import glob
import pandas as pd

from config import Config
from summary_worker import SummaryWorker
from occasion_worker import OccasionWorker
from account_summarizer import AccountSummarizer


pd.set_option("future.no_silent_downcasting", True)


class Summarizer:
    def __init__(self, month: int):
        self.config = Config.get_config()
        self.month = month
        self.accounts = self._summarize_accounts()

        self.summary_worker = SummaryWorker(self.month)
        self.occasion_worker = OccasionWorker(self.month)

        self._delete_source_files()

    def _delete_source_files(self):
        """delete source files because when we are at this step, it's sure we don't need them anymore"""
        files = glob.glob(f"{self.config.feeder_folder}/*")
        for f in files:
            os.remove(f)

        files = glob.glob(f"{self.config.database_folder}/zzzzzzzzzzres_*")
        for f in files:
            os.remove(f)

    def _summarize_accounts(self) -> dict[str, dict[str, pd.DataFrame]]:
        return AccountSummarizer(self.month).summarize_all_accounts()

    def execute(self):
        sum_dfs = []
        occasion_dfs = []
        for _dict in self.accounts.values():
            sum_dfs.append(_dict["sum"])
            occasion_dfs.append(_dict["occasion"])

        self.summary_worker.execute(sum_dfs)
        self.occasion_worker.execute(occasion_dfs)


def main(month: int):
    summarizer = Summarizer(month)
    summarizer.execute()


if __name__ == "__main__":
    main(int(sys.argv[1]))
