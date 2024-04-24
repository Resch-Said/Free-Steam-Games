import json
from time import sleep

import requests
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from exit_listener import ExitListener
from webdriver import Webdriver


class Steam:
    applist_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    appdetails_url = "https://store.steampowered.com/api/appdetails?appids="
    steam_app_url = "https://store.steampowered.com/app/"
    free_license_url = "https://store.steampowered.com/freelicense/addfreelicense/"
    rate_limit_retrying_time = 61  # Minutes.

    @classmethod
    def get_apps(cls):
        """
        :return: Returns a dictionary with the appid as key and the appname as value
        """
        response = requests.get(cls.applist_url)
        data = json.loads(response.text)

        app_dict = {app["appid"]: app["name"] for app in data["applist"]["apps"]}
        return app_dict

    @classmethod
    def get_app_details(cls, appid):
        response = requests.get(cls.appdetails_url + str(appid))
        data = json.loads(response.text)

        if not data[str(appid)]["success"]:
            return None

        return data[str(appid)]["data"]

    @classmethod
    def get_subid(cls, appid):
        """
        :param appid:
        :return: Returns the subid.
            If the game is already owned, it returns -1.
            If the game is not free, it returns None
        """
        subid = None
        driver = Webdriver.load_chrome_driver(hidden=True)
        driver.get(cls.steam_app_url + str(appid))

        try:
            if driver.find_element(By.CLASS_NAME, "already_in_library"):
                print(" Already owned. Can't retrive subid")
                subid = -1
        except NoSuchElementException:
            pass

        try:
            subid = (
                driver.find_element(
                    By.XPATH, "//*[starts-with(@onclick, 'AddFreeLicense')]"
                )
                .get_attribute(
                    # Extracts the subid from the onclick attribute
                    "onclick"
                )
                .split(",")[0]
                .split(" ")[1]
            )
        except NoSuchElementException:
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
        data = {"ajax": "true", "sessionid": {sessionid}}
        response = requests.post(url, headers=headers, data=data)
        sleep(5)
        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False

    @classmethod
    def main(cls):
        from database import Database

        appids, subids, appnames = Database.get_free_games_to_redeem()
        for subid in subids:
            if ExitListener.get_exit_flag():
                break

            print(f"Redeeming: {appnames[subids.index(subid)]} ({subid})")
            if Steam.activate_free_game(subid):
                print("Success")
                Database.update_app_redeemed(appids[subids.index(subid)])
            else:
                timer = cls.rate_limit_retrying_time
                while timer > 0:
                    if ExitListener.get_exit_flag():
                        break

                    print(
                        f"Failed. Probably rate Limited. Taking a break: {timer} Minutes remaining",
                        end="\r",
                    )
                    sleep(60)
                    timer -= 1


if __name__ == "__main__":
    Steam.main()
