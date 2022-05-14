# CuloBot
 Meme bot per gli amici del discord
 Progettato per uso su un singolo server

Ha anche un gioco di scacchi!
Sistemerò questo readme un giorno futuro...

# Quick start
Sorry for the poor documentation, will come back and fix later

N.B. there will come translations some time in the future, but for now it's a mix of english and italian. Sorry

## prerequisites
(this is what I am running, not a minimum or recommended)
- Python 3.9.2
- py-cord dev version (discord.py v2.0.0-alpha)
- Discord account

## steps
1. clone repository in a folder
2. create a file named `.env` in the main folder
3. paste this string: `DISCORD_TOKEN={SUPER_SECRET_TOKEN}`
4. log in the [Discord Developer Portal](https://discord.com/developers/applications)
5. create a New Application, change settings as you pleas
6. go to `Bot` on the left and click `Add Bot`
7. click `Reset token` and copy it (WARNING: the token grants access to your bot, do not share your token)
8. paste your token without quotes in the `.env` file replacing `SUPER_SECRET_TOKEN`
9. on the Developer portal, enable everything under `Privileged gateway intents`
10. click on `OAuth2` -> `Url generator`
11. check `Bot` in the middle and give the permissions you want, I don't know yet which are needed for the bot to work sorry about that
12. Add the bot to your server
13. start bot.py
14. everything should be good, probably, maybe not, idk...
15. submit all the Issues you had
