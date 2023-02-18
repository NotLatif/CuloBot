# v 1.0.4

🟧 **[CRITICAL]** Calling spotify many times can hang the program and stops heartbeat (seems to not be happening anymore)

✅ When user suggests a song restart with the new song

✅ Test suggestion function entirely

✅ Test culoplaylists with multiple tracks

✅ Test /play and /add_song to see if they support url1, url2 and playlists with multiple urls

✅ Test add_song positions (and END)

✅ See if song is explicit and eventually add Explicit in query

✅ Support for youtu.be URLs

✅ **[FEATURE]** Specify queue position when using pnext

✅ **[FEATURE]** /add {track} {position}
position can be START, END, number

✅ **[WEIRD]** using /play two times uses the same queue variable what???

✅ **[BUG]** Try `/play randomsite.com`, bot does not disconnect from vc after detecting error

✅ **[BUG]** Culobot EMBED sometimes hangs for some reason (pausing solves it??? wtf) (it still stops updating) maybe the process dies at some point idk (test with callback???? I DON'T KNOW WHAT THETHIE RHAEIRJHOI) solved :)

✅ **[FIX]** modules should be enabled by default and not the other way around.

✅ **[FIX]** MUSIC REPORT SYSTEM

✅ **[FIX]** muisicbot quits when adding single song

✅ **[FIX]** muisicbot stays in vc when queue is paused (setting available in config.py)

✅ **[FIX]** HTTP Forbidden error

✅ **[FIX]** looping a single song does not work everytime

✅ **[TODO]** previous track functionality

✅ **[TODO]** Clean up the main folder

✅ **[TODO]** musicbot button interactions

✅ **[TODO]** musicbot slash commands

✅ **[TODO]** Rewrite musicPlayer.py


# Culobot features
🟥 willdo in the next version
option to save playlist name internally when using a playlist link

🟥 not doing this as this feature is useless for now
Bot does not know when the player finished playing, possible solution:
    Leverage the EmbedHandler coroutine (when it returns the player is usually done)
    https://stackoverflow.com/questions/44345139/python-asyncio-add-done-callback-with-async-def

🟥 willdo in the future
add default permissions

# Culobot bugs

✅ willfix in the next version
Button interactions don't respond after some time passed 

🟥 The error is not appearing anymore
av_interleaved_write_fram(): Broken pipe
./bot-start: line 2: 1298 Killed
Error writing trailer of pipe:1: Broken pipe
./bot-start: line 3: n3.9: command not found

# Code things

🟥 Make settings a local variable under MyBot class

-----legenda-----
✅ Done/Fixed (resets with every release)
🟧 Test needed
🟦 TO DO/CHECK
🟥 wontdo (for now)