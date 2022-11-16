# v1.0.4-beta1 (Big rewrite of the musicbot module)

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
(maybe, maybe, maybe, API calls?? makes no sense honestly but could be a way)
Nah makes no sense, but Player should also update a file so it updates on the web!!!

✅ **[FIX]** youtubeParser caps @ 100 tracks per playlist

