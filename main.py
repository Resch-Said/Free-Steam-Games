import requests
import json

from database import Database


# TODO: Update app details
def update_free_steam_games():
    Database.create_database()
    Database.remove_outdated_apps()
    Database.add_new_apps_to_database()


def get_free_steam_games():
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(url)
    data = json.loads(response.text)

    free_games = {}
    for app in data['applist']['apps']:
        appid = app['appid']
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        response = requests.get(url)
        data = json.loads(response.text)

        data_success = data[str(appid)]['success']
        if not data_success:
            continue

        is_free = data[str(appid)]['data']['is_free']
        if not is_free:
            continue

        free_games[appid] = app['name']
        print(f"Found free game: {app['name']}")

    return free_games
