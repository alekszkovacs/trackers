import os
import yaml
import pandas as pd
import warnings

from abc import ABC, abstractmethod
from category_mapper import CategoryMapper
from configparser import ConfigParser

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = f"{CURRENT_DIR}/../.."


class Processor(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.categories = None
        self.df = None
        self.category_mapper = CategoryMapper()

        config_object = ConfigParser()
        config_object.read(f"{PROJECT_ROOT}/config.ini")
        self.source_folder = config_object["DEFAULT"]["source_folder"]
        self.output_folder = config_object["DEFAULT"]["output_folder"]

        self.completed_txns_column = None
        self.date_column = None
        self.amount_column = None
        self.vendor_column = None
        self.category_column = "Category"

    @abstractmethod
    def execute(self):
        """
        Calls _execute() with the correct parameters.
        """
        pass

    def _execute(
        self,
        categories_fname: str = "",
        source_fname: str = "",
        output_fname: str = "",
        completed_txns_column: str = "",
        date_column: str = "",
        amount_column: str = "",
        vendor_column: str = "",
    ) -> None:
        """
        args:
        * categories_fname
        * source_fname
        * output_fname
        * completed_txns_column
        * date_column
        * amount_column
        * vendor_column
        """

        categories_path = f"{CURRENT_DIR}/categories/{categories_fname}"
        source_path = f"{PROJECT_ROOT}/{self.source_folder}/{source_fname}"
        output_path = f"{PROJECT_ROOT}/{self.output_folder}/{output_fname}"

        self.completed_txns_column = completed_txns_column
        self.date_column = date_column
        self.amount_column = amount_column
        self.vendor_column = vendor_column

        columns_to_keep = [self.date_column, self.amount_column, self.vendor_column]
        columns_order = [
            self.date_column,
            self.amount_column,
            self.category_column,
            "",
            self.vendor_column,
        ]

        self._init_source(source_path)
        self._init_categories(categories_path)
        self._remove_account_stuff()
        self._keep_only_completed_txns()
        self._adjust_amounts()
        self._keep_columns(columns_to_keep)
        self._reorder_columns(columns_order)
        self._assign_categories_to_vendors()
        self._keep_only_first_days()
        self._put_categories_to_the_top()
        # self._put_categories_to_the_right()
        self._write_df_to_file(output_path)
        # self._delete_source(source_path)

    def _init_source(self, file: str):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            if file.endswith(".xlsx") or file.endswith("xls"):
                txns = pd.read_excel(file)
            elif file.endswith(".csv"):
                txns = pd.read_csv(file, encoding="utf-8-sig")
            self.df = pd.DataFrame(txns)

    def _init_categories(self, file: str):
        with open(file, "r") as f:
            self.categories = yaml.safe_load(f)

        all_categories = [
            category.split(".")[0]
            for category in os.listdir(self.category_mapper.source_path)
        ]
        _list = [
            category for category in self.categories if category not in all_categories
        ]
        if len(_list) > 0:
            raise Exception(
                f"'{_list[0]}' category is not in the category_mapper folder!"
            )

    def _delete_source(self, file: str) -> None:
        os.remove(file)

    def _keep_columns(self, columns: list[str]):
        self.df = self.df[columns]

    def _reorder_columns(self, columns: list[str]):
        self.df = self.df.reindex(columns=columns)

    def _assign_categories_to_vendors(self):
        vendors = self.df[self.vendor_column].tolist()
        categories = self.category_mapper.map_from_vendor_list(vendors)

        if self.category_column not in self.df.columns:
            raise Exception("Category column must exists!")

        self.df[self.category_column] = categories

    def _keep_only_first_days(self):
        df = self.df
        column = self.date_column
        df[column] = pd.to_datetime(df[column])
        df = df.sort_values(by=column).reset_index(drop=True)
        df[column] = df[column].dt.day
        df.loc[df.duplicated(column, keep="first"), column] = ""
        self.df = df

    def _put_categories_to_the_top(self):
        """
        Puts categories to the top of the dataframe, above Category column.
        It helps in manual categorization, excel suggests values from the values in the same column.
        """
        df = self.df
        top_categories = pd.DataFrame({"a": None, "b": None, "c": self.categories})
        # reindex to have matching column labels
        df.columns = range(0, df.columns.size)
        top_categories.columns = range(0, top_categories.columns.size)
        self.df = pd.concat([top_categories, df]).reset_index(drop=True)

    def _put_categories_to_the_right(self):
        """
        Puts categories next to the dataframe.
        It is more readable then it is on the top, however this has no usecase.
        """
        df = self.df
        right_categories = pd.DataFrame(
            {"a": None, "b": None, "c": None, "categories": self.categories}
        )
        self.df = pd.concat([df, right_categories], axis=1).reset_index(drop=True)

    def _write_df_to_file(self, file: str) -> None:
        self.df.to_excel(file, index=None, header=False)

    def _delete_source(self, file: str) -> None:
        os.remove(file)

    """ 
    ### Abstract methods ###
    These methods are not required by all accounts and probably very specific to a account, so they are abstracted, which means
    that you must specify in child if they are needed.
    """

    @abstractmethod
    def _remove_account_stuff(self):
        pass

    @abstractmethod
    def _keep_only_completed_txns(self):
        pass

    @abstractmethod
    def _adjust_amounts(self):
        pass
