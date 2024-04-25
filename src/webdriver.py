import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from better_path import BetterPath
from exit_listener import ExitListener


class Webdriver:
    login_url = "https://store.steampowered.com/login/"
    steam_url = "https://store.steampowered.com/"

    browser_path = BetterPath.get_absolute_path(
        "../selenium/webdriver"
    )  # user-data-dir requires absolute path
    cookies_path = "../selenium/cookies.json"
    user_logged_in_id = "account_pulldown"

    service = webdriver.ChromeService(
        executable_path="/usr/bin/chromedriver"
    )  # For Linux

    @classmethod
    def load_chrome_driver(cls, hidden=False):
        driver = None

        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument(f"user-data-dir={cls.browser_path}")
        chrome_options.add_argument("--enable-chrome-browser-cloud-management")
        chrome_options.add_argument("--no-sandbox")

        if hidden:
            chrome_options.add_argument("--headless=new")

        if os.name == "nt":
            driver = webdriver.Chrome(options=chrome_options)
        elif os.name == "posix":
            driver = webdriver.Chrome(service=cls.service, options=chrome_options)
        else:
            print("OS not supported")
            ExitListener.set_exit_flag(True)

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
            # Wait until user is logged in
            element = WebDriverWait(driver, 600).until(
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

    @classmethod
    def check_if_user_is_logged_in(cls):
        driver = cls.load_chrome_driver(hidden=True)
        driver.get(cls.steam_url)
        try:
            driver.find_element(By.ID, cls.user_logged_in_id)
            print("User is logged in")
            return True
        except:
            return False
        finally:
            driver.quit()


if __name__ == "__main__":
    Webdriver.main()
