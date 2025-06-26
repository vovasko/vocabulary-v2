import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path
import spacy # python -m spacy download de_core_news_sm

class TranslationError(Exception):
    def __init__(self, message: str, found = True):
        self.message = str(message)
        self.found = found
        super().__init__(self.message)

class Netzverb: 
    # base_url = "https://www.verbformen.de/?w="
    base_url = "https://www.verben.de/?w="
    noun_url = "https://www.verben.de/substantive/?w=" # + word + .htm
    conj_url = "https://www.verben.de/konjunktionen/?w="
    # "https://www.verben.de/substantive/?w="

    nouns = ["der", "die", "das", "NOUN", "PROPN", "X"]
    verbs = ["VERB", "AUX"]
    adjectives = ["ADJ", "ADV"]

    @classmethod
    def get_html_response(self, word):
        request_url = f"{self.base_url}{word}"
        return self._fetch_response(request_url)

    @classmethod
    def get_noun_html_response(self, word):
        request_url = f"{self.noun_url}{word}"
        return self._fetch_response(request_url)
    
    @classmethod
    def get_conj_html_response(self, word):
        request_url = f"{self.conj_url}{word}"
        return self._fetch_response(request_url)

    @classmethod
    def _fetch_response(self, request_url):
        try:
            response = requests.get(request_url)
            response.raise_for_status()  # Raise HTTPError for bad responses
            time.sleep(1)
            return BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.RequestException as e:
            raise TranslationError(f"Failed to fetch URL")
        
    @classmethod # Check whether Netzverb has a page related to specific word
    def check_netz_presence(self, soup: BeautifulSoup):
        present = False
        if soup == None: pass

        if soup.find("h1", string=re.compile(r"^Definition")):
            present = True
        
        if not present: raise TranslationError("Word not found on Netzverb", False)

    @classmethod
    def get_translation(self, soup: BeautifulSoup, language):
        if not soup: return None
        dd = soup.find("dd", lang=language)
        if not dd: return None
        span = dd.find_all("span")[1]
        if not span: return None
        words = [word.strip() for word in span.text.split(",")]
        return ", ".join(words[:4])
    
    @classmethod
    def get_example(self, soup: BeautifulSoup, n: int):
        if soup == None: return None
        examples = []
        # Find all <a> tags with href attributes
        anchor_tags = soup.find_all("a", href=True)
        if not anchor_tags: return None
        for tag in anchor_tags:
            href = tag["href"]
            if href.startswith("https://www.satzapp.de/?t="):
                sentance = href.split("=")[1]
                examples.append(sentance)
        return "; ".join(examples[:n])
    
    @classmethod
    def get_meaning(self, soup: BeautifulSoup, n: int): # class=rBox rBoxWht
        if soup == None: return None
        list_prefixes = ("a.", "b.", "c.", "d.", "e.")
        meanings = []
        sections = soup.find_all("section", class_="rBox rBoxWht")
        if not sections: return None
        for section in sections:
            h2 = section.find("h2")
            if h2 and h2.text == "Bedeutungen":
                dl = section.find('dl', class_='wNrn')
                if dl:
                    dd_tags = dl.find_all('dd')
                    for dd in dd_tags:
                        text = dd.text.strip()
                        if text.startswith(list_prefixes):
                            text = text[2:]
                        for part in text.split(";"):
                            part = part.strip()  
                            if part:
                                meanings.append(part)
                    return "; ".join(meanings[:n])
    
    @classmethod
    def get_word(self, soup: BeautifulSoup):
        if soup == None: return None
        return soup.find("div", class_="rCntr rClear").text.strip()
    
    @classmethod
    def check_verb(self, soup: BeautifulSoup):
        if soup == None: return None
        section = soup.find_all("section", class_="rBox rBoxWht")[0]
        span = section.find_all("span", class_="rInf")[0]
        part = span.find_all("span", attrs={'title': "Verb"})
        if part:
            return(part[0].text.upper())

