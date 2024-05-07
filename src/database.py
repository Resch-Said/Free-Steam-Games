import json
import os
import sqlite3
import threading
from contextlib import closing
from datetime import datetime
from json import JSONDecodeError
from time import sleep

import requests

from better_path import BetterPath
from exit_listener import ExitListener
from logger import Logger
from settings import Settings
from steam import Steam


class Database:
    lock = threading.Lock()
    version = Settings.get_database_version()

    BetterPath.create_path("../database")
    db_path = "../database/steam.db"
    prebuilt_db_path = "../database/prebuilt.db"

    app_detail_url = "https://store.steampowered.com/api/appdetails?appids="
    app_detail_retrying_time = 60 * 4  # Seconds

    @staticmethod
    def get_connection(path=db_path):
        return sqlite3.connect(path)

    @classmethod
    def execute_sql(cls, sql, values=None, many=False, db_path=db_path):
        with cls.lock:
            with closing(cls.get_connection(db_path)) as con:
                with closing(con.cursor()) as cur:
                    if many:
                        cur.executemany(sql, values)
                    elif values:
                        cur.execute(sql, values)
                    else:
                        cur.execute(sql)

                    if sql.strip().upper().startswith("SELECT"):
                        return cur.fetchall()
                    else:
                        con.commit()

    @classmethod
    def create_database(cls):
        cls.execute_sql(
            "CREATE TABLE IF NOT EXISTS apps (appID INTEGER PRIMARY KEY, name TEXT, "
            "type TEXT, main_game_id INTEGER, success INTEGER, is_free INTEGER,"
            "is_redeemed INTEGER DEFAULT (0), redeem_failed INTEGER DEFAULT(0), last_update TEXT)"
        )
        cls.create_version_table()

    @classmethod
    def get_apps(cls):
        apps = cls.execute_sql("SELECT appID, name FROM apps")
        return dict(apps)

    @classmethod
    def get_appids_to_update(cls):

        # Only update games, dlcs and entries that have not been updated yet
        appids = cls.execute_sql(
            'SELECT appID from apps WHERE is_redeemed = 0 and (type = "game" or type = "dlc") or (type is null and ('
            'last_update is null or last_update = "0")) ORDER BY last_update ASC LIMIT 1000'
        )

        appids = [app[0] for app in appids]
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
        conflicting_apps = {}

        for database_app in database_apps:
            if database_app in steam_apps:
                if steam_apps[database_app] != database_apps[database_app]:
                    conflicting_apps[database_app] = steam_apps[database_app]
        return conflicting_apps

    @classmethod
    def add_new_apps_to_database(cls, steam_apps, database_apps):
        new_apps = cls.get_apps_not_in_database(steam_apps, database_apps)
        apps_data = [(appid, steam_apps[appid]) for appid in new_apps]

        if ExitListener.get_exit_flag():
            return

        Logger.write_log(f"Adding new apps to the database")

        cls.execute_sql(
            "INSERT OR IGNORE INTO apps (appID, name)VALUES (?, ?)",
            apps_data,
            many=True,
        )

        Logger.write_log(f"Added {len(new_apps)} new apps to the database")

    @classmethod
    def update_app_detail(cls, appid):
        url = cls.app_detail_url + str(appid)

        response_success = False
        data = None
        data_success = None

        while not response_success:
            if ExitListener.get_exit_flag():
                return None

            response = requests.get(url)

            try:
                data = json.loads(response.text)
                data_success = data[str(appid)]["success"]
                response_success = True
            except TypeError:

                Logger.write_log(
                    f"Error in retrieving {appid}. Response was: {response.text} Retrying in "
                    f"{cls.app_detail_retrying_time} seconds"
                )

                retrying_time = cls.app_detail_retrying_time

                while retrying_time > 0:
                    if ExitListener.get_exit_flag():
                        return None

                    sleep(1)
                    retrying_time -= 1

            except JSONDecodeError:

                Logger.write_log(
                    f"Error in retrieving {appid}. JSONDecodeError. Response was: {response.text}. Skipping"
                )
                return None

        # Update the last update time and success
        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cls.execute_sql(
            "UPDATE apps SET last_update = ? WHERE appID = ?",
            (current_date_time, appid),
        )

        cls.execute_sql(
            "UPDATE apps SET success = ? WHERE appID = ?", (data_success, appid)
        )

        # Update the type of the app
        try:
            app_type = data[str(appid)]["data"]["type"]
            cls.execute_sql(
                "UPDATE apps SET type = ? WHERE appID = ?", (app_type, appid)
            )
        except KeyError:
            pass

        # Update is_free
        try:
            is_free = data[str(appid)]["data"]["is_free"]
            cls.execute_sql(
                "UPDATE apps SET is_free = ? WHERE appID = ?", (is_free, appid)
            )
        except KeyError:
            pass

        # Update main_game_id
        try:
            main_game_id = data[str(appid)]["data"]["fullgame"]["appid"]
            cls.execute_sql(
                "UPDATE apps SET main_game_id = ? WHERE appID = ?",
                (main_game_id, appid),
            )
        except KeyError:
            pass

    @classmethod
    def update_redeemed(cls, appid, success):

        cls.execute_sql(
            "UPDATE apps SET is_redeemed = ?, redeem_failed = ? WHERE appID = ?",
            (success, not success, appid),
        )

    @classmethod
    def get_free_games_to_redeem(cls):
        """
        :return: Returns a dict of appid and appname of free games that have not been redeemed yet
        """

        response = cls.execute_sql(
            """
            SELECT appID, name 
            FROM apps 
            WHERE is_free = 1 
            AND is_redeemed = 0 
            AND (type is "game" or type is "dlc")
            AND (main_game_id is null or main_game_id IN (SELECT appID FROM apps WHERE is_redeemed = 1))
            ORDER BY redeem_failed ASC, last_update ASC
            """
        )

        return dict(response)

    @classmethod
    def main(cls):
        cls.create_database()
        cls.upgrade_to_version_1()

        steam_apps = Steam.get_apps()
        database_apps = cls.get_apps()

        cls.add_new_apps_to_database(steam_apps, database_apps)
        cls.update_conflicting_apps(steam_apps, database_apps)

        cls.update_from_prebuilt_database()

        appids = cls.get_appids_to_update()

        database_apps = cls.get_apps()
        for index, appid in enumerate(appids):
            if ExitListener.get_exit_flag():
                break

            cls.update_app_detail(appid)
            remaining_apps = len(appids) - index

            Logger.write_log(
                f"Updated {appid} ({database_apps[appid]}) \t {remaining_apps} apps left to update"
            )

    @classmethod
    def update_conflicting_apps(cls, steam_apps, database_apps):
        conflicting_apps = cls.get_conflicting_apps(steam_apps, database_apps)

        for appid, appname in conflicting_apps.items():
            if ExitListener.get_exit_flag():
                break

            Logger.write_log(
                f'Name of {appid} changed from "{database_apps[appid]}" to "{appname}"'
            )

            cls.execute_sql("DELETE FROM apps WHERE appID = ?", (appid,))
            cls.execute_sql(
                "INSERT OR IGNORE INTO apps (appID, name) VALUES (?, ?)",
                (appid, appname),
            )

    @classmethod
    def get_current_version(cls):
        version = cls.execute_sql("SELECT version FROM version ORDER BY version DESC")
        return version[0][0]

    @classmethod
    def create_version_table(cls):
        if cls.execute_sql("SELECT * FROM sqlite_master WHERE name = 'version'"):
            return

        cls.execute_sql(
            "CREATE TABLE IF NOT EXISTS version (version INTEGER PRIMARY KEY)"
        )
        cls.execute_sql(
            "INSERT OR IGNORE INTO version (version) VALUES (?)", (cls.version,)
        )

    @classmethod
    def upgrade_to_version_1(cls):
        current_version = cls.get_current_version()
        if current_version >= 1:
            return

        # Placeholder for future upgrades

    @classmethod
    def update_from_prebuilt_database(cls):
        if not os.path.exists(cls.prebuilt_db_path):
            return

        prebuilt_data = cls.execute_sql(
            "SELECT type, main_game_id, success, is_free, last_update, appID FROM apps",
            db_path=cls.prebuilt_db_path,
        )

        Logger.write_log("Updating from prebuilt database")

        cls.execute_sql(
            """
            UPDATE apps
            SET type = ?, main_game_id = ?, success = ?, is_free = ?, last_update = ?
            WHERE appID = ?
            """,
            prebuilt_data,
            many=True,
        )

        Logger.write_log("Done updating from prebuilt database")
        os.remove(cls.prebuilt_db_path)


if __name__ == "__main__":
    Database.main()
