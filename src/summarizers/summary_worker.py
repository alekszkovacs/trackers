import pandas as pd
import shutil

from config import Config
from excel_handler import ExcelHandler


class SummaryWorker:
    def __init__(self, month: int):
        self.config = Config.get_config()
        self.month = month
        self._monthly_summary_file_name = (
            f"{self.config.current_year}_monthly_summary.xlsx"
        )
        self._monthly_consumptions_file_name = "monthly_consumptions.xlsx"

    def _calc_monthly_summary(self, sum_dfs: list[pd.DataFrame]):
        sum_df = None
        for df in sum_dfs:
            if sum_df is None:
                sum_df = df
            else:
                sum_df = pd.concat([sum_df, df], ignore_index=True)
        df = sum_df.groupby("category")["sum"].sum().reset_index()

        # add one empty row after the last row of df and then calculate the sum of the sum column, extracting the
        # following fields:
        # * salary
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

        file = f"{self.config.sum_folder}/{self._monthly_summary_file_name}"
        return ExcelHandler.add_df_to_excel(df, self.month, file, return_df=True)

    def _add_monthly_summary_to_monthly_consumptions(
        self, monthly_summary: pd.DataFrame
    ):
        """
        write self.month's summary to a single file. every row should start with the month's name and then the summary
        of every category. the header of the columns will be the category names
        """
        file = f"{self.config.sum_folder}/{self._monthly_consumptions_file_name}"
        try:
            df = pd.read_excel(file, header=0, index_col=0)
        except FileNotFoundError:
            df = pd.DataFrame()

        # reformat monthly_summary
        if self.month < 10:
            month = f"0{self.month}"
        else:
            month = self.month
        current_index = f"{self.config.current_year}-{month}"
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

    def _copy_results(self):
        """
        copy results from sum_folder to results_folder
        """
        shutil.copyfile(
            f"{self.config.sum_folder}/{self._monthly_summary_file_name}",
            f"{self.config.results_folder}/{self._monthly_summary_file_name}",
        )

        shutil.copyfile(
            f"{self.config.sum_folder}/{self._monthly_consumptions_file_name}",
            f"{self.config.results_folder}/{self._monthly_consumptions_file_name}",
        )

    def execute(
        self,
        sum_dfs: list[pd.DataFrame],
    ):
        monthly_summaries = self._calc_monthly_summary(sum_dfs)
        self._add_monthly_summary_to_monthly_consumptions(monthly_summaries[self.month])
        self._copy_results()