class Translator:
    def __init__(self):
        self.input_data = pd.Series()
        # columns=["type", "german", "translation", "second_translation", "example", "meaning", "score"]
        self.data = pd.DataFrame()
        
    def read_data(self, file):
        self.input_data = (pd.read_csv(file, header=None, names=["Input"])
                    .dropna()
                    .reset_index(drop=True))

    def noun_type(self, phrase):
        articles = ["der", "die", "das"]
        words = phrase.strip().split()
        if words[0].lower() in articles:
            article = words[0].lower()
            noun = " ".join(words[1:])
            return article, noun
        else:
            return None, phrase.strip()
    
    def word_type(self):
        nlp = spacy.load("de_core_news_sm", disable=["ner", "parser"])
        func = lambda x: nlp(x)[0].pos_
        self.data.type = self.data.type.fillna(self.data.german.apply(func))
        # print("Word type defined")

    def clean_data(self):
        cleaned_data = pd.DataFrame()
        cleaned_data[["type", "german"]] = self.input_data.apply(lambda x: pd.Series(self.noun_type(x)))
        self.input_data = pd.Series()
        self.data = pd.concat([self.data, cleaned_data])
        # print("Data cleaned")
        self.word_type()

    def output(self, file_name="vocabulary.csv"):
        out_location = Path(__file__).parent / file_name

        # Append if the file exists, otherwise write normally
        self.data.to_csv(
            out_location, 
            index=False, 
            mode="a" if out_location.exists() else "w", 
            header=not out_location.exists()
        )

        print(f"Translations saved to {out_location}")

    def get_netz_info(self, _settings: dict, progress_callback=None, callback = None):
        settings = _settings
        success_count = 0
        failed_words = []
        original_shape = self.data.shape[0]

        # Initialize columns dynamically        
        self.data["translation"] = None
        if settings["second_lang"]["lang"] != "None": 
            self.data["second_translation"] = None
        if settings["examples"]:
            self.data["example"] = None
        if settings["meanings"]: 
            self.data["meaning"] = None
        self.data["score"] = 0
        self.data["__drop__"] = False
        
        # create meaningful index
        self.data.index = range(len(self.data))

        def process_row(row):
            nonlocal success_count, failed_words
            word = row["german"]
            
            print(f"Parsing for {word}")
            if progress_callback: progress_callback(row.name + 1, self.data.shape[0])

            try:
                # Determine the correct Netzverb method
                if row["type"] in Netzverb.nouns:
                    soup = Netzverb.get_noun_html_response(word)
                elif row["type"] in ["CONJ", "CCONJ", "SCONJ"]:
                    soup = Netzverb.get_conj_html_response(word)
                else:
                    soup = Netzverb.get_html_response(word)

                # Skip processing if word is not present
                Netzverb.check_netz_presence(soup)

                # Get the base form and update German/Type columns
                base_form = Netzverb.get_word(soup)
                if base_form.find(",") != -1:
                    type_and_word = base_form.split(sep=',')
                    if len(type_and_word) > 2:
                        type_and_word = [type_and_word[0], type_and_word[2]]
                    row["german"], row["type"] = type_and_word
                    row["type"] = row["type"].strip()
                    row["german"] = row["german"].strip()
                        
                if row["type"] in Netzverb.verbs: 
                    base_form = Netzverb.get_word(soup)
                    if isinstance(base_form, str):
                        row["german"] = base_form

                # Fill translations and other data
                row["translation"] = Netzverb.get_translation(soup, settings["main_lang"]["code"])
                if "second_translation" in self.data.columns:
                    row["second_translation"] = Netzverb.get_translation(soup, settings["second_lang"]["code"])
                if "example" in self.data.columns:
                    row["example"] = Netzverb.get_example(soup, settings["examples"])
                if "meaning" in self.data.columns:
                    row["meaning"] = Netzverb.get_meaning(soup, settings["meanings"])
                    
                success_count += 1
            except TranslationError as te:
                if te.found == False: row["__drop__"] = True
                failed_words.append(f"{row['german']} ({te})")
            return row

        # Apply processing function to all rows
        self.data = self.data.apply(process_row, axis=1)
        # Delete bad values from df
        self.data = self.data[self.data["__drop__"] != True]
        self.data = self.data.drop(columns="__drop__")

        if callback: 
            callback(success = True, data={
                "success_count": success_count,
                "words_count"  : original_shape,
                "failed_words" : failed_words
            })


if __name__ == "__main__":
    pass

# === Tasks left to do: === 
# Create TextField and collect data from it
# Create file picking and loading functionality
# Create word of the day function in Netzverb and place to store it in settings
# Create function to check connection to the website
# Fill unsuccessful translations with data of one kind
# Save translated data to the db
# Display translated data on the translation view (maybe display input words and then append information about them)