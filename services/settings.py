from json import load, dump
from pathlib import Path

class SettingsManager:
    def __init__(self):
        self.file_path = Path(__file__).parent.parent / "config/settings.json"
        self._data = self._load()

    def _load(self):
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                print("Settings loaded")
                return load(f)
        print("Failed to load settings")
        return {}

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            dump(self._data, f, indent=4)

    def get(self, key, default=None):
        parts = key.split(".")
        d = self._data
        for part in parts:
            if isinstance(d, dict) and part in d:
                d = d[part]
            else: return default
        return d

    def set(self, key, value):
        parts = key.split(".")
        d = self._data
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = value

    @property
    def data(self):
        return self._data