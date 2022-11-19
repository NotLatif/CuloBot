# Culobot features
🟦 option to save playlist name internally when using a playlist link

🟥 not doing this as this feature is useless for now
Bot does not know when the player finished playing, possible solution:
    Leverage the EmbedHandler coroutine (when it returns the player is usually done)
    https://stackoverflow.com/questions/44345139/python-asyncio-add-done-callback-with-async-def

🟥 add default permissions

# Culobot bugs

🟦 Button interactions don't respond after some time passed 

🟦 
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