from pandas import DataFrame, Series
from services.DB_manager import DBManager
from flet import Container

class DFManager():
    def __init__(self, fill = True):
        print("DFManager called")
        self.data = DataFrame()
        self.db = DBManager()
        if fill: self.fill_data()

    def fill_data(self):
        self.data = self.db.to_dataframe()

    def delete_rows(self, rowids: list[int]):
        self.data.drop(rowids, inplace=True)
        rows_to_delete = [{"rowid": n} for n in rowids]
        self.db.delete_data(data=rows_to_delete)

    def print_info(self, df: DataFrame = None):
        if not isinstance(df, DataFrame): df = self.data
        print(df.info())
        print(f"{'':=^100}")
        print(df)

    def update_record(self, container: Container): # Update method for updates from edit dialog
        row_index = container.data["rowid"]
        new_row = {}
        for control in container.content.controls:
            value = control.value
            if value in ("", "-"):
                value = None
            new_row[control.data["col"]] = value

        if row_index in self.data.index:
            valid_keys = [k for k in new_row if k in self.data.columns]
            if valid_keys:
                self.data.loc[row_index, valid_keys] = Series(new_row) # update DataFrame
                new_row["rowid"] = row_index
                self.db.update_data(new_row) # update DB with rowid
            else:
                print("[WARN] No valid columns to update.")
        else:
            print(f"[ERROR] Index {row_index} not found in DataFrame.")

    def update_scores(self, df: DataFrame):
        self.db.update_data(data=df) # Update scores for selected rowids
        self.fill_data() # Than refresh DF

    def create_new_record(self, new_row: dict):
        if new_row == None: return
        for key in new_row.keys():
            if new_row[key] in ("", "-"):
                new_row[key] = None
        self.db.insert_data(new_row) # Insert row first in DB
        self.fill_data() # Than refresh DF

    def add_translated_data(self, new_data: DataFrame):
        self.db.insert_data(new_data)
        self.fill_data() # Refresh DF

    def fetch_df(self, mode: str, filters: tuple[str, str|list] = None) -> DataFrame:
        return self.db.to_dataframe(mode, filters=filters)