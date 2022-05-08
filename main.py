import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random
from datetime import datetime

def log(msg):
    now = datetime.now()
    current_time = now.strftime("[%d/%m/%y %H:%M:%S]")
    with open('err.log', 'a') as f:
        f.write(f'{current_time} {msg}')


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')[1:-1]
GUILD = os.getenv('DISCORD_GUILD')[1:-1]

client = discord.Client()
bot = commands.Bot(command_prefix='!')

settingsFile = "settings.cfg"
settings = {}

#VAR LOAD TODO, put in functions
if(os.path.isfile(settingsFile) == False): #create file if not exist.
    log("[INFO] il file delle impostazioni non esiste, ne creo uno nuovo.")

    settings = {"response":35}
    with open(settingsFile, 'w') as out:
        for settings,number in settings.items():
            line = settings + '=' + str(number) + '\n'
            out.write(line)

else:   #File exists load vars,
    with open(settingsFile, 'r') as infile:
        for line in infile:
            tokens = line.strip().split('=')
            var = tokens[0]
            number = tokens[1]
            settings[var] = float(number)

    #Controlla se le variabili sono state caricate correttamente
    try:
        settings['response'] 
    except KeyError as e:
        #TODO sistema il file automaticamente se mancano alcune variabili
        log(f'(ERROR): ./{settingsFile} non ha tutte le variabili necessarie: {e.args}')
    
    

#           -----           DISCORD BOT COROUTINES           -----       #
@client.event   ## EXCEPTION LOGGER
async def on_error(event, *args, **kwargs):
    if event == 'on_message':
        log(f'Unhandled message: {args[0]}\n')
    else:
        raise
        

@client.event   ## BOT ONLINE
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event   ## MEMBER JOIN XXX
async def on_member_join(member):
    
    await member.create_dm()
    await member.dm_channel.send(
        f'A {member.name} piace il culo.'
    )

@client.event   ## DETECT AND RESPOND TO MSG
async def on_message(message):
    if message.author == client.user: #don't respond to self
        return
    
    if len(message.content.split()) < 2:
        return
    print('detected2')
                                                #e.g. 40
    if random.randrange(0, 100) < settings["response"]: #40% chance of answering
        return

    msg = message.content.split() #["ciao", "prova", "1234"]
    msg[random.randrange(0, len(msg))] = "culo"
    msg = " ".join(msg)

    await message.channel.send(msg)
 





client.run(TOKEN)