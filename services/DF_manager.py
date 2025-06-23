import pandas as pd
from services.DB_manager import DBManager
from flet import Container

class DFManager():
    def __init__(self):
        self.data = pd.DataFrame()
        self.db = DBManager()
        self.fill_data()

    def fill_data(self):
        self.data = self.db.to_dataframe()

    def delete_rows(self, rowids: list[int]):
        self.data.drop(rowids, inplace=True)
        rows_to_delete = [{"rowid": n} for n in rowids]
        self.db.delete_data(data=rows_to_delete)

    def print_info(self, df: pd.DataFrame = None):
        if not isinstance(df, pd.DataFrame): df = self.data
        print(df.info())
        print(f"{'':=^100}")
        print(df)

    def update_record(self, container: Container): # Update method for updates from edit dialog
        row_index = container.data["rowid"]
        new_row = {}
        for control in container.content.controls:
            new_row[control.data["col"]] = control.value

        if row_index in self.data.index:
            valid_keys = [k for k in new_row if k in self.data.columns]
            if valid_keys:
                self.data.loc[row_index, valid_keys] = pd.Series(new_row) # update DataFrame
                new_row["rowid"] = row_index
                self.db.update_data(new_row) # update DB with rowid
            else:
                print("[WARN] No valid columns to update.")
        else:
            print(f"[ERROR] Index {row_index} not found in DataFrame.")

    def update_scores(self, df: pd.DataFrame):
        self.db.update_data(data=df) # Update scores for selected rowids
        self.fill_data() # Than refresh DF

    def create_new_record(self, new_row: dict):
        for key in new_row.keys():
            if new_row[key] in ("", "-"):
                new_row[key] = None
        self.db.insert_data(new_row) # Insert row first in DB
        self.fill_data() # Than refresh DF

    def fetch_df(self, mode: str, filters: tuple[str, str|list] = None) -> pd.DataFrame:
        return self.db.to_dataframe(mode, filters=filters)