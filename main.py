import os.path

import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_steam_sessionid():
    url = f"https://store.steampowered.com/"
    response = requests.get(url)
    cookies = response.cookies
    sessionid = cookies['sessionid']
    return sessionid


def get_cookies_steam_login_secure():
    if os.path.isfile('cookies.txt'):
        with open('cookies.txt', 'r') as f:
            cookies = json.loads(f.read())
            return cookies[1]['value']
    return None


# Get steam identity by logging in with selenium
def get_steam_login_secure():
    url = f"https://store.steampowered.com/login/?redir=%3Fsnr%3D1_60_4__global-header&redir_ssl=1&snr=1_4_4__global-header"

    if get_cookies_steam_login_secure() is not None:
        return get_cookies_steam_login_secure()

    driver = webdriver.Chrome()
    driver.get(url)
    try:
        element = WebDriverWait(driver, 600).until(
            EC.presence_of_element_located((By.ID, "account_pulldown"))  # Wait until user is logged in
        )
    finally:
        cookies = driver.get_cookies()
        with open('cookies.txt', 'w') as f:
            f.write(json.dumps(cookies))
        driver.quit()

    if get_cookies_steam_login_secure() is not None:
        return get_cookies_steam_login_secure()


# TODO: Get the true appid of the game. For example, the appid of "Muck" is 1625450, but the post request needs the appid 577069
def activate_free_steam_game(appid=1782210):
    sessionid = get_steam_sessionid()

    url = f"https://store.steampowered.com/freelicense/addfreelicense/577069"
    steam_login_secure = get_steam_login_secure()
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
