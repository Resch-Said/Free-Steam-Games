import os.path
import pathlib

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
    if os.path.isfile('cookies.json'):
        with open('cookies.json', 'r') as f:
            cookies = json.loads(f.read())
            for cookie in cookies:
                if cookie['name'] == 'steamLoginSecure':
                    return cookie['value']
    return None


def load_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_path = pathlib.Path(__file__).parent.absolute() / "chromedriver"

    chrome_options.add_argument(f"user-data-dir={chrome_path}")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


# Get steam identity by logging in with selenium
def create_steam_cookies():
    url = f"https://store.steampowered.com/login/?redir=%3Fsnr%3D1_60_4__global-header&redir_ssl=1&snr=1_4_4__global-header"

    driver = load_chrome_driver()
    driver.get(url)
    try:
        element = WebDriverWait(driver, 600).until(
            EC.presence_of_element_located((By.ID, "account_pulldown"))  # Wait until user is logged in
        )
    finally:
        cookies = driver.get_cookies()
        with open('cookies.json', 'w') as f:
            f.write(json.dumps(cookies))
        driver.quit()


def activate_free_steam_game(appid):
    sessionid = get_steam_sessionid()

    if get_cookies_steam_login_secure() is None:
        create_steam_cookies()

    subid = get_steam_subid(appid)
    url = f"https://store.steampowered.com/freelicense/addfreelicense/{subid}"

    steam_login_secure = get_cookies_steam_login_secure()
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


# Only works if you are logged in and game is not in your library (and free)
def get_steam_subid(appid):
    driver = load_chrome_driver()
    driver.get(f"https://store.steampowered.com/app/{appid}")
    try:
        element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "btn_blue_steamui"))
        )
    finally:
        subid = \
            driver.find_element(By.CLASS_NAME, "btn_blue_steamui").get_attribute("onclick").split(",")[0].split(" ")[1]
        driver.quit()
        return subid


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


print(activate_free_steam_game(1782210))
