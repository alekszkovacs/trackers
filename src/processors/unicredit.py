import math
from processor import Processor


class Unicredit(Processor):
    def execute(self):
        categories_fname = "unicredit_categories.yaml"
        source_fname = "export.xls"
        output_fname = "zzzzzzzzzzres_unicredit.xlsx"
        completed_txns_column = "Státusz"
        date_column = "Érték Dátum"
        amount_column = "Összeg"
        vendor_column = "Partner"

        self._execute(
            categories_fname=categories_fname,
            source_fname=source_fname,
            output_fname=output_fname,
            completed_txns_column=completed_txns_column,
            date_column=date_column,
            amount_column=amount_column,
            vendor_column=vendor_column,
        )

    def __init__(self) -> None:
        super().__init__()

    def _remove_account_stuff(self):
        self.df.columns = self.df.iloc[2]
        self.df = self.df[3:]

        # remove revolut top-ups
        df = self.df
        self.df = df[
            ~df[self.vendor_column].str.contains(
                "revolut**", case=False, na=False, regex=False
            )
        ]

    def _keep_only_completed_txns(self):
        df = self.df
        self.df = df[df[self.completed_txns_column] == ("Könyvelt")]

    def _adjust_amounts(self):
        self.df[self.amount_column] = self.df.apply(
            lambda row: math.floor(
                float(
                    row[self.amount_column]
                    .replace("\xa0", "")
                    .replace(",", ".")
                    .split(" ")[0]
                )
            ),
            axis=1,
        )


if __name__ == "__main__":
    unicredit = Unicredit()
    unicredit.execute()
