import pandas as pd
import shutil

from config import Config


class OccasionWorker:
    def __init__(self, month: int):
        self.config = Config.get_config()
        self.month = month
        self._occasions_summary_file_name = "occasions_summary.xlsx"

    def _calc_monthly_occasions(self, occasion_dfs: list[pd.DataFrame]) -> set[str]:
        """
        1. add each occasion's cost from multiple accounts together
        2. check if there is already a file named like the occasion, if not, create one
        3. add the current year-month's cost to the file with month and cost columns
        4. if there is already a line with the current year-month, update the cost
        """
        occasions = {}
        for _df in occasion_dfs:
            for occasion, cost in _df.values:
                if occasion in occasions:
                    occasions[occasion] += cost
                else:
                    occasions[occasion] = cost

        for occasion, _sum in occasions.items():
            file = f"{self.config.occasions_folder}/{occasion}.xlsx"
            try:
                df = pd.read_excel(file, header=0, index_col=0)
            except FileNotFoundError:
                df = pd.DataFrame(columns=["sum"])

            if self.month < 10:
                month = f"0{self.month}"
            else:
                month = self.month
            current_index = f"{self.config.current_year}-{month}"

            if current_index in df.index:
                df.at[current_index, "sum"] = _sum
            else:
                df.loc[current_index] = _sum

            result = df.sort_index(ascending=False)
            result.to_excel(file)

        return occasions.keys()

    def _add_monthly_occasions_to_occasion_summary(self, occasions: set[str]):
        """
        add the calculated monthly occasions to the occasion summary. every row should start with the occasion name and
        then the summary of every occasion group.
        occasion summary goes across years and months.
        """
        file = f"{self.config.sum_folder}/{self._occasions_summary_file_name}"
        try:
            occasions_summary_df = pd.read_excel(file, header=0, index_col=0)
        except FileNotFoundError:
            occasions_summary_df = pd.DataFrame(columns=["sum"])

        for occasion in occasions:
            occasion_file = f"{self.config.occasions_folder}/{occasion}.xlsx"
            df = pd.read_excel(occasion_file, header=0, index_col=0)
            _sum = df["sum"].sum()
            occasions_summary_df.at[occasion, "sum"] = _sum

        occasions_summary_df.to_excel(file)

    def _copy_results(self):
        """
        copy results from sum_folder to results_folder
        """
        shutil.copyfile(
            f"{self.config.sum_folder}/{self._occasions_summary_file_name}",
            f"{self.config.results_folder}/{self._occasions_summary_file_name}",
        )

    def execute(
        self,
        occasion_dfs: list[pd.DataFrame],
    ):
        occasions = self._calc_monthly_occasions(occasion_dfs)
        self._add_monthly_occasions_to_occasion_summary(occasions)
        self._copy_results()
