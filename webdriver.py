import json
import os
import pathlib

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Webdriver:
    login_url = "https://store.steampowered.com/login/?redir=%3Fsnr%3D1_60_4__global-header&redir_ssl=1&snr=1_4_4__global-header"
    steam_url = "https://store.steampowered.com/"
    chrome_path = pathlib.Path(__file__).parent.absolute() / "chromedriver"
    user_logged_in_id = "account_pulldown"

    @classmethod
    def load_chrome_driver(cls):
        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument(f"user-data-dir={cls.chrome_path}")
        driver = webdriver.Chrome(options=chrome_options)
        cls.update_cookies(driver)  # Making sure cookies are up to date

        return driver

    @classmethod
    def get_steam_sessionid(cls):
        if os.path.isfile('cookies.json'):
            with open('cookies.json', 'r') as f:
                cookies = json.loads(f.read())
                for cookie in cookies:
                    if cookie['name'] == 'sessionid':
                        return cookie['value']
        return None

    @classmethod
    def get_cookies_steam_login_secure(cls):
        if os.path.isfile('cookies.json'):
            with open('cookies.json', 'r') as f:
                cookies = json.loads(f.read())
                for cookie in cookies:
                    if cookie['name'] == 'steamLoginSecure':
                        return cookie['value']
        return None

    @classmethod
    def create_steam_cookies(cls):
        driver = cls.load_chrome_driver()
        driver.get(cls.login_url)
        try:
            element = WebDriverWait(driver, 600).until(
                EC.presence_of_element_located((By.ID, cls.user_logged_in_id))  # Wait until user is logged in
            )
        finally:
            cls.update_cookies(driver)
            driver.quit()

    @classmethod
    def update_cookies(cls, driver):
        cookies = driver.get_cookies()
        with open('cookies.json', 'w') as f:
            f.write(json.dumps(cookies))


if __name__ == '__main__':
    Webdriver.create_steam_cookies()
    driver = Webdriver.load_chrome_driver()
    driver.get("https://store.steampowered.com/")
    driver.quit()
