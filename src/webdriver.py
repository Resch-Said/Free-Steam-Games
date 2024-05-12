import os

from selenium import webdriver

from better_path import BetterPath
from exit_listener import ExitListener
from logger import Logger


class Webdriver:
    # user-data-dir requires absolute path
    browser_path = BetterPath.get_absolute_path("../selenium/webdriver")

    # For Linux
    service = webdriver.ChromeService(executable_path="/usr/bin/chromedriver")

    @classmethod
    def load_chrome_driver(cls, hidden=False):
        driver = None
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"user-data-dir={cls.browser_path}")
        chrome_options.add_argument("--enable-chrome-browser-cloud-management")
        chrome_options.add_argument("--no-sandbox")
        if hidden:
            chrome_options.add_argument("--headless=new")
        if os.name == "nt":
            driver = webdriver.Chrome(options=chrome_options)
        elif os.name == "posix":
            driver = webdriver.Chrome(service=cls.service, options=chrome_options)
        else:
            Logger.write_log("OS not supported")
            ExitListener.set_exit_flag(True)
        return driver

    @classmethod
    def main(cls):
        driver = Webdriver.load_chrome_driver()
        driver.get("https://store.steampowered.com/")
        driver.quit()


if __name__ == "__main__":
    Webdriver.main()
