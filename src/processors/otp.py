from processor import Processor


class Otp(Processor):
    def execute(self):
        categories_fname = "otp_categories.yaml"
        source_fname = "tranzakciók.xlsx"
        output_fname = "zzzzzzzzzzres_otp.xlsx"
        date_column = "Tranzakció dátuma"
        amount_column = "Összeg"
        vendor_column = "Partner neve"

        self._execute(
            categories_fname=categories_fname,
            source_fname=source_fname,
            output_fname=output_fname,
            date_column=date_column,
            amount_column=amount_column,
            vendor_column=vendor_column,
        )

    def __init__(self) -> None:
        super().__init__()

    def _remove_account_stuff(self):
        # remove revolut top-ups
        df = self.df
        self.df = df[
            ~df[self.vendor_column].str.contains(
                "revolut**", case=False, na=False, regex=False
            )
        ]

    def _keep_only_completed_txns(self):
        pass

    def _adjust_amounts(self):
        pass


if __name__ == "__main__":
    otp = Otp()
    otp.execute()
