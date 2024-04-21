import json
import sqlite3
from datetime import datetime
from time import sleep
import requests
from steam import Steam
from webdriver import Webdriver


class Database:
    con = sqlite3.connect('steam_free_games.db')
    cur = con.cursor()
    app_detail_url = "https://store.steampowered.com/api/appdetails?appids="

    @classmethod
    def create_database(cls):
        cls.cur.execute(
            "CREATE TABLE IF NOT EXISTS apps (appID INTEGER PRIMARY KEY, name TEXT, type TEXT, success INTEGER,is_free INTEGER,"
            "subID INTEGER,is_redeemed INTEGER DEFAULT (0), last_update TEXT)")
        cls.con.commit()

    @classmethod
    def get_app_ids_to_update(cls):
        # Only update games, dlcs and entries that have not been updated yet
        cls.cur.execute(
            "SELECT appID FROM apps WHERE is_redeemed = 0 and type = \"game\" or type = \"dlc\" or (type is null and last_update is null) ORDER BY last_update ASC")

        appids = cls.cur.fetchall()
        appids = [app[0] for app in appids]
        return appids

    @classmethod
    def remove_outdated_apps(cls):
        appids = cls.get_app_ids_to_update()
        steam_appids = Steam.get_app_list()[0]

        for appid in appids:
            print(f"Checking if {appid} is still existing")
            if appid not in steam_appids:
                print(f"Removing {appid}")
                cls.cur.execute("DELETE FROM apps WHERE appID = ?", (appid,))
        print("Committing changes")
        cls.con.commit()

    @classmethod
    def add_new_apps_to_database(cls):

        appids, appnames = Steam.get_app_list()

        for appid, appname in zip(appids, appnames):
            print(f"Checking {appname} ({appid})")
            cls.cur.execute(
                "INSERT OR IGNORE INTO apps (appID, name)VALUES (?, ?)", (appid, appname))
        print("Committing changes")
        cls.con.commit()

    @classmethod
    def update_app_detail(cls, appid):
        url = cls.app_detail_url + str(appid)

        response_success = False

        while not response_success:
            response = requests.get(url)
            data = json.loads(response.text)

            try:
                data_success = data[str(appid)]['success']
                response_success = True
            except TypeError:
                print(f"Error in retrieving {appid}. Retrying in 70 seconds")
                sleep(70)

        app_type = None

        try:
            appname = data[str(appid)]['data']['name']
            print(f"Updating {appname} ({appid})")
            cls.cur.execute(
                "UPDATE apps SET name = ? WHERE appID = ?", (appname, appid))
        except KeyError:
            pass

        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cls.cur.execute(
            "UPDATE apps SET last_update = ? WHERE appID = ?", (current_date_time, appid))
        cls.cur.execute(
            "UPDATE apps SET success = ? WHERE appID = ?", (data_success, appid))

        try:
            app_type = data[str(appid)]['data']['type']
            cls.cur.execute(
                "UPDATE apps SET type = ? WHERE appID = ?", (app_type, appid))
        except KeyError:
            pass

        try:
            is_free = data[str(appid)]['data']['is_free']
            cls.cur.execute(
                "UPDATE apps SET is_free = ? WHERE appID = ?", (is_free, appid))

            if is_free and app_type != "demo":
                subid = Steam.get_subid(appid)

                if subid == -1:
                    cls.cur.execute(
                        "UPDATE apps SET is_redeemed = ? WHERE appID = ?", (1, appid))
                cls.cur.execute(
                    "UPDATE apps SET subID = ? WHERE appID = ?", (subid, appid))
        except KeyError:
            pass

        cls.con.commit()

    @classmethod
    def update_app_redeemed(cls, appid):
        cls.cur.execute(
            "UPDATE apps SET is_redeemed = ? WHERE appID = ?", (1, appid))
        cls.con.commit()

    @classmethod
    def get_free_games_to_redeem(cls):
        """
        :return: Returns a tuple containing two lists\n
        [0] sub_ids\n
        [1] app_names
        """
        cls.cur.execute(  # TODO: We need to associate games with their dlcs and music to avoid redeeming them if the main game is not redeemed
            "SELECT appID, subID, name FROM apps WHERE is_free = 1 AND is_redeemed = 0 and subID is not null and type is \"game\"")
        response = cls.cur.fetchall()
        appids = [app[0] for app in response]
        subids = [app[1] for app in response]
        appnames = [app[2] for app in response]
        return appids, subids, appnames

    @classmethod
    def main(cls):
        cls.create_database()
        cls.remove_outdated_apps()
        cls.add_new_apps_to_database()
        appids = cls.get_app_ids_to_update()
        for appid in appids:
            cls.update_app_detail(appid)
        cls.con.close()


# TODO: Allow an easy way to stop the script
if __name__ == '__main__':
    Webdriver.create_steam_cookies()
    Database.main()
