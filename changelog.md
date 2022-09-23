# v1.0.3 - release 

- it seems like the music player does no longer dead-lock the script (still needs testing)
- users not can't use musicplayer buttons if they're not in the voice channel
- the bot does no longer dead-lock when a youtube search fails
- starting to slowly implement error codes in this format Exxxx
- /module-info is now more efficient
- /module-info will no longer crash if a channel gets deleted
- improved user experience for .env file issues
- added botFiles.culobotdata.json for a future API
- moving the bot between different voice channels will no longer break the embedMSG
- moving the bot between different voice channels will no longer break it if there are already people in that channel (if it does, skip the song)
- other small fixes