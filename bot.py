from dis import disco
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random
from datetime import datetime

import Main

load_dotenv()#Sensitive data is stored in a ".env" file
TOKEN = os.getenv('DISCORD_TOKEN')[1:-1]
GUILD = os.getenv('DISCORD_GUILD')[1:-1]

intents = discord.Intents.default()
intents.members = True
intents.messages = True
#bot = commands.Bot(command_prefix='!', intents=intents)
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!'),
    intents=intents,
    owner_id=348199387543109654
)

bot.remove_command("help")

settingsFile = "settings.cfg"
settings = {"response":35}

def log(msg):
    """
    It takes a string as an argument, gets the current time, formats it, and writes the message to a file

    please add [STATE]: before message, e.g: `log('[INFO]: bot reloaded.')`

    possible states:
        `INFO, WARN, ERROR, FATAL, DEBUG`

    :param msg: The message to be logged
    """
    if msg[-1] != "\n":
        msg = msg + "\n"

    now = datetime.now()
    current_time = now.strftime("[%d/%m/%y %H:%M:%S]")
    with open('bot.log', 'a') as f:
        f.write(f'{current_time} {msg}')

def getWord():
    """
    :return: A random word from the words.txt file.
    """
    with open('words.txt', 'r') as words:
        lines = words.read().splitlines()
        return random.choice(lines)

def saveSetting(var, value):
    """
    Saves a bot setting in file for future usage
    
    :param var: The key of the dict
    :param value: The value you want to set the variable to
    """
    newlines = ""
    with open('settings.cfg', 'r') as file:
        newlines = file.readlines()
        for n,line in enumerate(newlines):
            if var in line:
                newlines[n] = f'{line.split("=")[0]}={value}\n'

    with open('settings.cfg', 'w') as file:
        file.writelines(newlines)
        

"""
settings:
response = int:         % di probabilità di culificare un messaggio (0 <= int <= 100)
                        - default: 35, minimo 2 parole
other_response = int:   % di possibilità di culificare più di una parola   (0 <= int <= 100)
                        - default: 50, 1 culo ogni due parole
                        - ogni parola ha il 50% di probabilità di essere cambiata rispetto alla precedente                       
"""
def makeSettings():
    """
    If the settings file doesn't exist, create it and write the default settings to it
    """
    
    log("[INFO] il file delle impostazioni non esiste, ne creo uno nuovo.")

    settings = {"response":35, "other_response": 50}
    with open(settingsFile, 'w') as out:
        for settings,number in settings.items():
            line = settings + '=' + str(number) + '\n'
            out.write(line)

def loadSettings():
    """
    It reads the settings file and stores the contents in te settings dict
    """
    with open(settingsFile, 'r') as infile:
        for line in infile:
            tokens = line.strip().split('=')
            var = tokens[0]
            number = tokens[1]
            settings[var] = int(number) #FIXME str should be allowed

    #Controlla se le variabili sono state caricate correttamente
    try:
        settings['response']
        settings['other_response']
    except KeyError as e:
        #TODO sistema il file automaticamente se mancano alcune variabili
        log(f'[ERROR]: ./{settingsFile} non ha tutte le variabili necessarie: {e.args}')



if(os.path.isfile(settingsFile) == False): #create file if not exist.
    makeSettings()
else:   #File exists load vars,
   loadSettings()    

#           -----           DISCORD BOT COROUTINES           -----       #
@bot.event   ## EXCEPTION LOGGER
async def on_error(event, *args, **kwargs):
    if event == 'on_message':
        log(f'[ERROR]: Unhandled message: {args[0]}\n')
    else:
        raise

@bot.event   ## BOT ONLINE
async def on_ready():
    for guild in bot.guilds:
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
    #await member.send(f'A {member.name} piace il culo.')
    channel = bot.get_channel(696014103034069015) 
    await channel.send(f'A {member.name} piace il culo.')   
    print("join detected")


@bot.command(name='resp')
async def perc(ctx, arg=''):  ## BOT COMMAND
    if(arg == ''):
        await ctx.send(f'Rispondo il {settings["response"]}% delle volte')
        return

    newPerc = int(arg.strip("%"))

    if (settings['response'] == newPerc):
        await ctx.send(f"non è cambiato niente.")
        return

    settings["response"] = newPerc
    await ctx.send(f"ok, risponderò il {newPerc}% delle volte")

    log(f'[INFO]: {ctx.author} set response to {arg}%')
    saveSetting('response', newPerc)

@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(
        title = 'CuloBot',
        description = 'I comandi vanno preceduti da "!", questo bot fa uso di ignoranza digitale',
        colour = 0xf39641
    )
    embed.set_footer(text = 'Developed by NotLatif')
    embed.set_thumbnail(url='https://i.pinimg.com/originals/b5/46/3c/b5463c3591ec63cf076ac48179e3b0db.png')
    embed.set_author(name='Help', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    embed.add_field(name='!resp', value='Richiedi la percentuale di risposta', inline=True)
    embed.add_field(name='!resp [x]', value='Imposta la percentuale a (x)', inline=True)
    embed.add_field(name='!ping', value='Pong!', inline=True)
    embed.add_field(name='Source code', value="https://github.com/NotLatif/CuloBot", inline=False)
    embed.set_footer(text='Qualsiasi problema è colpa di @NotLatif')
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    pingms = round(bot.latency*1000)
    await ctx.send(f'Pong! {pingms}ms')
    log(f'[INFO]: ping detected: {pingms} ms')




@bot.event   ## DETECT AND RESPOND TO MSG
async def on_message(message):
    await bot.process_commands(message)

    if message.author == bot.user or len(message.content.split()) < 2 or message.content[0] == '!':
        return  #don't respond to: self, strings with < 2 words, commands
 
    if random.randrange(0, 100) > settings["response"]: #implement % of answering
        return

    if 'word' in message.content: #for future implementation, respond to specific string
        pass

    #culificazione
    msg = message.content.split() #trasforma messaggio in lista
    
    i = 0
    while (len(msg) // 2 > i): #non cambio più di una parola ogni 2    
        scelta = random.randrange(0, len(msg)) #scegli una parola
        parola = getWord() #scegli con cosa cambiarla
        if(msg[scelta].isupper()): #controlla se la parola è maiuscola, o se la prima lettera è maiuscola
            parola = parola.upper()
        elif(msg[scelta][0].isupper()):
            parola = parola[0].upper() + parola[1:]
        msg[scelta] = parola #sostituisci parola

        if(random.randrange(0, 100) > settings['other_response']):
           i+=1
        i+=1

    msg = " ".join(msg) #trasforma messaggio in stringa

    await message.reply(msg, mention_author=False)
    print('responded')
    log(f'[INFO]: responded to message <resp_rate: {settings["response"]}%>')


bot.run(TOKEN)

#TODO comando per vedere la lista delle parole
#TODO comando per togliere/aggiungere parole dalla lista