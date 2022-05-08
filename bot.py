from dis import disco
import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='.', intents=intents)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')[1:-1]
GUILD = os.getenv('DISCORD_GUILD')[1:-1]

bot = commands.Bot(command_prefix='!')
bot.remove_command("help")

settingsFile = "settings.cfg"
settings = {"response":35}

def log(msg):
    now = datetime.now()
    current_time = now.strftime("[%d/%m/%y %H:%M:%S]")
    with open('err.log', 'a') as f:
        f.write(f'{current_time} {msg}\n')

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
@bot.event   ## EXCEPTION LOGGER
async def on_error(event, *args, **kwargs):
    if event == 'on_message':
        log(f'Unhandled message: {args[0]}\n')
    else:
        raise

@bot.event   ## BOT ONLINE
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

    #channel = bot.get_channel(972610894930538507)
    #await channel.send("hello world")

@bot.event   ## MEMBER JOIN FIXME
async def on_member_join(member):
    ch = member.get_channel()
    await ch.send(f'A {member.name} piace il culo.')   
    print("join detected")


@bot.command(name='resp', help="Indica la percentuale (intera) di volte a cui il bot risponde ad un messaggio")
async def perc(ctx, arg=''):  ## BOT COMMAND
    if(arg == ''):
        await ctx.send(f'{settings["response"]}%')
        return

    newPerc = int(arg.strip("%"))
    settings["response"] = newPerc
    await ctx.send(f"ok, risponderò il {newPerc}% delle volte")
    log(f'(INFO): {ctx.author} set response to {arg}%')

@bot.command(name='help', help="")
async def help(ctx):
    await ctx.send(f'''
    ```Comandi supportati:\n!resp <int>% -> imposta il valore percentuale delle risposte ai messaggi\n\te.g. !resp 23%```''')

@bot.event   ## DETECT AND RESPOND TO MSG
async def on_message(message):
    await bot.process_commands(message)
    

    if message.author == bot.user: #don't respond to self
        return
    
    if len(message.content.split()) < 2 or message.content[0] == '!':
        return
    print('detected2')
                                                #e.g. 40
    if random.randrange(0, 100) > settings["response"]: #40% chance of answering
        return

    msg = message.content.split() #["ciao", "prova", "1234"]
    msg[random.randrange(0, len(msg))] = "culo"
    msg = " ".join(msg)

    await message.channel.send(msg)



bot.run(TOKEN)