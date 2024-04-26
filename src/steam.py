import json
from time import sleep

import requests
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from exit_listener import ExitListener
from webdriver import Webdriver


class Steam:
    applist_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    appdetails_url = "https://store.steampowered.com/api/appdetails?appids="
    steam_app_url = "https://store.steampowered.com/app/"
    free_license_url = "https://store.steampowered.com/freelicense/addfreelicense/"
    rate_limit_retrying_time = 61  # Minutes.
    max_retries = 3

    timeout_exception_retrying_time = 60  # Seconds.

    in_library_class = "already_in_library"
    age_gate_class = "age_gate"
    free_games_xpath = [
        f"//*[starts-with(@onclick, 'AddFreeLicense')]",
        f"/html/body/div[1]/div[7]/div[6]/div[3]/div[2]/div[1]/div[4]/div[2]/div[1]/div/div/div[2]/div/div/a",
    ]

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
    def activate_free_game(cls, appid):
        success = False

        driver = Webdriver.load_chrome_driver(hidden=True)

        cls.wait_until_website_reachable(appid, driver)
        cls.auto_accept_age_gate(driver)

        for xpath in cls.free_games_xpath:
            try:
                driver.find_element(By.XPATH, xpath).click()
                break
            except NoSuchElementException:
                pass

        cls.wait_until_website_reachable(appid, driver)
        cls.auto_accept_age_gate(driver)

        if cls.already_owned(driver):
            success = True

        driver.quit()
        return success

    @classmethod
    def already_owned(cls, driver):
        try:
            driver.find_element(By.CLASS_NAME, cls.in_library_class)
            return True
        except NoSuchElementException:
            return False

    @classmethod
    def wait_until_website_reachable(cls, appid, driver):
        is_website_reachable = False

        while not is_website_reachable:
            if ExitListener.get_exit_flag():
                break

            try:
                driver.get(cls.steam_app_url + str(appid))
                is_website_reachable = True
            except TimeoutException:
                print("TimeoutException occurred")
                sleep(cls.timeout_exception_retrying_time)

    @classmethod
    def main(cls):
        from database import Database

        current_retry = 0

        appids, appnames = Database.get_free_games_to_redeem()
        for appid in appids:
            if ExitListener.get_exit_flag():
                break

            print(f"Redeeming: {appnames[appids.index(appid)]} ({appid})")
            if Steam.activate_free_game(appid):
                print("Success")
                Database.update_redeemed(appid, 1)
            else:
                Database.update_redeemed(appid, 0)
                current_retry += 1
                print(f"Failed: {current_retry}/{cls.max_retries}")
                timer = cls.rate_limit_retrying_time

                while timer > 0 and current_retry >= cls.max_retries:
                    if ExitListener.get_exit_flag():
                        break
                    print(
                        f"Failed. Probably rate Limited. Taking a break: {timer} Minutes remaining",
                        end="\r",
                    )
                    sleep(60)  # 1 minute
                    timer -= 1

                if timer <= 0:
                    current_retry = 0

    @classmethod
    def auto_accept_age_gate(cls, driver):
        age_check_passed = False

        if not cls.age_gate_visible(driver):
            return

        driver.find_element(By.ID, "ageYear").send_keys("1900")
        driver.find_element(By.CLASS_NAME, "btnv6_blue_hoverfade").click()

        # Wait until next page is loaded

        while not age_check_passed:
            try:
                driver.find_element(By.CLASS_NAME, "game_area_purchase_game ")
                age_check_passed = True
            except NoSuchElementException:
                sleep(1)

    @classmethod
    def age_gate_visible(cls, driver):
        try:
            driver.find_element(By.CLASS_NAME, cls.age_gate_class)
            return True
        except NoSuchElementException:
            return False


if __name__ == "__main__":
    Steam.main()
