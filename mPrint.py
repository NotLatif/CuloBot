import codecs
from datetime import datetime
from colorama import Fore, Style, init
init()

useColors = True
logLevel = 2 #log level should be >= print level
printLevel = 0
#levels: (0 will show every tag; 3 will only show ERROR and FATAL)
# 0 - INFO, MUSIC, USER, GAME
# 1 - DEBUG, VARS, TEST, FUNC
# 2 - WARN, GAMEErr
# 3 - ERROR, FATAL, SONGERROR

def mPrint(tag, source, text):
    """
    Custom print function to use colors
    """

    willPrint = False
    willLog = False
    songError = False

    if printLevel <= 3:
        if tag in ['ERROR', 'FATAL', 'SONGERROR']: willPrint = True
    if printLevel <= 2:
        if tag in ['WARN', 'GAMEErr']: willPrint = True
    if printLevel <= 1:
        if tag in ['DEBUG', 'VARS', 'TEST', 'FUNC']: willPrint = True
    if printLevel <= 0:
        if tag in ['INFO', 'MUSIC', 'USER', 'GAME']: willPrint = True

    if logLevel <= 3:
        if tag in ['ERROR', 'FATAL', 'SONGERROR']: willLog, songError = True, True
    if logLevel <= 2:
        if tag in ['WARN', 'GAMEErr']: willLog = True
    if logLevel <= 1:
        if tag in ['DEBUG', 'VARS', 'TEST', 'FUNC']: willLog = True
    if logLevel <= 0:
        if tag in ['INFO', 'MUSIC', 'USER', 'GAME']: willLog = True
    
    if willPrint == False: return

    now = datetime.now().strftime("[%d/%m/%y %H:%M:%S]")
    
    logstr = f"{now} > [{tag}]({source}): {text}\n"
    
    style = Style.RESET_ALL

    #tags
    if tag == 'INFO':
        tag = f"{Fore.LIGHTCYAN_EX}[{tag}]"

    elif tag == 'WARN':
        tag = f"{Fore.YELLOW}[{tag}]"

    elif tag in ['ERROR', 'FATAL', 'SONGERROR']:
        tag = f"{Fore.RED}[{tag}]"
        style = Style.BRIGHT

    elif tag == 'DEBUG':
        tag = f"{Fore.MAGENTA}[{tag}]"

    elif tag == 'FUNC':
        tag = f"{Fore.LIGHTBLACK_EX}[{tag}]"

    elif tag == 'TEST':
        tag = f"{Fore.LIGHTBLUE_EX}[{tag}]"
        style = Style.BRIGHT
        
    elif tag == 'USER':
        tag = f"{Fore.CYAN}[{tag}]"
            
    #chessEngine TODO
    elif tag == 'GAME':
        tag = f"{Fore.GREEN}[{tag}]"

    elif tag == 'GAMEErr':
        tag = f"{Fore.RED}[{tag}]"

    elif tag == 'VARS':
        tag = f"{Fore.YELLOW}[{tag}]"
        style = Style.DIM
    
    #musicbot TODO
    elif tag == 'MUSIC':
        tag = f"{Fore.WHITE}[{tag}]"

    else:
        tag = f"[{tag}]"
        
#							  p2 is only used for ENGINE
    print(f'{style}{tag}({source}) - {text}{Fore.RESET}')

    #log string
    if willLog:
        with codecs.open('bot.log', 'a', 'utf-8') as f:
            f.write(logstr)

    if songError:
        with codecs.open('song_wrong_url.log', 'a', 'utf-8') as f:
            f.write(logstr)