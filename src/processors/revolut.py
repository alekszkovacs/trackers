from processor import Processor


class Revolut(Processor):
    def execute(self):
        categories_fname = "revolut_categories.yaml"
        source_fname = "account-statement.csv"
        output_fname = "zzzzzzzzzzres_revolut.xlsx"
        completed_txns_column = "State"
        # keep "Started Date" and drop "Completed Date" because "Started Date" is what Revolut app shows
        date_column = "Started Date"
        amount_column = "Amount"
        vendor_column = "Description"

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
        # remove rows from df which contain "To HUF" or "Apple Pay Top-Up" in the "Description" column
        df = self.df
        self.df = df[~df[self.vendor_column].str.contains("To HUF|Apple Pay Top-Up")]

    def _keep_only_completed_txns(self):
        df = self.df
        self.df = df[df[self.completed_txns_column] == ("COMPLETED")]

    def _adjust_amounts(self):
        pass


if __name__ == "__main__":
    revolut = Revolut()
    revolut.execute()
