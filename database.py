import json
import sqlite3
from datetime import datetime

import requests

from steam import Steam


class Database:
    con = sqlite3.connect('steam_free_games.db')
    cur = con.cursor()
    app_detail_url = "https://store.steampowered.com/api/appdetails?appids="

    @classmethod
    def create_database(cls):
        cls.cur.execute(
            "CREATE TABLE IF NOT EXISTS apps (appID INTEGER PRIMARY KEY, name TEXT, success INTEGER,is_free INTEGER,"
            "subID INTEGER,is_redeemed INTEGER, last_update TEXT)")
        cls.con.commit()

    @classmethod
    def get_app_ids(cls):
        cls.cur.execute("SELECT appID FROM apps")
        appids = cls.cur.fetchall()
        appids = [app[0] for app in appids]
        return appids

    @classmethod
    def remove_outdated_apps(cls):
        appids = cls.get_app_ids()
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
            cls.cur.execute("INSERT OR IGNORE INTO apps (appID, name)VALUES (?, ?)", (appid, appname))
        print("Committing changes")
        cls.con.commit()

    @classmethod
    def update_app_detail(cls, appid):
        url = cls.app_detail_url + str(appid)
        response = requests.get(url)
        data = json.loads(response.text)
        data_success = data[str(appid)]['success']

        try:
            appname = data[str(appid)]['data']['name']
            print(f"Updating {appname} ({appid})")
            cls.cur.execute("UPDATE apps SET name = ? WHERE appID = ?", (appname, appid))
        except KeyError:
            pass

        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cls.cur.execute("UPDATE apps SET last_update = ? WHERE appID = ?", (current_date_time, appid))
        cls.cur.execute("UPDATE apps SET success = ? WHERE appID = ?", (data_success, appid))

        try:
            is_free = data[str(appid)]['data']['is_free']
            cls.cur.execute("UPDATE apps SET is_free = ? WHERE appID = ?", (is_free, appid))

            if is_free:
                subid = Steam.get_subid(appid)
                cls.cur.execute("UPDATE apps SET subID = ? WHERE appID = ?", (subid, appid))
        except KeyError:
            pass

        cls.con.commit()


Database.update_app_detail(50)
