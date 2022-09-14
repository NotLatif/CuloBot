# Terminal
logLevel = 0 #determines what tags the script prints in the terminal
printLevel = 0 #determines what tags the script prints in the "bot.log" file
useColors = True #whether the terminal should display colored text

#levels: (0 will show every tag; 3 will only show ERROR and FATAL)
# 0 - INFO, MUSIC, USER, GAME
# 1 - DEBUG, VARS, TEST, FUNC
# 2 - WARN, GAMEErr
# 3 - ERROR, FATAL, SONGERROR

#MUSIC PLAYER

timeline_chars = ('▂', '▅')
# Default: ('▂', '▅') -> The character shown in the timeline (tuple[str:str], the first str is the base, the second is the current progress)

timeline_max = 14 
#the max timeline precision guilds can set
# WARNING: a value too high could get you rate limited by the discord API

max_alone_time = 60 * 5 
#Default: 300 -> (max=300) The maximum time (in seconds) the bot can play music while no one is connected to the voice channel