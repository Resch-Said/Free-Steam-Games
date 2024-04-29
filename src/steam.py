import json
from time import sleep

import requests
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from exit_listener import ExitListener
from webdriver import Webdriver


class Steam:
    applist_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    appdetails_url = "https://store.steampowered.com/api/appdetails?appids="
    app_shop_url = "https://store.steampowered.com/app/"
    steam_url = "https://store.steampowered.com/"
    login_url = "https://store.steampowered.com/login/"

    rate_limit_retrying_time = 61  # Minutes.
    max_retries = 3

    in_library_class = "already_in_library"
    age_gate_class = "age_gate"
    user_logged_in_id = "account_pulldown"
    free_games_xpath = [
        f"//*[starts-with(@onclick, 'AddFreeLicense')]",
        f"/html/body/div[1]/div[7]/div[6]/div[3]/div[2]/div[1]/div[4]/div[2]/div[1]/div/div/div[2]/div/div/a",
    ]

    @classmethod
    def open_steam_login_page(cls):
        driver = Webdriver.load_chrome_driver()
        driver.get(cls.login_url)
        try:
            # Wait until user is logged in
            WebDriverWait(driver, 600).until(
                EC.presence_of_element_located((By.ID, cls.user_logged_in_id))
            )

        finally:
            driver.quit()

    @classmethod
    def check_if_user_is_logged_in(cls):
        driver = Webdriver.load_chrome_driver(hidden=True)
        driver.get(cls.steam_url)
        try:
            driver.find_element(By.ID, cls.user_logged_in_id)
            print("User is logged in")
            return True
        except NoSuchElementException:
            return False
        finally:
            driver.quit()

    @classmethod
    def get_apps(cls):
        """
        :return: Returns a dictionary with the appid as key and the appname as value
        """
        response = requests.get(cls.applist_url)
        data = json.loads(response.text.encode("utf-8"))

        app_dict = {app["appid"]: app["name"] for app in data["applist"]["apps"]}
        return app_dict

    @classmethod
    def activate_free_game(cls, appid):
        success = False

        driver = Webdriver.load_chrome_driver(hidden=True)

        cls.load_app_store(appid, driver)
        cls.auto_accept_age_gate(driver)

        for xpath in cls.free_games_xpath:
            try:
                driver.find_element(By.XPATH, xpath).click()
                break
            except NoSuchElementException:
                pass

        cls.load_app_store(appid, driver)
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
    def load_app_store(cls, appid, driver):

        try:
            driver.get(cls.app_shop_url + str(appid))
        except TimeoutException:
            print("TimeoutException occurred.")
            return False

    @classmethod
    def main(cls):
        from database import Database

        current_retry = 0

        database_apps = Database.get_free_games_to_redeem()
        for appid in database_apps:
            if ExitListener.get_exit_flag():
                break

            if Steam.activate_free_game(appid):
                print(f'Success in redeeming: "{database_apps[appid]}" ({appid})')
                Database.update_redeemed(appid, 1)
                current_retry = 0
            else:
                Database.update_redeemed(appid, 0)
                current_retry += 1
                print(
                    f'Failed to redeem "{database_apps[appid]} ({appid})": {current_retry}/{cls.max_retries}'
                )
                timer = cls.rate_limit_retrying_time

                while timer > 0 and current_retry >= cls.max_retries:
                    if ExitListener.get_exit_flag():
                        break
                    print(
                        f"Failed. Probably rate Limited. Taking a break: {timer} Minutes remaining"
                    )
                    sleep(60)  # 1 minute
                    timer -= 1

    @classmethod
    def auto_accept_age_gate(cls, driver):

        if not cls.age_gate_visible(driver):
            return

        driver.find_element(By.ID, "ageYear").send_keys("1900")
        driver.find_element(By.CLASS_NAME, "btnv6_blue_hoverfade").click()

        try:
            driver.find_element(By.ID, "ageYear")
            print("Failed to pass Age Gate.")
        except NoSuchElementException:
            print("Age Gate successfully passed.")

    @classmethod
    def age_gate_visible(cls, driver):
        try:
            driver.find_element(By.CLASS_NAME, cls.age_gate_class)
            return True
        except NoSuchElementException:
            return False


if __name__ == "__main__":
    Steam.main()
