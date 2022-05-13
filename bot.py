from ast import arg
import asyncio
import os
import discord #using py-cord dev version (discord.py v2.0.0-alpha)
from discord.ext import commands
from dotenv import load_dotenv
import random
from datetime import datetime
# from discord_slash.model import ButtonStyle
# from discord_slash import SlashCommand
import chessBridge

#oh boy for whoever is looking at this, good luck
#I'm  not reorganizing the code for now (maybe willdo)

#TODO single server use? cringe bro. fucking chess can have infinite instances
#change the stupid settings file and make this work with multiple servers

load_dotenv()#Sensitive data is stored in a ".env" file
TOKEN = os.getenv('DISCORD_TOKEN')[1:-1]
GUILD = os.getenv('DISCORD_GUILD')[1:-1]

intents = discord.Intents.all()
intents.members = True
intents.messages = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!'),
    intents=intents,
    owner_id=348199387543109654
)
# slash = SlashCommand(bot, sync_commands=True)


bot.remove_command("help")

settingsFile = "settings.cfg"
settings = {"response":35, 'other_response':100 , 'respondtobots':100}



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
    :return: A random line from the words.txt file.
    e.g. culo, i culi
    """
    with open('words.txt', 'r') as words:
        lines = words.read().splitlines()
        return random.choice(lines)

def parseWord(message:str, i:int, words:str, articoli:list[str]) -> tuple[str, str]:
    #message = 'No voglio il rosso'
    #words = 'il culo, i culi'
    
    article_word = words.split(', ') #['il culo', 'i culi']
    print(article_word)
    #sorry for spaghetti code maybe will reparse later

    if len(article_word) == 1: #word has only one form (eg: ['il culo'])
        if len(article_word[0].split()) == 1:
            return (message[i-1], article_word[0]) #eg. words = ['culo']
        if message[i-1] not in articoli: #don't change the word before if not an article
            return (message[i-1], article_word[0].split()[1]) #eg. words = ['il culo']
        return (article_word[0].split()[0], article_word[0].split()[1]) #eg. words = ['il culo']

    if message[i-1] not in articoli: #the word before is not an article
        if message[i-1].isnumeric(): #e.g. '3 cavolfiori'
            if message[i-1] == '1':
                return (message[i-1], article_word[0].split()[1]) #'1 culo'
            else:
                return (message[i-1], article_word[1].split()[1]) #'3 culi'
        return (message[i-1], article_word[0].split()[1]) #eg. returns ('ciao', 'culo')

    if message[i-1] in ['il', 'lo', 'la']: #eg. returns ('il', 'culo')
        return (article_word[0].split()[0], article_word[0].split()[1])

    if message[i-1] in ['i', 'gli', 'le']: #eg. returns ('i', 'culi')
        return (article_word[1].split()[0], article_word[1].split()[1])
    
    return ('parsing error', 'parseWord(str, int, str, list[str]) -> tuple[str, str]')

        


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

    settings = {"response":35, "other_response": 50, 'respondtobots':100}
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
        settings['respondtobots']
    except KeyError as e:
        #TODO sistema il file automaticamente se mancano alcune variabili
        log(f'[ERROR]: ./{settingsFile} non ha tutte le variabili necessarie: {e.args}')



if(os.path.isfile(settingsFile) == False): #create file if not exist.
    makeSettings()
else:   #File exists load vars,
   loadSettings()    

#           -----           DISCORD BOT COROUTINES           -----       #
# @bot.event   ## EXCEPTION LOGGER
# async def on_error(event, *args, **kwargs):
#     if event == 'on_message':
#         log(f'[ERROR]: Unhandled message: {args[0]}\n')
#     else:
#         raise

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

@bot.command(name='resp') #TODO add other settings
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

@bot.command(name='user')
async def user(ctx):
    await ctx.send(f'User: {bot.user}')

@bot.command(name='reload')
async def reload(ctx):
    loadSettings()
    await ctx.send(f'Impostazioni aggiornate')
    log('[INFO]: settins reloaded')

@bot.command(name='game', pass_context=True)
async def chessGame(ctx):
    try:
        await ctx.message.delete()
    except:
        pass
    #delete messages: ctx.channel.purge(limit=int(n))
    embed = discord.Embed(title = 'Cerco giocatori, usa una reazione per unirti ad un team (max 1 per squadra)', color = 0x0a7ace)
    playerFetchMsg = await ctx.send(embed=embed)
    reactions = ('⚪', '🌑') #('🤍', '🖤') ✅⛔
    r1, r2 = reactions
    await playerFetchMsg.add_reaction(r1)
    await playerFetchMsg.add_reaction(r2)

    def check1(reaction, user):
        return str(reaction.emoji) in reactions and user != bot.user
    def check2(reaction, user):
        return str(reaction.emoji) in reactions and user != bot.user
    players = [0, 0]
    try:
        r1, players[0] = await bot.wait_for('reaction_add', timeout=60.0, check=check1)
        r2, players[1] = await bot.wait_for('reaction_add', timeout=60.0, check=check2)

    except asyncio.TimeoutError:
        embed = discord.Embed(
            title = 'Non ci sono abbastanza giocatori.',
            colour = 0xdc143c
        )
        await ctx.send(embed=embed)
        await playerFetchMsg.delete()
    else:
        if r1 == reactions[0]: #r1 is white TODO check if white is actually p1 and viceversa
            player1 = players[0]
            player2 = players[1]
        else:
            player1 = players[1]
            player2 = players[0]

        
        embed = discord.Embed(
            title = f'Giocatori trovati\n{r1} {player1} :vs: {player2} {r2}',
            colour = 0x27E039
        )
        
        thread = await ctx.send(embed=embed)
        gameThread = await thread.create_thread(name=(f'{str(player1)[:-5]} -VS- {str(player2)[:-5]}'), auto_archive_duration=60, reason='Scacchi')
        await gameThread.add_user(player1)
        await gameThread.add_user(player2)
        await playerFetchMsg.delete()
        mainThreadEmbed = (thread, embed)

    #game main
    await chessBridge.loadGame(gameThread, bot, [player1, player2], mainThreadEmbed, ctx)


@bot.event   ## DETECT AND RESPOND TO MSG
async def on_message(message):
    await bot.process_commands(message)
    user = message.author
    if message.author == bot.user:
        return
    
    # manage_components.create_button(style=ButtonStyle.URL, label="Your channel", url=f'https://discord.com/channels/{user.guild.id}/{user.id}')
    # action_row = manage_components.create_actionrow(button)
        
    # await message.reply('Hello')
    # return

    if 'word' in message.content: #for future implementation, respond to specific string
        pass
        
    if message.author.id == 438269159126859776: #buttbot
        if random.randrange(1, 100) < settings["respondtobots"]: #implement % of answering
            await asyncio.sleep(random.randrange(1, 3))
            m = ''
            with open('antiButt.txt', 'r') as lines:
                m = random.choice(lines.read().splitlines())
            await message.reply(m, mention_author=False)
            if random.randrange(1, 100) < settings["respondtobots"]/2:
                r = random.choice(['🤣', '😂', '🤢', '🤡'])
                await message.add_reaction(r)
        return

    #culificazione
    articoli = ['il', 'lo', 'la', 'i', 'gli', 'le']
    if message.author == bot.user or len(message.content.split()) < 2 or message.content[0] == '!':
        return  #don't respond to: self, strings with < 2 words, commands
 
    if random.randrange(1, 100) > settings["response"]: #implement % of answering
        return

    msg = message.content.split() #trasforma messaggio in lista
    
    i = 0
    while (len(msg) // 2 > i): #non cambio più di una parola ogni 2    
        scelta = random.randrange(1, len(msg)) #scegli una parola
        if msg[scelta] in articoli and scelta < len(msg)-1:
            scelta += 1
        parola = getWord() #scegli con cosa cambiarla
        articolo, parola = parseWord(msg, scelta, parola, articoli)

        msg[scelta-1] = articolo
        if(msg[scelta].isupper()): #controlla se la parola è maiuscola, o se la prima lettera è maiuscola
            parola = parola.upper()
        elif(msg[scelta][0].isupper()):
            parola = parola[0].upper() + parola[1:]
        msg[scelta] = parola #sostituisci parola

        if(random.randrange(1, 100) > settings['other_response']):
           i+=1
        i+=1

    msg = " ".join(msg) #trasforma messaggio in stringa

    await message.reply(msg, mention_author=False)
    print('responded')
    log(f'[INFO]: responded to message <resp_rate: {settings["response"]}%>')


bot.run(TOKEN)

#TODO comando per vedere la lista delle parole
#TODO comando per togliere/aggiungere parole dalla lista