# v 1.0.5

🟦 **CRITICAL** separate guildsData guild into different files to reduce possibibility of conflicts

🟦 `spotify_url` in urlsync is not enforced to be unique (this can cause spotify_url duplicates in urlsync)

🟦 suggesting a link after it already finished won't delete the old track which will be accessible using `previous`

🟦 Check rate limits

🟦 transform the musicPlayer embedhandler from polling to observer pattern (or combination of both)

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



[30/03/23 12:39:33][INFO](musicPlayer) - ---------------- PLAYNEXT ----------------
[30/03/23 12:39:33][DEBUG](musicObjects) - Searching URL for Last Man Standing Nitro (Explicit)
[30/03/23 12:39:35][DEBUG](musicPlayer) - URL: https://www.youtube.com/watch?v=ZgTjZWbFlf0
[30/03/23 12:39:35][MUSIC](musicPlayer) - Now Playing: (Last Man Standing) URL = https://www.youtube.com/watch?v=ZgTjZWbFlf0
[youtube] Extracting URL: https://www.youtube.com/watch?v=ZgTjZWbFlf0