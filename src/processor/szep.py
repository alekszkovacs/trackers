from processor import Processor


class Szep(Processor):
    def execute(self):
        categories_fname = "szep_categories.yaml"
        source_fname = "exportalt__tablazat.xlsx"
        output_fname = "zzzzzzzzzzres_SZEP.xlsx"
        completed_txns_column = "Státusz"
        date_column = "Dátum"
        amount_column = "Összeg"
        vendor_column = "Ellenoldali név"

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
        # add "Sikeres" Státusz to txns with "Feltöltés" Jogcím
        self.df.loc[
            (self.df["Jogcím"] == "Feltöltés"), self.completed_txns_column
        ] = "Sikeres"

    def _keep_only_completed_txns(self):
        df = self.df
        self.df = df[df[self.completed_txns_column] == ("Sikeres")]

    def _adjust_amounts(self):
        """
        combine "Jóváírás" and "Terhelés" columns into "Összeg" column, making values under "Terhelés" negative first
        """
        df = self.df
        df["Terhelés"] = df["Terhelés"] * -1

        df["Jóváírás"].fillna(0, inplace=True)
        df["Terhelés"].fillna(0, inplace=True)
        df["Összeg"] = df["Jóváírás"] + df["Terhelés"]

        self.df = df


if __name__ == "__main__":
    szep = Szep()
    szep.execute()
