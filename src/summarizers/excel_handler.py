import pandas as pd


class ExcelHandler:
    @staticmethod
    def read_excel(fname: str) -> dict[pd.DataFrame]:
        try:
            dfs = pd.read_excel(fname, sheet_name=None)
        except FileNotFoundError:
            return {}

        return {int(k): v for k, v in dfs.items()}

    @staticmethod
    def write_excel(dfs: dict[pd.DataFrame], fname: str):
        dfs = {k: dfs[k] for k in sorted(dfs)}
        with pd.ExcelWriter(fname) as writer:
            for sheet_name, df in dfs.items():
                df.to_excel(writer, sheet_name=str(sheet_name), index=False)

    @staticmethod
    def add_df_to_excel(df: pd.DataFrame, sheet_name: str, fname: str):
        dfs = ExcelHandler.read_excel(fname)
        dfs[sheet_name] = df
        ExcelHandler.write_excel(dfs, fname)
