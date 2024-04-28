import json


class Settings:
    @classmethod
    def get_database_version(cls):
        with open("../settings.json", "r") as f:
            data = json.load(f)
            return data["database"]["version"]

    @classmethod
    def get_software_version(cls):
        with open("../settings.json", "r") as f:
            data = json.load(f)
            return data["software"]["version"]


print(Settings.get_database_version())
print(Settings.get_software_version())
