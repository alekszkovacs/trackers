import sys
import os
import glob
import pandas as pd

from account_summarizer import AccountSummarizer
from excel_handler import ExcelHandler
from configparser import ConfigParser

from __init__ import PROJECT_ROOT


class Summarizer:
    def __init__(self, month: int):
        self.month = month

        config_object = ConfigParser()
        config_object.read(f"{PROJECT_ROOT}/config.ini")
        self._source_folder = config_object["DEFAULT"]["_source_folder"]
        self.database_folder = f'{config_object["DEFAULT"]["database_folder"]}/{config_object["DEFAULT"]["current_year"]}'
        self.current_year = config_object["DEFAULT"]["current_year"]
        self.sum_folder = config_object["DEFAULT"]["sum_folder"]

        self.account_summaries = self._get_account_summaries()

        self._delete_source_files()

    def _delete_source_files(self):
        """delete source files because when we are at this step, it's sure we don't need them anymore"""
        files = glob.glob(f"{self._source_folder}/*")
        for f in files:
            os.remove(f)

        files = glob.glob(f"{self.database_folder}/zzzzzzzzzzres_*")
        for f in files:
            os.remove(f)

    def _get_account_summaries(self):
        return AccountSummarizer(self.month).summarize_all_accounts()

    def calc_monthly_summary(self):
        sum_df = None
        for df in self.account_summaries.values():
            if sum_df is None:
                sum_df = df
            else:
                sum_df = pd.concat([sum_df, df], ignore_index=True)
        df = sum_df.groupby("category")["sum"].sum().reset_index()

        file = f"{self.sum_folder}/{self.current_year}_monthly_summary.xlsx"
        return ExcelHandler.add_df_to_excel(df, self.month, file, return_df=True)

    def write_monthly_summary_to_monthly_consumptions(
        self, monthly_summary: pd.DataFrame
    ):
        """
        write self.month's summary to a single file. every row should start with the month's name and then the summary
        of every category. the header of the columns will be the category names
        """
        file = f"{self.sum_folder}/monthly_consumptions.xlsx"
        try:
            df = pd.read_excel(file, header=0, index_col=0)
        except FileNotFoundError:
            df = pd.DataFrame()

        current_index = f"{self.current_year}-{self.month}"

        monthly_summary = monthly_summary.transpose().rename(
            index={"sum": current_index}
        )
        # grab the first row for the header
        new_header = monthly_summary.iloc[0]
        # take the data less the header row
        monthly_summary = monthly_summary[1:]
        # set the header row as the df header
        monthly_summary.columns = new_header

        print(monthly_summary)
        result = pd.concat([df, monthly_summary], join="outer").fillna(0)
        print(result)

        result.to_excel(file)

    def execute(self):
        monthly_summaries = self.calc_monthly_summary()
        self.write_monthly_summary_to_monthly_consumptions(
            monthly_summaries[self.month]
        )


def main(month: int):
    summarizer = Summarizer(month)
    summarizer.execute()


if __name__ == "__main__":
    main(int(sys.argv[1]))
