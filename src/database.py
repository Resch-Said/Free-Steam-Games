import json
import sqlite3
from datetime import datetime
from json import JSONDecodeError
from time import sleep

import requests

from better_path import BetterPath
from exit_listener import ExitListener
from steam import Steam
from webdriver import Webdriver


class Database:
    BetterPath.create_path("../database")

    con = sqlite3.connect("../database" + "/steam.db")
    cur = con.cursor()
    app_detail_url = "https://store.steampowered.com/api/appdetails?appids="
    app_detail_retrying_time = 180  # Seconds

    @classmethod
    def create_database(cls):
        cls.cur.execute(
            "CREATE TABLE IF NOT EXISTS apps (appID INTEGER PRIMARY KEY, name TEXT, type TEXT, main_game_id INTEGER, success INTEGER, is_free INTEGER,"
            "subID INTEGER,is_redeemed INTEGER DEFAULT (0), last_update TEXT)"
        )
        cls.con.commit()

    @classmethod
    def get_apps(cls):
        cls.cur.execute("SELECT appID, name FROM apps")
        apps = cls.cur.fetchall()
        return dict(apps)

    @classmethod
    def get_app_ids_to_update(cls):
        # Only update games, dlcs and entries that have not been updated yet
        cls.cur.execute(
            'SELECT appID FROM apps WHERE is_redeemed = 0 and type = "game" or type = "dlc" or (type is null and last_update is null) ORDER BY last_update ASC'
        )

        appids = cls.cur.fetchall()
        appids = [app[0] for app in appids]
        return appids

    @classmethod
    def add_new_apps_to_database(cls):
        steam_apps = Steam.get_apps()
        database_apps = cls.get_apps()

        # Apps that changed their names since the last update
        conflicting_apps = {
            appid: appname
            for appid, appname in steam_apps.items()
            if appid in database_apps and appname != database_apps[appid]
        }
        for appid, appname in conflicting_apps.items():
            print(f"Name of {appid} changed from {database_apps[appid]} to {appname}")
            cls.cur.execute(
                "DELETE FROM apps WHERE appID = ?",
                (appid,),
            )

        # Apps that are not in the database
        new_apps = list(steam_apps.keys() - database_apps.keys())

        for appid in new_apps:
            print(f"Adding {appid} to the database")
            cls.cur.execute(
                "INSERT OR IGNORE INTO apps (appID, name)VALUES (?, ?)",
                (appid, steam_apps[appid]),
            )

        print("Committing changes")
        cls.con.commit()

    @classmethod
    def update_app_detail(cls, appid):
        url = cls.app_detail_url + str(appid)

        response_success = False

        while not response_success:
            response = requests.get(url)

            try:
                data = json.loads(response.text)
                data_success = data[str(appid)]["success"]
                response_success = True
            except TypeError:
                print(
                    f"Error in retrieving {appid}. Response was: {response.text} Retrying in {cls.app_detail_retrying_time} seconds"
                )
                sleep(cls.app_detail_retrying_time)
            except JSONDecodeError:
                print(
                    f"Error in retrieving {appid}. JSONDecodeError Retrying in {cls.app_detail_retrying_time} seconds"
                )
                sleep(cls.app_detail_retrying_time)

        app_type = None

        try:
            appname = data[str(appid)]["data"]["name"]
            print(f"Updating {appname} ({appid})", end="")
            cls.cur.execute(
                "UPDATE apps SET name = ? WHERE appID = ?", (appname, appid)
            )
        except KeyError:
            pass

        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cls.cur.execute(
            "UPDATE apps SET last_update = ? WHERE appID = ?",
            (current_date_time, appid),
        )
        cls.cur.execute(
            "UPDATE apps SET success = ? WHERE appID = ?", (data_success, appid)
        )

        try:
            app_type = data[str(appid)]["data"]["type"]
            cls.cur.execute(
                "UPDATE apps SET type = ? WHERE appID = ?", (app_type, appid)
            )
        except KeyError:
            pass

        try:
            is_free = data[str(appid)]["data"]["is_free"]
            cls.cur.execute(
                "UPDATE apps SET is_free = ? WHERE appID = ?", (is_free, appid)
            )

            if is_free and (app_type == "game" or app_type == "dlc"):
                subid = Steam.get_subid(appid)

                if subid == -1:
                    cls.cur.execute(
                        "UPDATE apps SET is_redeemed = ? WHERE appID = ?", (1, appid)
                    )
                cls.cur.execute(
                    "UPDATE apps SET subID = ? WHERE appID = ?", (subid, appid)
                )
        except KeyError:
            pass

        try:
            main_game_id = data[str(appid)]["data"]["fullgame"]["appid"]
            cls.cur.execute(
                "UPDATE apps SET main_game_id = ? WHERE appID = ?",
                (main_game_id, appid),
            )
        except KeyError:
            pass

        cls.con.commit()

    @classmethod
    def update_app_redeemed(cls, appid):
        cls.cur.execute("UPDATE apps SET is_redeemed = ? WHERE appID = ?", (1, appid))
        cls.con.commit()

    @classmethod
    def get_free_games_to_redeem(cls):
        """
        :return: Returns a tuple containing three lists\n
        [0] app_ids\n
        [1] sub_ids\n
        [2] app_names
        """
        cls.cur.execute(
            """
            SELECT appID, subID, name 
            FROM apps 
            WHERE is_free = 1 
            AND is_redeemed = 0 
            AND subID is not null 
            AND (type is "game" or type is "dlc")
            AND (main_game_id is null or main_game_id IN (SELECT appID FROM apps WHERE is_redeemed = 1))
            """
        )
        response = cls.cur.fetchall()
        appids = [app[0] for app in response]
        subids = [app[1] for app in response]
        appnames = [app[2] for app in response]
        return appids, subids, appnames

    @classmethod
    def main(cls):
        Webdriver.create_steam_cookies()

        cls.create_database()
        cls.add_new_apps_to_database()
        appids = cls.get_app_ids_to_update()
        for index, appid in enumerate(appids):
            if ExitListener.get_exit_flag():
                break

            cls.update_app_detail(appid)
            remaining_apps = len(appids) - index
            print(":\t" + f" {remaining_apps} apps left to update")
        cls.con.close()


if __name__ == "__main__":
    Database.main()
