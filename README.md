# Vocabulary Booster v2

**Vocabulary Booster v2** is an upgraded version of [Vocabulary Booster](https://github.com/vovasko/german_vocabulary?tab=readme-ov-file) for translating and managing German vocabulary. Built with the [Flet](https://flet.dev) framework, it features a clean, responsive UI with improved navigation, a “Word of the Day” section to enhance daily learning, and a Statistics Card to track your vocabulary progress and integrity.

## Features

- 🔤 Translate individual German words using [Netzverb](https://www.verben.de)
- 📚 View and manage your vocabulary list with **sorting and filtering**
- 🌟 “Word of the Day” to reinforce regular practice
- 📈 Stats card showing progress and word distribution
- 🧠 Flashcard viewer with point-based learning system
- 🛠 Built-in **Settings view** to customize the experience
- 📌 Edit and delete existing records
- ❌ Detect and manage duplicate entries

> ⚠️ *Importing words from files is temporarily unavailable due to issues with Flet’s FilePicker.*  
> ❌ *The export feature has been removed in this version.*

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/vovasko/vocabulary-v2
    ```
2. Navigate to the project directory:
    ```sh
    cd german-vocabulary
    ```
3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Download the SpaCy language model:
    ```sh
    python -m spacy download de_core_news_sm
    ```

## Running the Application

For local (desktop) usage:
```sh
python main.py
```

For web mode using Flet:
```sh
flet run main.py --web
```

## Dependencies

- `flet >= 0.25.0`
- `pandas >= 2.0.0`
- `requests >= 2.31.0`
- `beautifulsoup4 >= 4.12.0`
- `spacy >= 3.7.0`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.