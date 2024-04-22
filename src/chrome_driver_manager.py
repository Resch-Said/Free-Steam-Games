import os
from zipfile import ZipFile

import requests


class ChromeDriverManager:
    windows_driver_url = "chromedriver_win32.zip"
    linux_driver_url = "chromedriver_linux64.zip"
    driver_url = None

    if os.name == "nt":
        driver_url = windows_driver_url
    elif os.name == "posix":
        driver_url = linux_driver_url

    @classmethod
    def download_driver(cls, version="0"):
        if version == "0":
            version = cls.get_latest_version()

        url = f"https://chromedriver.storage.googleapis.com/{version}/{cls.driver_url}"
        response = requests.get(url)

        with open(cls.driver_url, "wb") as f:
            f.write(response.content)
        with ZipFile(cls.driver_url, "r") as zip_ref:
            zip_ref.extractall("../driver/")
        with open("../driver/version.txt", "w") as f:
            f.write(version)

        os.remove(cls.driver_url)
        print(f"Driver version {version} downloaded and extracted")

    @classmethod
    def get_latest_version(cls):
        url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        response = requests.get(url)
        return response.text

    @classmethod
    def get_current_version(cls):
        if not os.path.exists("../driver/version.txt"):
            with open("../driver/version.txt", "w") as f:
                f.write("0")

        with open("../driver/version.txt", "r") as f:
            return f.read()

    @classmethod
    def check_new_version(cls):
        current_version = cls.get_current_version()
        latest_version = cls.get_latest_version()
        return current_version != latest_version

    @classmethod
    def main(cls):
        if cls.check_new_version():
            cls.download_driver()
        else:
            print("Driver is up to date")


if __name__ == "__main__":
    ChromeDriverManager.main()
