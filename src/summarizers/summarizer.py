import sys
import os
import glob
import shutil
import pandas as pd

from account_summarizer import AccountSummarizer
from excel_handler import ExcelHandler
from configparser import ConfigParser

from __init__ import PROJECT_ROOT


pd.set_option("future.no_silent_downcasting", True)


class Summarizer:
    def __init__(self, month: int):
        self.month = month

        config_object = ConfigParser()
        config_object.read(f"{PROJECT_ROOT}/config.ini")
        self.feeder_folder = config_object["DEFAULT"]["feeder_folder"]
        self.database_folder = f'{config_object["DEFAULT"]["data_folder"]}/{config_object["DEFAULT"]["current_year"]}'
        self.current_year = config_object["DEFAULT"]["current_year"]
        self.output_folder = config_object["DEFAULT"]["output_folder"]
        self.results_folder = config_object["DEFAULT"]["results_folder"]

        self._monthly_summary_file_name = f"{self.current_year}_monthly_summary.xlsx"
        self._monthly_consumptions_file_name = f"monthly_consumptions.xlsx"

        self.account_summaries = self._get_account_summaries()

        self._delete_source_files()

    def _delete_source_files(self):
        """delete source files because when we are at this step, it's sure we don't need them anymore"""
        files = glob.glob(f"{self.feeder_folder}/*")
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

        """
        add one empty row after the last row of df and then calculate the sum of the sum column, extracting the
        following fields:
        * salary
        """
        df.loc[len(df)] = pd.Series(dtype="float64")
        df.at[df.index[-1], "category"] = "SUM"
        df.at[df.index[-1], "sum"] = df["sum"].sum()
        df.at[df.index[-1], "sum"] -= df.loc[df["category"] == "salary", "sum"].values[
            0
        ]

        # add one empty row after the last row of df and then calculate the earnings from SUM and salary
        df.loc[len(df)] = pd.Series(dtype="float64")
        df.at[df.index[-1], "category"] = "EARNINGS"
        df.at[df.index[-1], "sum"] = (
            df.loc[df["category"] == "salary", "sum"].values[0]
            + df.loc[df["category"] == "SUM", "sum"].values[0]
        )

        file = f"{self.output_folder}/{self._monthly_summary_file_name}"
        return ExcelHandler.add_df_to_excel(df, self.month, file, return_df=True)

    def write_monthly_summary_to_monthly_consumptions(
        self, monthly_summary: pd.DataFrame
    ):
        """
        write self.month's summary to a single file. every row should start with the month's name and then the summary
        of every category. the header of the columns will be the category names
        """
        file = f"{self.output_folder}/{self._monthly_consumptions_file_name}"
        try:
            df = pd.read_excel(file, header=0, index_col=0)
        except FileNotFoundError:
            df = pd.DataFrame()

        # reformat monthly_summary
        if self.month < 10:
            self.month = f"0{self.month}"
        current_index = f"{self.current_year}-{self.month}"
        monthly_summary = monthly_summary.transpose().rename(
            index={"sum": current_index}
        )
        ## grab the first row for the header
        new_header = monthly_summary.iloc[0]
        ## take the data less the header row
        monthly_summary = monthly_summary[1:]
        ## set the header row as the df header
        monthly_summary.columns = new_header
        ## put SUM column to be the first column
        monthly_summary = monthly_summary[
            ["SUM"]
            + ["EARNINGS"]
            + ["salary"]
            + [
                col
                for col in monthly_summary.columns
                if col not in ["SUM", "EARNINGS", "salary"]
            ]
        ]

        if current_index in df.index:
            df = df.drop(current_index)
        result = pd.concat([df, monthly_summary], join="outer").fillna(0)
        result = result.sort_index(ascending=False)

        result.to_excel(file)

    def copy_results(self):
        """
        copy results from output_folder to results_folder
        """
        shutil.copyfile(
            f"{self.output_folder}/{self._monthly_summary_file_name}",
            f"{self.results_folder}/{self._monthly_summary_file_name}",
        )

        shutil.copyfile(
            f"{self.output_folder}/{self._monthly_consumptions_file_name}",
            f"{self.results_folder}/{self._monthly_consumptions_file_name}",
        )

    def execute(self):
        monthly_summaries = self.calc_monthly_summary()
        self.write_monthly_summary_to_monthly_consumptions(
            monthly_summaries[self.month]
        )
        self.copy_results()


def main(month: int):
    summarizer = Summarizer(month)
    summarizer.execute()


if __name__ == "__main__":
    main(int(sys.argv[1]))
