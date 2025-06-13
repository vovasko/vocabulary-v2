import pandas as pd
from services.DB_manager import DBManager

class DFManager():
    def __init__(self):
        self.data = pd.DataFrame()
        self.db = DBManager()
        self.fill_data()

    def fill_data(self):
        # dummy_data = [
        #     [f"type", f"Word number {i}", f"Here goes translation", "Here goes another translation", "Some long sentance goes here", "Some long sentance goes here", i%4]
        #     for i in range(20)
        # ]
        # new_df = pd.DataFrame(dummy_data, columns=self.data.columns)

        # self.data = pd.concat(objs=[self.data, new_df])
        self.data = self.db.to_dataframe()

    def delete_rows(self, rowids: list[int]):
        self.data.drop(rowids, inplace=True)
        rows_to_delete = [{"rowid": n} for n in rowids]
        self.db.delete_data(data=rows_to_delete)
        self.print_info()

    def print_info(self):
        print(self.data.info())
        print(f"{'':=^100}")
        print(self.data)