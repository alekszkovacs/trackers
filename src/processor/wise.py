from src.processor.processor import Processor


class Wise(Processor):
    def execute(self):
        categories_fname = "wise_categories.yaml"
        source_fname = "transaction-history.csv"
        output_fname = "zzzzzzzzzzres_WISE.xlsx"
        completed_txns_column = "Status"
        # keep "Finished on" and drop "Created on" because "Finished on" is what Wise app shows
        date_column = "Finished on"
        amount_column = "Amount"
        vendor_column = "Target name"

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

    def _remove_bank_stuff(self):
        """
        Remove rows where "Target name" is "Alex Márk Kovács".
        With this we will get rid from txns which were money top-ups.
        """
        df = self.df
        self.df = df[~df[self.vendor_column].str.contains("Alex Márk Kovács")]

    def _keep_only_completed_txns(self):
        df = self.df
        self.df = df[df[self.completed_txns_column] == ("COMPLETED")]

    def _adjust_amounts(self):
        """
        - add "Source fee amount" and "Source amount (after fees)" to get "Amount"
        - add negative sign to "Amount" if "Direction" is "OUT"
        """
        self.df[self.amount_column] = self.df.apply(
            lambda row: row["Source fee amount"] + row["Source amount (after fees)"],
            axis=1,
        )
        self.df[self.amount_column] = self.df.apply(
            lambda row: row[self.amount_column] * -1
            if row["Direction"] == "OUT"
            else row[self.amount_column],
            axis=1,
        )


if __name__ == "__main__":
    wise = Wise()
    wise.execute()
