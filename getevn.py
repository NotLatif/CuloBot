# Sensitive data is stored in a ".env" file
# Since I had problems getting getenv to work on linux for some reason,
# I'm writing my own function in case someone else has the same problems

import os
import sys
from mPrint import mPrint as mp
def mPrint(tag, value):mp(tag, 'env', value)

if not os.path.isfile(".env"):
    mPrint('FATAL', 'File not found')
    with open('.env', 'w') as f:
        f.write("#required fields: DISCORD_TOKEN\nDISCORD_TOKEN={}\nSPOTIFY_ID={}\nSPOTIFY_SECRET={}\nGENIOUS_SECRET={}\nOWNER_ID={}#This is optional and only needed for the /feedback command, the data will still be saved in the feedback.log file")
    mPrint('INFO', 'I created a file named ".env", insert your tokens there')
    input("Press enter to exit...")
    sys.exit()

def missing(severity, message):
    """
    :param severity: 0=WARN, 1=FATAL
    """
    if severity == 1:
        mPrint('FATAL', message)
        input("Press enter to exit...")
        sys.exit()
    elif severity == 0:
        mPrint('WARN', message)

def getenv(var : str, required=False) -> str:
    with open('.env', 'r') as env:
        lines = env.readlines()
        for l in lines:
            if '#' in l: #remove comments
                l = l.split('#')[0]
            if var in l:
                token = l.strip(var)[2:-2]
                if token != "":
                    return token
                else:
                    break
    #token not found
    missing(required, f"TOKEN {var} was not found, insert it in the .env file")
    return 0