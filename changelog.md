# v1.0.4-beta3 (Big rewrite of the musicbot module)

# beta 3
- Fixed automatic update rate of getEmbed()
- Prevented some 400 responses by shortening fields in the musicbot embed
- Both features toghether should brevent getting rate limited by discord
- Increased timeframe to check if bot was disconnected to prevent accidental queue stop
- /add_song now shows an arrow in the queue if the song is in the viewable list
- You can now use commas for multiple songs with /play and /add_song. eg: /play url=[Song1, Song2] (works with urls, playlists and youtube search)
- When suggesting a wrong track the player now restarts with the new song
- When using the suggest button if the song skips the suggested one is added to the queue as next but not played until the current one finishes
- Fixed issue with youtubeparser (see diff)
- getEnv() has generally better parsing
- This version seems to fix most of the big issues with the latest version

# beta 2
- file bot.py now supports the lang.py file (TODO: easy language change in config.py)
- new config for music player to wait in VC after the queue finishes
- other fixes

# beta 1
- lang is now a python file for better management
- utilities files are now moved in the utils folder
- musicBridge and chessBridge were moved in the music/ and chessGame/ folders

# beta 0

### Changes
- Links now get parsed in a smarter way
  - Using a youtube link with a playlist attached will now add all the songs starting from the one you are currently listening on youtube (if shuffle is disable)
- Musicbot now uses slash commands
- emoji "buttons" are now discord.ui.Button
- errors are now generally more descriptive
- Solved most bugs that make the bot crash
- Modules are now enabled by default

### Done

🟧 **[CRITICAL]** Calling spotify many times can hang the program and stops heartbeat _(Needs further testing)_

✅ **[FEATURE]** Specify queue position when using pnext

✅ **[FEATURE]** /add_song {track} {position}
position can be int or number (default = 0)

✅ **[WEIRD]** using /play two times uses the same queue variable what???

✅ **[BUG]** Culobot EMBED sometimes hangs for some reason (pausing solves it??? wtf) (it still stops updating) maybe the process dies at some point idk (test with callback???? I DON'T KNOW WHAT THETHIE RHAEIRJHOI)

✅ **[FIX]** modules should be enabled by default and not the other way around.

✅ **[FIX]** MUSIC REPORT SYSTEM (PLEASE)

✅ **[FIX]** muisicbot quits when adding single song

✅ **[FIX]** muisicbot stays in vc when queue is paused

✅ **[FIX]** HTTP Forbidden error (retry one time bug error #2, #3)

✅ **[FIX]** looping a single song does not work everytime

✅ **[TODO]** facendo traccia precedente torna indietro (anche se a metà traccia)

✅ **[TODO]** Clean up the main folder

✅ **[TODO]** musicbot slash commands

✅ **[TODO]** Rewrite musicPlayer.py, seriously, it sucks especially the way EMBED works and how it links to the player

✅ **[FIX]** youtubeParser caps @ 100 tracks per playlist

