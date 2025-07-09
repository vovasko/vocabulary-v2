import sqlite3
from pandas import DataFrame, read_sql_query
from re import search, IGNORECASE
from pathlib import Path

class DBManager:
    def __init__(self):
        # self.path = Path(__file__).parent.parent / "db/vocabulary.db"
        self.path = self.get_db_path()
        self.connect_to_db()

    def get_db_path(self):
        # Save in user-specific folder: ~/.vocab_app/
        db_dir = Path.home() / ".vocab_app"
        db_dir.mkdir(parents=True, exist_ok=True)
        return db_dir / "vocabulary.db"

    def connect_to_db(self):
        try:
            self.connection = sqlite3.connect(self.path)
            self.cursor = self.connection.cursor()
            print(f"[INFO] Connected to database at {self.path}")
            self.create_table()
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to connect to database: {e}")
            raise 

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

    def insert_data(self, data: dict | list | DataFrame): # ensure to always form dictionaries 
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()

            if isinstance(data, DataFrame): 
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

    def update_data(self, data: dict | list | DataFrame): # to bulk update, all columns should be same
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()

            if isinstance(data, DataFrame):
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
            
    def delete_data(self, data: dict | list | DataFrame):
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()

            delete_query = """
            DELETE FROM vocabulary
            WHERE rowid=:rowid; """

            try:
                if isinstance(data, list):
                    cursor.executemany(delete_query, data)
                elif isinstance(data, DataFrame):
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
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            select_query = "SELECT rowid, * FROM vocabulary "

            match mode:
                case "duplicates": select_query += """                                    
                                    WHERE (type, german) IN (
                                        SELECT type, german FROM vocabulary
                                        GROUP BY type, german
                                        HAVING COUNT(*) > 1
                                    ); """
                case "nulls"     : select_query += """
                                    WHERE translation IS NULL;
                                    """
                case "new"       : select_query += "WHERE score = 0;"
                case "repeat"    : select_query += "WHERE score IN (-1, 1);"
                case "learnt"    : select_query += "WHERE score IN (2, 3);"
                case "nouns"     : select_query += "WHERE type IN ('NOUN', 'PROPN', 'der', 'die', 'das');"
                case "verbs"     : select_query += "WHERE type IN ('VERB', 'AUX');"
                case "adjectives": select_query += "WHERE type IN ('ADJ', 'ADP', 'ADV');"
                case "other"     : select_query += "WHERE type NOT IN ('NOUN', 'VERB', 'ADJ', 'PROPN', 'AUX', 'ADP', 'ADV', 'der', 'die', 'das');"
                case _           : select_query += ";" # all

            if just_return_query:
                return select_query
            else:
                cursor.execute(select_query)
                return cursor.fetchall()
            
    def count_rows(self, mode: str = "all") -> int:
        select_query = self.fetch_data(mode, just_return_query=True)

        match = search(r'\bFROM\b', select_query, IGNORECASE)
        if match:
            from_index = match.start()
            count_query = 'SELECT COUNT(*) ' + select_query[from_index:]
        else: count_query = "SELECT COUNT(*) FROM vocabulary;"

        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            cursor.execute(count_query)
            return cursor.fetchone()[0]

    def to_dataframe(self, mode: str = "all", filters: tuple[str, list] = None) -> DataFrame:
        if mode == "filter" and filters is not None:
            query = self.create_filter_query(filters)
        else: 
            query = self.fetch_data(mode, just_return_query=True) # get query according to given mode
        with sqlite3.connect(self.path) as connection:
            # read the data into DataFrame and make rowid the index
            return read_sql_query(query, connection, index_col="rowid") 
        
    def update_from_df(self, df: DataFrame):
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

    def create_filter_query(self, filter_tuple: tuple[str, list]):
        select_query = "SELECT rowid, * FROM vocabulary "

        if filter_tuple[0] in ("type", "score"):
            values = ", ".join(f"'{elem}'" for elem in filter_tuple[1])
            select_query += f"WHERE {filter_tuple[0]} IN ({values});" 

        if filter_tuple[0] in ("TYPE"):
            values = ""
            other_type = ""
            for mode in filter_tuple[1]:
                match mode:
                    case "noun"     : values += "'NOUN', 'PROPN', 'der', 'die', 'das',"
                    case "verb"     : values += "'VERB', 'AUX'," 
                    case "adjective": values += "'ADJ', 'ADP', 'ADV',"
                    case "other"    : other_type += "WHERE type NOT IN ('NOUN', 'VERB', 'ADJ', 'PROPN', 'AUX', 'ADP', 'ADV', 'der', 'die', 'das')"
                    case _          : pass # all            
            if other_type:
                select_query += other_type
                if values: # if len(values) > 0
                    select_query += f" OR type IN ({values[:-1]});" 
                else:  select_query += ';'
            elif values: select_query += f"WHERE type IN ({values[:-1]});"
            else: select_query += ';'

        if filter_tuple[0] in ("special"):
            where_clause = ""
            for mode in filter_tuple[1]:
                if where_clause: where_clause += " OR "
                match mode:
                    case "duplicates": where_clause += """
                                        (type, german) IN (
                                        SELECT type, german FROM vocabulary
                                        GROUP BY type, german
                                        HAVING COUNT(*) > 1 )"""
                    case "nulls"     : where_clause += "translation IS NULL"
            select_query += "WHERE " + where_clause

        return select_query