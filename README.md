# Free-Steam-Games

## Get Chrome Webdrivers

Since we use selenium, we need to install the webdrivers
> sudo apt install chromium-chromedriver

## Run in background using screen

> sudo apt install screen\
> screen

Now we can detach with `CTRL + A + D`\
Show all detached screens: `screen -list`\
Attach to a specific screen with `screen -r <number>` or just `screen -r`

This will allow us to run the redeemer in the background and regularly check if something went wrong or just stop it
altogether.

## How to use the software

If you're using a newer machine like Windows, it could the beneficial to change `selenium==<version>` inside the
requirements.txt to `selenium`, so you get the newest version.

> git clone https://github.com/Resch-Said/Free-Steam-Games.git \
> cd Free-Steam-Games/ \
> python -m pip install -r requirements.txt \
> python main.py

Wait until the login screen opens and login into steam. That's pretty much all.\
You can check for updates by doing `git pull` \
To stop the script, you can press "q" and enter.
