# CuloBot (CURRENTLY WIP)
A discord bot that can play music, let's you play chess and do other things

<img align="right" src="docs/logo.png" width="150px">

## About
Sorry for the poor documentation, I'll improve it later (maybe)

N.B. there will come translations some time in the future, but for now it's a mix of english and italian. Sorry

### built with:
- Python 3.9.2
- py-cord dev version (discord.py v2.0.0-alpha)

othre requirements are in the `requirements.txt` file

### how to self-host the bot
#### Prerequisites:
- The discord token of your bot [create a bot here](https://discord.com/developers/applications)
- [optional] The spotify key and user id [You can get them here](https://developer.spotify.com/dashboard/applications)
- A copy of FFmpeg installed to path (needed only for musicbot)

#### steps:
1. clone repository in a folder `git clone https://github.com/NotLatif/CuloBot .`
1. Start the `bot.py` file (if necessary install the modules in the `requirements.txt` file
1. Edit the `.env` file adding your keys without quotes
1. on the Developer portal, enable intents under `Privileged gateway intents`
1. click on `OAuth2` -> `Url generator`
1. check `Bot` in the middle, administrator permissions should be good for your own server
1. Add the bot to your server
1. start bot.py
1. everything should be good, probably, maybe not, idk...
1. submit all the Issues you had

## Discord commands
You can find them here https://notlatif.github.io/CuloBot/
