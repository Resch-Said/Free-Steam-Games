import json
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from selenium import webdriver
from better_path import BetterPath


class Webdriver:
    login_url = "https://store.steampowered.com/login/"
    steam_url = "https://store.steampowered.com/"

    browser_path = BetterPath.get_absolute_path("../selenium/webdriver")
    cookies_path = "../selenium/cookies.json"
    user_logged_in_id = "account_pulldown"

    @classmethod
    def load_chrome_driver(cls, hidden=False):
        chrome_driver_path = None

        if os.name == "nt":
            chrome_driver_path = "../driver/chromedriver.exe"

        elif os.name == "posix":
            chrome_driver_path = "../driver/chromedriver"

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = chrome_driver_path

        chrome_options.add_argument(f"user-data-dir={cls.browser_path}")
        chrome_options.add_argument("--enable-chrome-browser-cloud-management")
        chrome_options.add_argument("--no-sandbox")

        if hidden:
            chrome_options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=chrome_options)
        cls.update_cookies(driver)  # Making sure cookies are up to date
        return driver

    @classmethod
    def get_steam_sessionid(cls):
        if os.path.isfile(cls.cookies_path):
            with open(cls.cookies_path, "r") as f:
                cookies = json.loads(f.read())
                for cookie in cookies:
                    if cookie["name"] == "sessionid":
                        return cookie["value"]
        return None

    @classmethod
    def get_cookies_steam_login_secure(cls):
        if os.path.isfile(cls.cookies_path):
            with open(cls.cookies_path, "r") as f:
                cookies = json.loads(f.read())
                for cookie in cookies:
                    if cookie["name"] == "steamLoginSecure":
                        return cookie["value"]
        return None

    @classmethod
    def create_steam_cookies(cls):
        driver = cls.load_chrome_driver()
        driver.get(cls.login_url)
        try:
            element = WebDriverWait(driver, 600).until(
                # Wait until user is logged in
                EC.presence_of_element_located((By.ID, cls.user_logged_in_id))
            )
        finally:
            cls.update_cookies(driver)
            driver.quit()

    @classmethod
    def update_cookies(cls, driver):
        cookies = driver.get_cookies()
        with open(cls.cookies_path, "w") as f:
            f.write(json.dumps(cookies))

    @classmethod
    def main(cls):
        Webdriver.create_steam_cookies()
        driver = Webdriver.load_chrome_driver()
        driver.get("https://store.steampowered.com/")
        driver.quit()


if __name__ == "__main__":
    Webdriver.main()
