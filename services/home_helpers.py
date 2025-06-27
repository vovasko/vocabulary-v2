from services.settings import SettingsManager
from services.translator import Netzverb

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
                print("Getting new word")
                word = choice(words) # choose random word
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