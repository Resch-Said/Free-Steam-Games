# Free-Steam-Games

## Run in background using screen (Linux)

> sudo apt install screen\
> screen

Now we can detach with `CTRL + A + D`\
Show all detached screens: `screen -list`\
Attach to a specific screen with `screen -r <number>` or just `screen -r` \
Kill a screen with `exit` or `CTRL + D`

This will allow us to run the redeemer in the background and regularly check if something went wrong or just stop it
altogether.

## How to use the software

| ![Exclamation Mark](https://toppng.com/public/uploads/thumbnail/exclamation-mark-png-exclamation-mark-icon-11563006763nmogfagx6y.png) | Make sure to install git and python3.9 or higher. |
|---------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|

Wait until the login screen opens and login into steam (first time). That's pretty much all. \
The run script will automatically run `git pull` to check for updates. \
To stop the script, you can press "q" and enter.

## Windows

> git clone https://github.com/Resch-Said/Free-Steam-Games.git \
> cd Free-Steam-Games/ \
> .\run.bat

## Linux

> sudo apt install chromium-chromedriver \
> git clone https://github.com/Resch-Said/Free-Steam-Games.git \
> cd Free-Steam-Games/ \
> sudo chmod +x run.sh \
> ./run.sh

