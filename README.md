# Free-Steam-Games

Free Steam Games is a little script that automatically redeems free games on Steam. It uses the selenium library to
interact with the Steam website.
At the beginning, the Steam Login website will open and ask you to log in. Everything else runs automatically in the
background. You also do not have to sign in again when you start the application.

The run script will automatically run `git pull` to check for updates. \
To stop the script, you can press "q" and enter.

## Linux

Make sure git and python3.9 or higher are installed.

### Installation

> sudo apt install chromium-chromedriver \
> git clone https://github.com/Resch-Said/Free-Steam-Games.git \
> cd Free-Steam-Games/ \
> sudo chmod +x run.sh \
> ./run.sh

### Run in background using screen

> sudo apt install screen\
> screen

Now we can detach with `CTRL + A + D`\
Show all detached screens: `screen -list`\
Attach to a specific screen with `screen -r <number>` or just `screen -r` \
Kill a screen with `exit` or `CTRL + D`

This will allow us to run the redeemer in the background and regularly check if something went wrong or just stop it
altogether.

## Windows

Make sure to install [git](https://git-scm.com/downloads)
and [python3.9](https://apps.microsoft.com/detail/9p7qfqmjrfp7) or higher.

Select a folder in which the application should be installed and open the terminal.
> git clone https://github.com/Resch-Said/Free-Steam-Games.git \
> cd Free-Steam-Games/ \
> .\run.bat
