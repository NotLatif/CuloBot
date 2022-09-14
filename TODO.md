# Culobot features

✅ merge contents of config.py into guildsData.json

✅ make timeline_precision settable for each guild whithin a max you can set on `config.py`

✅ if music_precision is set to 0, the bar and timer should not appear in the embed

✅ add !music to help

✅ test timeline_precision and shuffle

✅ Embed colors are not consistent, fix

🟦 Warn users that try to start the bot when it's already on in another text/voice chat

🟦 update system/checker, changelog embed viewer

🟦 Command to change language

🟦 Command for other_perc

🟦 There are too many commands and they are not very consistent. It's starting to get overwelming, maybe command update?

🟦 speed pitch effects(filters nightcore, filters bassboost, filters list, filters reset)

🟦 Finish lang.json

🟦 poll.py

🟥 Palindromi (italian)

# Culobot bugs

✅(seems ok) CHECK IF joining to a second guilds bugs the guildData (also try joining both guilds at the same time)

✅[musicPlayer.py -> getVideoURL()] Song duration is pulled from spotify not youtube!!!!

✅`musicBridge.py@45` `overwritten = tuple[str:str])` = instead of : ? maybe typo, test pls

✅ Quando usi il comando queue non funzionano più i pulsanti

✅ mv x y: sposta la canzone x -> y

✅ MusicPlayer remove from queue

✅[bot.py -> playSong()] Se la queue è in un altra chat si sminchia

✅ loop queue: quando una canzone finisce viene aggiunta in coda

✅ skip while looping queue

🟧 restart: ripete la traccia

🟦 graphical bug while skipping with 1 song loop

🟦 Aggiungere una canzone alla volta fa cose strane allo shuffle

🟦 Raramente può capitare che queue e canzoni in riproduzione si desincronizzano???? (Bug copia.txt)

🟦 guildSettings `buttbotReplied` can get big

🟦 Check what happens when keys are not in the .env file

🟥 reorganize musicPlayer.MessageHandler.getEmbed()

-----legenda-----
✅ Done/Now working
🟧 Test needed
🟦 TO DO/CHECK
🟥 wontdo (for now)


# Other IDEAS for the future

## Music player ⏮ function should
- if current step >= 1, repeat the current song
- else go back one song
  - The queue numbers should not be deleted but there should be a variable that keeps track of the index and can move on the list

