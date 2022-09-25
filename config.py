# Terminal
logLevel = 2 #determines what tags the script prints in the terminal
printLevel = 0 #determines what tags the script prints in the "bot.log" file
useColors = True #whether the terminal should display colored text
timeInTerminal = True

#NOTE, if something won't print it won't log either even if you specified otherwise (printLevel <= logLevel)
#levels: (0 will show every tag; 3 will only show ERROR)
# 0 - DEBUG, VARS, TEST, FUNC, CMDS     < DEBUG, INFO, WARN and ERROR
# 1 - INFO, MUSIC, USER, GAME           < INFO, WARN and ERROR
# 2 - WARN, GAMEErr                     < WARN and ERROR
# 3 - ERROR, FATAL, SONGERROR           < only ERROR

#MUSIC PLAYER

timeline_chars = ('▂', '▅')
# Default: ('▂', '▅') -> The character shown in the timeline (tuple[str:str], the first str is the base, the second is the current progress)

timeline_max = 14 
#the max timeline precision guilds can set
# WARNING: a value too high could get you rate limited by the discord API

max_alone_time = 60 * 5
#Default: 300 -> (max=300) The maximum time (in seconds) the bot can play music while no one is connected to the voice channel

class Colors:
    error = 0xff0000
    red = 0xd32c41
    orange = 0xf39641
    blu = 0x0a7ace
    aqua = 0x7cdcfe
    green = 0x27E039
    black = 0x030303
    white = 0xf2f2f2
