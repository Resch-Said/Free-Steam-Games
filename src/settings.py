import json


class Settings:
    @classmethod
    def get_version(cls):
        with open("../settings.json", "r") as f:
            data = json.load(f)
            return data["database"]["version"]


print(Settings.get_version())
