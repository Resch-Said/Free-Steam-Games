import json

import requests
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver import Webdriver


class Steam:
    applist_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    appdetails_url = "https://store.steampowered.com/api/appdetails?appids="
    steam_app_url = "https://store.steampowered.com/app/"
    free_license_url = "https://store.steampowered.com/freelicense/addfreelicense/"

    @classmethod
    def get_app_list(cls):
        response = requests.get(cls.applist_url)
        data = json.loads(response.text)

        app_ids = [app['appid'] for app in data['applist']['apps']]
        app_names = [app['name'] for app in data['applist']['apps']]
        return app_ids, app_names

    @classmethod
    def get_app_details(cls, appid):
        response = requests.get(cls.appdetails_url + str(appid))
        data = json.loads(response.text)

        if not data[str(appid)]['success']:
            return None

        return data[str(appid)]['data']

    @classmethod
    def get_subid(cls, appid):
        subid = None
        driver = Webdriver.load_chrome_driver()
        driver.get(cls.steam_app_url + str(appid))

        try:
            if driver.find_element(By.CLASS_NAME, "already_in_library"):
                print("Already owned")
                return None
        except NoSuchElementException:
            pass

        try:
            subid = \
                driver.find_element(By.CLASS_NAME, "btn_blue_steamui").get_attribute("onclick").split(",")[0].split(
                    " ")[1]
        finally:
            pass

            driver.quit()
            return subid

    @classmethod
    def activate_free_game(cls, subid):
        sessionid = Webdriver.get_steam_sessionid()

        if Webdriver.get_cookies_steam_login_secure() is None:
            Webdriver.create_steam_cookies()

        url = cls.free_license_url + str(subid)

        steam_login_secure = Webdriver.get_cookies_steam_login_secure()
        headers = {
            "accept": "*/*",
            "accept-language": "de,de-DE;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cookie": f"sessionid={sessionid}; steamLoginSecure={steam_login_secure}",
        }
        data = {
            "ajax": "true",
            "sessionid": {sessionid}
        }
        response = requests.post(url, headers=headers, data=data)
        print(response.text)


if __name__ == "__main__":
    print(Steam.get_subid(1782210))
