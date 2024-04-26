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

    # con = sqlite3.connect("../database" + "/steam.db")
    # cur = con.cursor()
    app_detail_url = "https://store.steampowered.com/api/appdetails?appids="
    app_detail_retrying_time = 60 * 4  # Seconds

    @classmethod
    def create_database(cls):
        con, cur = cls.get_connection()

        cur.execute(
            "CREATE TABLE IF NOT EXISTS apps (appID INTEGER PRIMARY KEY, name TEXT, "
            "type TEXT, main_game_id INTEGER, success INTEGER, is_free INTEGER,"
            "is_redeemed INTEGER DEFAULT (0), redeem_failed INTEGER DEFAULT(0), last_update TEXT)"
        )
        con.commit()
        con.close()

    @classmethod
    def get_connection(cls):
        con = sqlite3.connect("../database" + "/steam.db")
        cur = con.cursor()
        return con, cur

    @classmethod
    def get_apps(cls):
        con, cur = cls.get_connection()

        cur.execute("SELECT appID, name FROM apps")
        apps = cur.fetchall()
        con.close()
        return dict(apps)

    @classmethod
    def get_app_ids_to_update(cls):
        con, cur = cls.get_connection()

        # Only update games, dlcs and entries that have not been updated yet
        cur.execute(
            "SELECT appID FROM apps "
            'WHERE is_redeemed = 0 and (type = "game" or type = "dlc") or (type is null and last_update is null) '
            "ORDER BY last_update ASC"
        )

        appids = cur.fetchall()
        appids = [app[0] for app in appids]

        con.close()
        return appids

    @classmethod
    def get_apps_not_in_database(cls, steam_apps, database_apps):
        new_apps = steam_apps.keys() - database_apps.keys()
        return new_apps

    @classmethod
    def get_conflicting_apps(cls, steam_apps, database_apps):
        """
        :param steam_apps:
        :param database_apps:
        :return: dict of appid and appname that are in the database but have a different name in the steam_apps
        """
        return {
            appid: appname
            for appid, appname in steam_apps.items()
            if appid in database_apps and appname != database_apps[appid]
        }

    @classmethod
    def add_new_apps_to_database(cls, steam_apps, database_apps):
        new_apps = cls.get_apps_not_in_database(steam_apps, database_apps)

        con, cur = cls.get_connection()

        for appid in new_apps:
            if ExitListener.get_exit_flag():
                break

            print(f"Adding {appid} to the database")
            cur.execute(
                "INSERT OR IGNORE INTO apps (appID, name)VALUES (?, ?)",
                (appid, steam_apps[appid]),
            )

        print("Committing changes")
        con.commit()
        con.close()

    @classmethod
    def update_app_detail(cls, appid):
        url = cls.app_detail_url + str(appid)

        response_success = False
        data = None
        data_success = None
        con, cur = cls.get_connection()

        while not response_success:
            response = requests.get(url)

            try:
                data = json.loads(response.text)
                data_success = data[str(appid)]["success"]
                response_success = True
            except TypeError:
                print(
                    f"Error in retrieving {appid}. Response was: {response.text} Retrying in "
                    f"{cls.app_detail_retrying_time} seconds"
                )
                sleep(cls.app_detail_retrying_time)
            except JSONDecodeError:
                print(
                    f"Error in retrieving {appid}. JSONDecodeError Retrying in {cls.app_detail_retrying_time} seconds"
                )
                sleep(cls.app_detail_retrying_time)

        # Update the name of the app
        try:
            appname = data[str(appid)]["data"]["name"]
            print(f"Updating {appname} ({appid})", end="")
            cur.execute("UPDATE apps SET name = ? WHERE appID = ?", (appname, appid))
        except KeyError:
            pass

        # Update the last update time and success
        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "UPDATE apps SET last_update = ? WHERE appID = ?",
            (current_date_time, appid),
        )
        cur.execute(
            "UPDATE apps SET success = ? WHERE appID = ?", (data_success, appid)
        )

        # Update the type of the app
        try:
            app_type = data[str(appid)]["data"]["type"]
            cur.execute("UPDATE apps SET type = ? WHERE appID = ?", (app_type, appid))
        except KeyError:
            pass

        # Update is_free
        try:
            is_free = data[str(appid)]["data"]["is_free"]
            cur.execute("UPDATE apps SET is_free = ? WHERE appID = ?", (is_free, appid))

        except KeyError:
            pass

        # Update main_game_id
        try:
            main_game_id = data[str(appid)]["data"]["fullgame"]["appid"]
            cur.execute(
                "UPDATE apps SET main_game_id = ? WHERE appID = ?",
                (main_game_id, appid),
            )
        except KeyError:
            pass

        con.commit()
        con.close()

    @classmethod
    def update_redeemed(cls, appid, success):
        con, cur = cls.get_connection()

        cur.execute(
            "UPDATE apps SET is_redeemed = ?, redeem_failed = ? WHERE appID = ?",
            (success, not success, appid),
        )
        con.commit()
        con.close()

    @classmethod
    def get_free_games_to_redeem(cls):
        """
        :return: Returns a tuple containing three lists\n
        [0] app_ids\n
        [1] app_names
        """
        con, cur = cls.get_connection()

        cur.execute(
            """
            SELECT appID, name 
            FROM apps 
            WHERE is_free = 1 
            AND is_redeemed = 0 
            AND (type is "game" or type is "dlc")
            AND (main_game_id is null or main_game_id IN (SELECT appID FROM apps WHERE is_redeemed = 1))
            """
        )
        response = cur.fetchall()
        appids = [app[0] for app in response]
        appnames = [app[1] for app in response]

        con.close()
        return appids, appnames

    @classmethod
    def main(cls):

        if not Webdriver.check_if_user_is_logged_in():
            Webdriver.open_steam_login_page()
        cls.create_database()

        steam_apps = Steam.get_apps()
        database_apps = cls.get_apps()

        cls.add_new_apps_to_database(steam_apps, database_apps)
        cls.update_conflicting_apps(steam_apps, database_apps)

        appids = cls.get_app_ids_to_update()
        for index, appid in enumerate(appids):
            if ExitListener.get_exit_flag():
                break

            cls.update_app_detail(appid)
            remaining_apps = len(appids) - index
            print(":\t" + f" {remaining_apps} apps left to update")

    @classmethod
    def update_conflicting_apps(cls, steam_apps, database_apps):
        conflicting_apps = cls.get_conflicting_apps(steam_apps, database_apps)
        con, cur = cls.get_connection()

        for appid, appname in conflicting_apps.items():
            if ExitListener.get_exit_flag():
                break

            print(f"Name of {appid} changed from {database_apps[appid]} to {appname}")

            # Delete old entry and add as a new one.
            cur.execute("DELETE FROM apps WHERE appID = ?", (appid,))
            cur.execute(
                "INSERT OR IGNORE INTO apps (appID, name)VALUES (?, ?)",
                (appid, appname),
            )

        con.commit()
        con.close()


if __name__ == "__main__":
    Database.main()
