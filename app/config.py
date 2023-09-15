import json, os

class Config:
    def __init__(self, fn="config.json"):
        self.fn = fn
        self.data = json.load(open(fn)) if os.path.isfile(fn) else {}

    def save(self):
        json.dump(self.data, open(self.fn, "w"), indent=4)

    def get(self, key, default=None):
        if key not in self.data:
            self[key] = default
        return self.data.get(key)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()

config = Config()