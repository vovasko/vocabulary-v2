import sqlite3
import pandas as pd
from pathlib import Path

class DBManager:
    def __init__(self):
        self.path = Path(__file__).parent.parent / "db/vocabulary.db"
        self.connect_to_db()

    def connect_to_db(self):
        try:
            connection = sqlite3.connect(self.path)
            connection.close()
            print(f"[INFO] Connected to database at {self.path}")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to connect to database: {e}")
            raise  # re-raise to let the app handle it

    def create_db(self):
        with sqlite3.connect(self.path) as connection:
            pass

    def create_table(self):
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary (
                type TEXT NOT NULL,
                german TEXT NOT NULL,
                translation TEXT,
                second_translation TEXT,
                example TEXT,
                meaning TEXT,
                score INTEGER NOT NULL DEFAULT 0
            ); """)

            connection.commit()

    def insert_data(self, data: dict | list | pd.DataFrame): # ensure to always form dictionaries 
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()

            if isinstance(data, pd.DataFrame): 
                if "rowid" in data.columns: # if rowid is in the df, make it index
                        data.set_index("rowid", inplace=True)
                data = data.to_dict(orient="records")
            template = data[0] if isinstance(data, list) else data # get a dict to use as template

            insert_query = f"""
            INSERT INTO vocabulary ({", ".join(template.keys())})
            VALUES ({", ".join([f":{key}" for key in template.keys() if key != "rowid"])});
            """

            try:
                if isinstance(data, list):
                    cursor.executemany(insert_query, data)
                else:
                    cursor.execute(insert_query, data)
                connection.commit()
            except sqlite3.IntegrityError as e:
                print("IntegrityError:", e)
            except Exception as e:
                print("Error:", e)

    def update_data(self, data: dict | list | pd.DataFrame): # to bulk update, all columns should be same
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()

            if isinstance(data, pd.DataFrame):
                if "rowid" not in data.columns: # if rowid is not in the df, add it from index
                        data.reset_index(inplace=True)
                data = data.to_dict(orient="records")
            template = data[0] if isinstance(data, list) else data # get a dict to use as template

            set_clause = ", ".join([f"{key}=:{key}" for key in template.keys() if key != "rowid"])
            update_query = f"""
                UPDATE vocabulary
                SET {set_clause}
                WHERE rowid=:rowid;
                """

            try:
                if isinstance(data, list):
                    cursor.executemany(update_query, data)
                else:
                    cursor.execute(update_query, data)
                connection.commit()
            except sqlite3.IntegrityError as e:
                print("IntegrityError:", e)
            except Exception as e:
                print("Error:", e)
            
    def delete_data(self, data: dict | list | pd.DataFrame):
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()

            delete_query = """
            DELETE FROM vocabulary
            WHERE rowid=:rowid; """

            try:
                if isinstance(data, list):
                    cursor.executemany(delete_query, data)
                elif isinstance(data, pd.DataFrame):
                    if "rowid" not in data.columns: # if rowid is not in the df, add it from index
                        data.reset_index(inplace=True)
                    data_list = data.to_dict(orient="records")
                    cursor.executemany(delete_query, data_list)
                else:
                    cursor.execute(delete_query, data)
                connection.commit()
            except sqlite3.IntegrityError as e:
                print("IntegrityError:", e)
            except Exception as e:
                print("Error:", e)

    def drop_table(self):
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()

            cursor.execute("DROP TABLE IF EXISTS vocabulary;")

            connection.commit()
        
    def fetch_data(self, mode: str = "all", just_return_query: bool = False) -> list | str:
        # return either a list of tuples or a query string
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()

            match mode:
                case "duplicates": select_query = """
                                    SELECT rowid, * FROM vocabulary
                                    WHERE (type, german) IN (
                                        SELECT type, german FROM vocabulary
                                        GROUP BY type, german
                                        HAVING COUNT(*) > 1
                                    ); """
                case "new"       : select_query = "SELECT rowid, * FROM vocabulary WHERE score = 0;"
                case "nouns"     : select_query = "SELECT rowid, * FROM vocabulary WHERE type IN ('NOUN', 'PROPN', 'der', 'die', 'das');"
                case "verbs"     : select_query = "SELECT rowid, * FROM vocabulary WHERE type IN ('VERB', 'AUX');"
                case "adjectives": select_query = "SELECT rowid, * FROM vocabulary WHERE type IN ('ADJ', 'ADP', 'ADV');"
                case "other"     : select_query = "SELECT rowid, * FROM vocabulary WHERE type NOT IN ('NOUN', 'VERB', 'ADJ', 'PROPN', 'AUX', 'ADP', 'ADV', 'der', 'die', 'das');"
                case _           : select_query = "SELECT rowid, * FROM vocabulary;" # all

            if just_return_query:
                return select_query
            else:
                cursor.execute(select_query)
                return cursor.fetchall()
            
    def count_rows(self, mode: str = "all") -> int:
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()

            match mode:
                case "duplicates": count_query = """
                                    SELECT COUNT(*) FROM vocabulary
                                    WHERE (type, german) IN (
                                        SELECT type, german FROM vocabulary
                                        GROUP BY type, german
                                        HAVING COUNT(*) > 1
                                    ); """
                case "nulls"     : count_query = """
                                    SELECT COUNT(*) FROM vocabulary
                                    WHERE translation IS NULL
                                    OR second_translation IS NULL
                                    OR example IS NULL
                                    OR meaning IS NULL;
                                    """
                case "new"       : count_query = "SELECT COUNT(*) FROM vocabulary WHERE score = 0;"
                case _           : count_query = "SELECT COUNT(*) FROM vocabulary;"

            cursor.execute(count_query)
            return cursor.fetchone()[0]

    def to_dataframe(self, mode: str = "all") -> pd.DataFrame:
        query = self.fetch_data(mode, just_return_query=True) # get query according to given mode
        with sqlite3.connect(self.path) as connection:
            # read the data into a DataFrame and make rowid the index
            return pd.read_sql_query(query, connection, index_col="rowid") 
        
    def update_from_df(self, df: pd.DataFrame):
        if "rowid" not in df.columns: # if rowid is not in the df, add it from index
            df.reset_index(inplace=True)

        self.update_data(df)

        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            query = """
            DELETE FROM vocabulary WHERE german LIKE '#del%';
            """
            cursor.execute(query)
            connection.commit()