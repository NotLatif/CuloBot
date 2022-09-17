<img  align="right"  src="docs/logo.png"  width="200px">

# [CuloBot](https://notlatif.github.io/CuloBot/)

A discord bot that can play music, let's you play chess and do other things.
**Please submit issues, thank you**

If you like the project and want to help, consider [buying me a coffee!](https://www.buymeacoffee.com/CuloBot)

### [Add bot to your server](https://notlatif.github.io/CuloBot/)

### [Join the Discord!](https://discord.com/invite/YTvn5Zwc5R)



  

## About

Sorry for the poor documentation, I'll improve it later (maybe)

N.B. there will come translations some time in the future, but for now it's a mix of english and italian. Sorry


## How to self-host the bot


#### Prerequisites:

- Python 3.9.2
  
- modules in `requirements.txt` file
- A copy of [ffmpeg](https://ffmpeg.org) added to [path](https://www.thewindowsclub.com/how-to-install-ffmpeg-on-windows-10) (Only needed to use the musicbot module)

- The discord token of your bot [create a bot here](https://discord.com/developers/applications)

- [optional] The spotify key and user id [You can get them here](https://developer.spotify.com/dashboard/applications)

  

#### steps:

1. clone repository in a folder `git clone https://github.com/NotLatif/CuloBot .`

1. Start the `bot.py` file (if necessary install the modules in the `requirements.txt` file

1. Edit the `.env` file adding your keys without quotes

1. on the Developer portal, enable intents under `Privileged gateway intents`

1. click on `OAuth2` -> `Url generator`

1. check `Bot` in the middle, administrator permissions should be good for your own server

1. Add the bot to your server

1. start `bot.py`

1. Everything should be good

  

## Discord commands

You can find them here https://notlatif.github.io/CuloBot/
