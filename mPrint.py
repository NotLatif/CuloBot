from colorama import Fore, Style, init
init()

useColors = True
log = False

def mPrint(tag, source, text):
    """
    Custom print function to use colors
    """
    if not useColors:
        print(f"[{tag}]({source}): {text}")
    
    style = Style.RESET_ALL

    #default is white
    logString = False #this prevents logging useless data (like INFO tag)

    #tags
    if tag == 'INFO':
        tag = f"{Fore.LIGHTCYAN_EX}{tag}"
        logString = False
    elif tag == 'WARN':
        logString = True
        tag = f"{Fore.YELLOW}[{tag}]"
        style = Style.BRIGHT
    elif tag in ['ERROR', 'FATAL']:
        logString = True
        tag = f"{Fore.RED}[{tag}]"
        style = Style.BRIGHT
    elif tag == 'DEBUG':
        logString = False
        tag = f"{Fore.LIGHTMAGENTA_EX}[{tag}]"
    elif tag == 'FUNC':
        logString = False
        tag = f"{Fore.LIGHTBLACK_EX}[{tag}]"
    elif tag == 'USER':
        logString = True
        tag = f"{Fore.CYAN}[{tag}]"
            
    #chessEngine TODO
    elif tag == 'GAME':
        logString = False
        tag = f"{Fore.GREEN}[{tag}]"
    elif tag == 'GAMEErr':
        logString = True
        tag = f"{Fore.RED}[{tag}]"
    elif tag == 'VARS':
        logString = False
        tag = f"{Style.DIM}{Fore.YELLOW}[{tag}]"
    
    #musicbot TODO
    elif tag == 'MUSIC':
        logString = False
        tag = f"{Fore.WHITE}[{tag}]"

    else:
        tag = f"[{tag}]"
        
#							  p2 is only used for ENGINE
    print(f'{style}{tag}({source}) - {text}{Fore.RESET}')

    #log string
    if log: pass