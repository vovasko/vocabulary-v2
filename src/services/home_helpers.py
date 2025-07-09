from services.settings import SettingsManager
from services.translator import Netzverb
from services.DF_manager import DFManager

from datetime import datetime
from random import choice

class DayWord():
    def __init__(self):
        self.settings = SettingsManager()

        self.today = datetime.today().date()
        self.word_data = None
        self.saved = False
        self.load_word()
        self.actualize_word()

    def get_word_data(self):
        words = Netzverb.get_random_words()
        if words == None: 
            self.load_word()
            # call dialog and say couldn't retrieve new word
            print("Could not retrieve new word")
        else: 
            self.word_data = None
            self.saved = False
            while self.word_data == None:
                word = choice(words) # choose random word
                print(f"Getting info for {word}")
                self.word_data = Netzverb.get_noun_data(word, self.settings._data)
            self.save_word()
            print("New word saved to settings")

    def save_word(self):
        self.settings.set("day_word.date", str(self.today))
        self.settings.set("day_word.saved", self.saved)
        self.settings.set("day_word.data", self.word_data)
        self.settings.save()
        print("word saved")

    def load_word(self):
        self.word_data = self.settings.get("day_word.data")
        self.saved = self.settings.get("day_word.saved")

    def actualize_word(self):
        previous_date = self.settings.get("day_word").get("date")
        previous_date = datetime.strptime(previous_date, "%Y-%m-%d").date()
        if self.today > previous_date: self.get_word_data()
        else: print("Word is up to date")

    def on_word_added(self):
        self.saved = True
        self.settings.set("day_word.saved", self.saved)
        self.settings.save()


class Statistics():
    def __init__(self, df_manager: DFManager):
        self.df_manager = df_manager

        self.words_count = self.df_manager.count_rows("all")
        self.duplicates = self.df_manager.count_rows("duplicates")
        self.nulls = self.df_manager.count_rows("nulls")
        self.new = self.df_manager.count_rows("new")
        self.repeat = self.df_manager.count_rows("repeat")
        self.learnt = self.df_manager.count_rows("learnt")
        self.nouns = self.df_manager.count_rows("nouns")
        self.verbs = self.df_manager.count_rows("verbs")
        self.adjectives = self.df_manager.count_rows("adjectives")
        self.other = self.df_manager.count_rows("other")

        self.bad_vals_flag = bool(self.duplicates or self.nulls)

    def get_stats(self, mode: str) -> list[dict]:
        # Mode - type, score, bad_vals
        match mode:
            case "type": stats = [
                {"name": "Nouns", "count": int(self.nouns)},
                {"name": "Verbs", "count": int(self.verbs)},
                {"name": "Adjectives", "count": int(self.adjectives)},
                {"name": "Other", "count": int(self.other)}
            ]
            case "score": stats = [
                {"name": "Learned", "count": self.learnt},
                {"name": "New", "count": self.new},
                {"name": "Unlearned", "count": self.repeat}
            ]
            case "bad_vals": stats = [
                {"name": "Duplicates", "count": self.duplicates},
                {"name": "Nulls", "count": self.nulls},
            ]
        return stats