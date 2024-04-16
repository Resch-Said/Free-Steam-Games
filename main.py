import requests
import json


def get_steam_sessionid():
    url = f"https://store.steampowered.com/"
    response = requests.get(url)
    cookies = response.cookies
    sessionid = cookies['sessionid']
    return sessionid


def get_steam_login_secure():
    pass


# TODO: Get steam login secure
# TODO: Get the true appid of the game. For example, the appid of "Muck" is 1625450, but the post request needs the appid 577069
def activate_free_steam_game(appid=1782210):
    sessionid = get_steam_sessionid()

    url = f"https://store.steampowered.com/freelicense/addfreelicense/577069"
    steam_login_secure = ""
    headers = {
        "accept-language": "de,de-DE;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cookie": f"sessionid={sessionid}; steamLoginSecure={steam_login_secure}",
    }
    data = {
        "ajax": "true",
        "sessionid": {sessionid}
    }
    response = requests.post(url, headers=headers, data=data)
    print(response.text)


# TODO: Currently just returning a list of free games.
#  I will implement a way to store free games in a file (probably sqlite) and regularly update the list

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

        final_price = 0

        price_exists = 'price_overview' in data[str(appid)]['data']
        if price_exists:
            final_price = data[str(appid)]['data']['price_overview']['final']

        if final_price == 0:
            free_games[appid] = app['name']
            print(f"Found free game: {app['name']}")

    return free_games


print(activate_free_steam_game())
