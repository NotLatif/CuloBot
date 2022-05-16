import asyncio
import os
import json
import random
import copy
import shutil
import sys
import discord #using py-cord dev version (discord.py v2.0.0-alpha)
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
from typing import Union

import chessBridge

#oh boy for whoever is looking at this, good luck
#I'm  not reorganizing the code for now (maybe willdo)

load_dotenv()#Sensitive data is stored in a ".env" file
TOKEN = os.getenv('DISCORD_TOKEN')[1:-1]
GUILD = os.getenv('DISCORD_GUILD')[1:-1]

SETTINGS_TEMPLATE = {"id":{"responseSettings":{"join_message":"A %name% piace il culo!","response_perc":35,"other_response":20,"response_to_bots_perc":25,"will_respond_to_bots":True,"use_global_words":True,"custom_words":[]},"chessGame":{"default_board": "default","boards":{},"designs":{}}}}
#TOIMPLEMENT: use_global_words, chessGame

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

settingsFile = "botFiles/guildsData.json"
settings = {}
with open(settingsFile, 'a'): pass #make setting file if it does not exist

#Useful funtions
def splitString(str, separator = ' ', delimiter = '\"') -> list:
    #https://icodelog.wordpress.com/2018/08/01/splitting-on-comma-outside-quotes-python/
    #splits string based on separator only if outside double quotes
    i = -1
    isQ = False
    lstStr = []
    for s in str:
        if s != separator and s != delimiter:
            if i == -1 or i < len(lstStr):
                lstStr.append(s)
                i = len(lstStr)
            else:
                lstStr[i-1] = lstStr[i-1] + s
         
        elif s == separator and isQ == False:
            lstStr.append('')
            i = len(lstStr)
             
        elif s == delimiter and isQ == False:
            isQ = True
            continue
         
        elif s == delimiter and isQ == True:
            isQ = False
            continue
         
        elif s == separator and isQ == True:
            lstStr[i-1] = lstStr[i-1] + s
         
    return lstStr

def dumpSettings():
    """Saves the settings to file"""
    with open(settingsFile, 'w') as f:
        json.dump(settings, f, indent=2)

def loadSettings():
    template = {}
    global settings
    try:
        with open(settingsFile, 'r') as f:
            settings = json.load(f)
    except json.JSONDecodeError: #file is empty
        with open(settingsFile, 'w') as fp:
            json.dump(template, fp , indent=2)
        return 0

def updateSettings(id : int, setting :str = None, value :str = None, reset : bool = False, category : str = "responseSettings"):
    id = str(id)
    if setting != None:
        settingFound = False
        for s in settings[id][category]:
            if s == setting:
                settings[id][category][s] = value
                settingFound = True
        if settingFound == False : return -1

        print('settings updated for ' + str(id))
        with open(settingsFile, 'w') as f:
            json.dump(settings, f, indent=2)
        return
    
    elif reset: #if only id is given, we want to append a new server
        with open(settingsFile, 'r') as f:
            temp = json.load(f)
        temp[id] = SETTINGS_TEMPLATE["id"]
        with open(settingsFile, 'w') as fp:
            json.dump(temp, fp , indent=2)
            settings[id] = temp[id]
  
def checkSettingsIntegrity(id : str):
    id = str(id)
    print(f'Checking guildData integrity of ({id})')

    settingsToCheck = copy.deepcopy(settings[id])
    
    #check if there is more data than there should
    for key in settingsToCheck:
        if(key not in SETTINGS_TEMPLATE["id"]): #check if there is a key that should not be there (avoid useless data)
            del settings[id][key]
            print(f'Deleting: {key}')

        if(type(settingsToCheck[key]) == dict):
            for subkey in settingsToCheck[key]:
                if(subkey not in SETTINGS_TEMPLATE["id"][key]): #check if there is a subkey that should not be there (avoid useless data)
                    del settings[id][key][subkey]
                    print(f'Deleting: {subkey}')

    #check if data is missing
    for key in SETTINGS_TEMPLATE["id"]:
        if(key not in settings[id]): #check if there is a key that should not be there (avoid useless data)
            settings[id][key] = SETTINGS_TEMPLATE["id"][key]
            print(f'Missing key: {key}')

        #it it's a dict also check it's keys
        if(type(SETTINGS_TEMPLATE["id"][key]) == dict):
            for subkey in SETTINGS_TEMPLATE["id"][key]:
                if(subkey not in settings[id][key]): #check if there is a key that should not be there (avoid useless data)
                    settings[id][key][subkey] = SETTINGS_TEMPLATE["id"][key][subkey]
                    print(f'Missing subkey: {subkey}')

    dumpSettings()

    print('####### Done #######')

def log(msg): #It's more annoying than it is usefull, maybe 
    return
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

def getWord(all=False) -> Union[str,list]:
    """
    :return: A random line from the words.txt file.
    e.g. culo, i culi
    """
    with open('botFiles/words.txt', 'r') as words:
        lines = words.read().splitlines()
        if(all):
            return lines
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

        

#           -----           DISCORD BOT COROUTINES           -----       #
@bot.event #exception logger
async def on_error(event, *args, **kwargs):
    print(sys.exc_info())
    if event == 'on_message':
        log(f'[ERROR]: Unhandled message: {args[0]}\n')
    log(sys.exc_info())

@bot.event   ## BOT ONLINE
async def on_ready():
    for guild in bot.guilds:
        print(
            f'\nConnected to the following guild:\n'
            f'{guild.name} (id: {guild.id})'
        )

        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')
        if (str(guild.id) not in settings):
            print('^ Generating settings for guild')
            updateSettings(str(guild.id), reset=True)

        checkSettingsIntegrity(str(guild.id))

@bot.event
async def on_member_join(member : discord.Member):
    joinString = settings[str(member.guild.id)]['responseSettings']['join_message']
    if(joinString == ''): return
    joinString.replace('%name%', member.name)

    await member.guild.system_channel.send(joinString)   
    print("join detected")

@bot.command(name='rawdump')
async def rawDump(ctx : commands.Context):
    await ctx.send(f'```JSON dump for {ctx.guild.name}:\n{json.dumps(settings[str(ctx.guild.id)], indent=3)}```')

@bot.command(name='rawchange')
async def rawChange(ctx : commands.Context):
    args = ctx.message.content.split()[1:]
    id = str(ctx.guild.id)
    if len(args) == 2:
        if (args[1].isnumeric()): args[1] = int(args[1])
        r = updateSettings(id, args[0], args[1])
        if r == -1:
            await ctx.send(f'```Setting "{args[0]}" not found\nuse !rawdump to see the data```')
        else:
           await ctx.send(f'```"{args[0]}" = {args[1]}```')
    else:
        await ctx.send('huh?')

@bot.command(name='joinmsg')
async def joinmsg(ctx : commands.Context):
    args = ctx.message.content.split()
    if len(args) == 1:
        #if join message is not empty
        if(settings[str(ctx.guild.id)]['responseSettings']['join_message'] != ''):
            await ctx.send(settings[str(ctx.guild.id)]['responseSettings']['join_message'])
        else:
            await ctx.send('Il server non ha un messaggio di benvenuto, `!joinmsg help` per informazioni')
    else:
        if args[1] == 'help':
            await ctx.send('`!joinmsg [msg]`: cambia il messaggio di benvenuto\nPuoi usare %name% nel messaggio per riferirti ad un utente eg: `!joinmsg A %name% piace il culo 🍑`\nUsa `!joinmsg false` per disattivarlo')
            return
        elif args[1].lower() == 'false':
            settings[str(ctx.guild.id)]['responseSettings']['join_message'] = ''
            await ctx.send('Hai disattivato la risposta')
            return
        settings[str(ctx.guild.id)]['responseSettings']['join_message'] = ' '.join(args[1:])
        dumpSettings()
        await ctx.send(f"Il nuovo messaggio di benvenuto è:\n{settings[str(ctx.guild.id)]['responseSettings']['join_message']}")

@bot.command(name='resp') 
async def perc(ctx : commands.Context):  ## RESP command
    arg = ctx.message.content.replace('!resp', '')
    respSettings = settings[str(ctx.guild.id)]["responseSettings"]

    if(arg == ''):
        await ctx.send(f'Rispondo il {respSettings["response_perc"]}% delle volte')
        return
    
    arg = arg.lower().split()

    affirmative = ['true', 'yes', 'si', 'vero']
    negative = ['false', 'no', 'false']
    validResponse = False
    if(arg[0].strip('s') == 'bot'):
        print(arg)
        if len(arg) == 1:
            await ctx.send(f'Risposta ai bot: {respSettings["will_respond_to_bots"]}\nRispondo ai bot il {respSettings["response_to_bots_perc"] if respSettings["will_respond_to_bots"] else 0}% delle volte')
            return

        if(arg[1].isnumeric()):
            await ctx.send(f'Okay, risponderò ai bot il {arg[1]}% delle volte')
            updateSettings(str(ctx.guild.id), 'response_to_bots_perc', int(arg[1]))
            return
        
        if arg[1] in affirmative:
            response = 'Okay, culificherò anche i bot 🍑'
            validResponse = True
        elif arg[1] in negative:
            response = 'Niente culi per i bot 🤪'
            validResponse = True
        else:
            response = 'Ehm, non ho capito? cosa vuoi fare con i bot?'
        await ctx.send(response)
        if validResponse:
            updateSettings(ctx.guild.id, 'will_respond_to_bots', arg[1])
            return

    newPerc = int(arg[0].strip("%"))

    if (respSettings['response_perc'] == newPerc):
        await ctx.send(f"non è cambiato niente.")
        return

    respSettings["response_perc"] = newPerc
    await ctx.send(f"ok, risponderò il {newPerc}% delle volte")

    log(f'[INFO]: {ctx.author} set response to {arg}%')
    updateSettings(str(ctx.guild.id) , 'response', newPerc)
    updateSettings(str(ctx.guild.id) , 'other_response', newPerc//2)

@bot.command(name='words', aliases=['parole'])
async def words(ctx : commands.Context): #send an embed with the words that the bot knows
    args = ctx.message.content.split()
    if len(args) > 1: #add new words
        newWord = ' '.join(args[1:])
        if args[1].lower() == 'del':
            delWord = int(args[2])
            if len(settings[str(ctx.guild.id)]['responseSettings']['custom_words']) > delWord:
                del settings[str(ctx.guild.id)]['responseSettings']['custom_words'][delWord]
                await ctx.send('Fatto')
            else:
                await ctx.send('Id parola non trovato, `!words` per la lista di parole')
            return
        
        if args[1].lower() == 'edit':
            editWord = int(args[2])
            if len(settings[str(ctx.guild.id)]['responseSettings']['custom_words']) > editWord:
                settings[str(ctx.guild.id)]['responseSettings']['custom_words'][editWord] = ' '.join(args[3:])
                await ctx.send('Fatto')
            else:
                await ctx.send('Id parola non trovato, `!words` per la lista di parole')
            return

        if args[1].lower() == 'add':
            newWord = ' '.join(args[2:])
        
        settings[str(ctx.guild.id)]['responseSettings']['custom_words'].append(newWord)
        await ctx.send('Nuova parola imparata!')
        dumpSettings()

        return

    #1. Send a description
    custom_words = settings[str(ctx.guild.id)]['responseSettings']['custom_words']
    description = f'''Comandi disponibili:\n`!words del <x>` per eliminare una parola
                        `!words edit <x> <parola>` per cambiare una parola
                        `!words <parola>` per aggiungere una parola nuova
                        `!words del <id>` per rimuovere una parola nuova
                        `!words useDefault [true|false]` per scegliere se usare le parole di default
                        eg: `!words il culo, i culi` < per un esperienza migliore specifica l'articolo e la forma singolare(plurale)
                        eg: `!words culo` < specificare le forme non è obbligatorio
                        Puoi modificare solo le parole di {ctx.guild.name}
    '''

    if not settings[str(ctx.guild.id)]['responseSettings']['use_global_words']:
       description += f'{ctx.guild.name} non usa le parole di default, quindi non verranno mostrate, per mostrarle usare il comando: `!words useDefault `'
        
    embed = discord.Embed(
        title = 'Ecco le parole che conosco: ',
        description = description,
        colour = 0xf39641
    )

    value = ''
    #2a. get the global words
    botWords = getWord(True)

    #2b. if the guild uses the global words, append them to value
    if settings[str(ctx.guild.id)]['responseSettings']['use_global_words']:
        #is server uses default words
        value = '\n'.join(botWords)
        embed.add_field(name = 'Parole del bot:', value=value)
        value = '' 

    #2c. append the guild(local) words to value
    for i, cw in enumerate(custom_words):
        value += f'[`{i}`]: {cw}\n'
    if value == '': value='Nessuna parola impostata, usa `!words help` per più informazioni'
    embed.add_field(name = f'Parole di {ctx.guild.name}:', value=value)
    
    #3. send the words
    await ctx.send(embed=embed)

@bot.command(name = 'help')
async def embedpages(ctx : commands.Context):
    e = discord.Embed (
        title = 'CuloBot',
        description = 'I comandi vanno preceduti da "!", questo bot fa uso di ignoranza artificiale',
        colour = 0xf39641
    ).set_footer(text='Ogni cosa è stata creata da @NotLatif, se riscontrare bug sapete a chi dare la colpa.')
    
    e.set_thumbnail(url='https://i.pinimg.com/originals/b5/46/3c/b5463c3591ec63cf076ac48179e3b0db.png')

    page1 = e.copy().set_author(name='Help 1/3, culo!', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page2 = e.copy().set_author(name='Help 2/3, CHECKMATE', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page3 = e.copy().set_author(name='Help 3/3, misc', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    
    #Page 1
    page1.add_field(name='!resp', value='Chiedi al bot la percentuale di culificazione', inline=False)#ok
    page1.add_field(name='!resp [x]%', value='Imposta la percentuale di culificazione a [x]%', inline=False)#ok
    page1.add_field(name='!resp bot', value= 'controlla le percentuale di risposta verso gli altri bot', inline=False)#ok
    page1.add_field(name='!resp bot [x]%', value= 'Imposta la percentuale di culificazione contro altri bot a [x]%', inline=False)#ok
    page1.add_field(name='!resp bot [True|False]', value= 'abilita/disabilita le culificazioni di messaggi di altri bot', inline=False)#ok
    page1.add_field(name='!words', value='Usalo per vedere le parole che il bot conosce', inline=False)
    page1.add_field(name='!words [add <words>|del <id>|edit<id> <word>]', value='Usalo modificare le parole del server', inline=False)
    page1.add_field(name='Struttura di word:', value='Per un esperienza migliore è consigliato usare gli articoli e specificare prima la forma singolare e poi quella plurale divise da una virgola e.g. `il culo, i culi`\n`il culo` `culo` `culo, culi` sono comunque forme accettabili', inline=False)

    #Page 2
    page2.add_field(name='!chess [@user | @role] [fen="<FEN>" | board=<boardname>] [design=<deisgn>]', 
    value='Gioca ad una partita di scacchi!\n\
     [@user]: Sfida una persona a scacchi\n\
     [@role]: Sfida un ruolo a scacchi\n\
     [fen="<FEN>"]: usa una scacchiera preimpostata\n\
     [board=<boardname>]: usa una delle scacchiere salvate\n\
     [design=<design>: usa uno dei design disponibili', inline=False)#ok
    page2.add_field(name='e.g.:', value='```!chess board=board2\n!chess\n!chess @Admin\n!chess fen="k7/8/8/8/8/8/8/7K"```')

    page2.add_field(name='!chess boards', value='vedi i FEN disponibili', inline=False)#ok
    page2.add_field(name='!chess design [see|add|del|edit]', value='vedi le scacchiere disponibili `!chess design` per più informazioni', inline=False)#ok
    page2.add_field(name='!chess render <name | FEN>', value='genera l\'immagine della scacchiera', inline=False)#ok
    page2.add_field(name='!chess add <name> <FEN>', value='aggiungi una scacchiera', inline=False)#ok
    page2.add_field(name='!chess remove <name>', value='rimuovi una scacchiera', inline=False)#ok
    page2.add_field(name='!chess rename <name> <newName>', value='rinomina una scacchiera', inline=False)#ok
    page2.add_field(name='!chess edit <name> <FEN>', value='modifica una scacchiera', inline=False)#ok

    #Page 3
    page3.add_field(name='!ping', value='Pong!', inline=False)#ok
    page3.add_field(name='!rawdump', value='manda un messaggio con tutti i dati salvati di questo server', inline=False)#ok
    page3.add_field(name='joinmsg [msg]', value="Mostra il messaggio di benvenuto del bot, usa `!joinmsg help` per più informazioni\n", inline=False)

    #fotter for page 1
    page1.add_field(name='Source code', value="https://github.com/NotLatif/CuloBot", inline=False)
    page1.add_field(name='Problemi? lascia un feedback qui', value="https://github.com/NotLatif/CuloBot/issues", inline=False)
    
    pages = [page1, page2, page3]

    msg = await ctx.send(embed = page1)

    await msg.add_reaction('◀')
    await msg.add_reaction('▶')
    
    i = 0
    emoji = ''

    while True:
        if str(emoji) == '⏮':
            i = 0
            await msg.edit(embed = pages[i])
        elif str(emoji) == '◀':
            if i > 0:
                i -= 1
                await msg.edit(embed = pages[i])
        elif str(emoji) == '▶':
            if i < 2:
                i += 1
                await msg.edit(embed = pages[i])
        elif str(emoji) == '⏭':
            i = 2
            await msg.edit(embed = pages[i])
        
        def check(reaction, user):
            return user != bot.user and str(reaction.emoji) in ['⏮', '◀', '▶', '⏭']
        
        try:
            emoji, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            await msg.remove_reaction(str(emoji), user)
            continue
        except asyncio.TimeoutError:
            await msg.clear_reactions()
            break

    await msg.clear_reactions()

@bot.command(name='ping')
async def ping(ctx : commands.Context):
    pingms = round(bot.latency*1000)
    await ctx.send(f'Pong! {pingms}ms')
    log(f'[INFO]: ping detected: {pingms} ms')

@bot.command(name='user')
async def user(ctx : commands.Context):
    await ctx.send(f'User: {bot.user}')

@bot.command(name='chess', pass_context=True) #CHESS GAME (very long def)
async def chessGame(ctx : commands.Context):
#1. Prepare the variables
    #info about the player challenging another player or a role to a match
    challenge = { #need dict otherwise script dumps some of the variables idk
        'type': 'Everyone', #can be: Everyone / Role / Player
        'challenged' : None, #challenged user/role id 
        'whitelist' : [], #list of user ids (int) (or 1 role id) 
        'authorJoined': False, #Needed when type = 'Role
    } #more info about how the challenge={} works is found below in the code

    #put args inside a list for "easier" parsing, also remove !chess since it's not needed
    args = ctx.message.content.replace('!chess ', '')
    print(f'chessGame: issued command: chess\nauthor: {ctx.message.author.id}, args: {args}')

    #useful for FENs: eg   (!chess) game fen="bla bla bla" < str.strip will return ["game", "fen=bla", "bla", "bla"]
    args = splitString(args)                    #wheras splitString will return ["game", "fen=", "bla", "bla", "bla"]
    gameFEN = ''
    gameBoard = settings[str(ctx.guild.id)]["chessGame"]["default_board"]
    design = 'default'
    
# 2. Parse args
    #2A. detect challenges
    if(len(args) >= 1 and args[0][:2] == '<@'): 
        if (args[0][:3] == '<@&'): #user challenged role
            challenge['type'] = 'Role'
            challenge['challenged'] = int(args[0][3:-1])
            challenge['whitelist'].append(int(challenge['challenged'])) #when checking: Delete if (user != author) so that author has a chance to join when multiple users with the role attempt to join
            await ctx.send(f'{ctx.message.author} Ha sfidato <@&{challenge["challenged"]}> a scacchi!')

        else:  #user challenged user
            challenge['type'] = 'User'
            challenge['challenged'] = int(args[0][2:-1])
            challenge['whitelist'].append(int(ctx.message.author.id))
            challenge['whitelist'].append(int(challenge['challenged'])) #when checking: delete users from here as they join
            await ctx.send(f'{ctx.message.author} Ha sfidato <@{challenge["challenged"]}> a scacchi!')

    #2B. detect commands / settings
    if len(args) >= 1:
        #a. Commands
        if args[0] == 'boards' or args[0] == 'board': #show board list
            #i. prepare the embed
            embed = discord.Embed(
                title = 'Scacchiere disponibili: ',
                colour = 0xf39641
            )

            #ii. append the global data boards to the embed
            botBoards = chessBridge.getBoards()
            value = ''
            for b in botBoards:
                value += f"**{b}**: {botBoards[b]}\n"
            embed.add_field(name = 'Scacchiere del bot:', value=value, inline=False)

            #iii. if guild data has boards, append them to the embed
            if settings[str(ctx.guild.id)]['chessGame']['boards'] != {}:
                guildBoards = ''
                for b in settings[str(ctx.guild.id)]['chessGame']['boards']:
                    guildBoards += f"**{b}**: {settings[str(ctx.guild.id)]['chessGame']['boards'][b]}\n"
                embed.add_field(name = f'Scacchiere di {ctx.guild.name}:', value=guildBoards, inline=False)
            
            #iv. send the embed
            await ctx.send(embed=embed)
            return 0

        elif args[0] == 'designs' or args[0] == 'design': #show board designs
            if len(args) == 1:
                #i. prepare the embed
                embed = discord.Embed(
                    title = 'Design disponibili: ',
                    colour = 0xf39641
                )

                #ii. append the global data designs to the embed
                botDesigns = chessBridge.chessMain.getDesignNames()
                value = ''
                for b in range(len(botDesigns)):
                    value += f"{botDesigns[b]}\n"

                embed.add_field(name = 'Design disponibili:', value=value, inline=False)

                #iii. if guild data has designs, append them to the embed
                if settings[str(ctx.guild.id)]['chessGame']['designs'] != {}:
                    guildDesigns = ''
                    for b in settings[str(ctx.guild.id)]['chessGame']['designs']:
                        guildDesigns += f"**{b}**: {settings[str(ctx.guild.id)]['chessGame']['designs'][b]}\n"
                    embed.add_field(name = f'Design di {ctx.guild.name}:', value=guildDesigns, inline=False)
                
                
                embed.add_field(name="\nComandi disponibili:\nPer creare una scacchiera: ", value="`!chess design add <nome> <colore1> <colore2>`", inline=False)
                embed.add_field(name="Per modificare una scacchiera: ", value="`!chess design edit <nome> <colore1> <colore2>`", inline=False)
                embed.add_field(name="Per eliminare una scacchiera: ", value="`!chess design del <nome>`", inline=False)
                embed.add_field(name="Per vedere una scacchiera: ", value="`!chess design see <nome>`\nI colori devono essere in formato HEX e.g.:`B00B1E` N.B. non mettere l'# in quanto discord può interpretarlo come un canale testuale", inline=False)

                #iv. send the embed
                await ctx.send(embed=embed)
                return 0
            
            #else
            if args[1] == 'see': #user wants the image of a design
                if(len(args) == 3):
                    #design exists in guildData
                    if args[2] in settings[str(ctx.guild.id)]['chessGame']['designs']:
                        colors = settings[str(ctx.guild.id)]['chessGame']['designs'][args[2]]
                        design = chessBridge.chessMain.gameRenderer.renderBoard(colors, ctx.message.id)
                        path = chessBridge.chessMain.gameRenderer.spritesFolder + design
                        with open(path+'chessboard.png', "rb") as fh:
                            f = discord.File(fh, filename=(path + 'chessboard.png'))
                            await ctx.send(file=f)
                        shutil.rmtree(path, ignore_errors=False, onerror=None)
                        return 0
                    
                    #design does not exist in guildData, search if exists in sprites folder
                    if chessBridge.chessMain.gameRenderer.doesDesignExist(args[2]):
                        design = f'{chessBridge.chessMain.gameRenderer.spritesFolder}{args[2]}/chessboard.png'
                        with open(design, "rb") as fh:
                            f = discord.File(fh, filename=design)
                            await ctx.send(file=f)
                    else:
                        await ctx.send("Design non trovato, usa `!chess design` per vedere i design disponibili")
                else:
                    await ctx.send('Usage: `!chess design see <name>`')
                return 0
            
            if args[1] == 'del': #delete a guild design
                if(len(args) >= 3):
                    selectedDesign = args[2:]
                    for d in selectedDesign: 
                        if d in settings[str(ctx.guild.id)]['chessGame']['designs']:
                            design = settings[str(ctx.guild.id)]['chessGame']['designs'].pop(d)
                            await ctx.send(f'Ho eliminato {d}: {design}')
                            dumpSettings()
                        else:
                            await ctx.send("Design non trovato, usa `!chess design` per vedere i design disponibili")
                else:
                    await ctx.send('Usage: `!chess design del <name>`')
                return 0
            
            def parseHEX(hex1, hex2) -> list:
                colors = [hex1, hex2]
                possible = ['#', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
                for i, hex in enumerate(colors): #foreach color
                    # if it has not an # add it
                    if hex[0] != '#': hex = '#' + hex
                    for char in hex: #check if color digits are valid
                        if char.lower() not in possible:
                            return '0'
                    if len(hex) == 4: #if the hex type is #fff expand it to #ffffff
                        hex = f'#{hex[1]}{hex[1]}{hex[2]}{hex[2]}{hex[3]}{hex[3]}'
                    if len(hex) != 7:
                        return '0'
                    colors[i] = hex

                return colors
                

            if args[1] == 'edit':
                #design edit name #0340430 #0359340
                if len(args) == 5:
                    if args[2] in settings[str(ctx.guild.id)]['chessGame']['designs']:
                        colors = parseHEX(args[3], args[4])
                        if colors == '0':
                            await ctx.send("Invalid hex")
                            return -2
                        settings[str(ctx.guild.id)]['chessGame']['designs'][args[2]] = colors
                        await ctx.send(f"Design modificato: **{args[2]}**: {colors}")
                        dumpSettings()
                    else:
                        await ctx.send("Design non trovato, usa `!chess design` per vedere i design disponibili")
                        return -2
                else:
                    await ctx.send('Usage: `!chess design edit <nome> <colore1> <colore2>`\ne.g.:`!chess design edit test1 #24AB34 #8E24FF`')
                return 0

            if args[1] == 'add':
                if len(args) == 5:
                    if args[2] in settings[str(ctx.guild.id)]['chessGame']['designs']:
                        await ctx.send(f'Il design esiste già. Usa `!chess design edit {args[2]} {args[3]} {args[4]} se vuoi modificarlo`')
                        return -2
                    colors = parseHEX(args[3], args[4])
                    if colors == '0':
                        await ctx.send("Invalid hex")
                        return -2
                    settings[str(ctx.guild.id)]['chessGame']['designs'][args[2]] = colors
                    await ctx.send(f"Design aggiunto: **{args[2]}**: {colors}")
                    dumpSettings()
                else:
                    await ctx.send('Usage: `!chess design add <nome> <colore1> <colore2>`\ne.g.:`!chess design edit test1 #24AB34 #8E24FF`')
                return 0

        elif args[0] == 'renderboard' or args[0] == 'render': # renders a FEN and send it in chat
            #i. avoid indexError because of the dumb user
            if len(args) >= 2:
                #ii. let the Engine make the image
                try:
                    image = chessBridge.getBoardImgPath(args[1], ctx.message.id)
                except Exception:
                    await ctx.send("Qualcosa è andato storto, probabilmente il FEN è errato")
                    return -2

                if image == 'Invalid':
                    await ctx.send('Invalid board')
                    return -1
                print(f'rendered image: {image}')

                #iii. Send the image to discord
                imgpath = (f'{image[0]}{image[1]}.png')
                logpath = (f'{image[0]}{"logs/"}{image[1]}.log')
                with open(imgpath, "rb") as fh:
                    f = discord.File(fh, filename=imgpath)
                    await ctx.send(file=f)
                #iv. data hoarding is bad
                os.remove(imgpath)
                os.remove(logpath)
            else:
                await ctx.send("Usage: `!chess render <name|FEN>`")
            return 0

        elif args[0] == 'addboard' or args[0] == 'add': #appends a board in the Data
            #i. avoid indexError because of the dumb user
            if len(args) == 3:
                #ii. check if the board does not exist
                if args[1] not in settings[str(ctx.guild.id)]['chessGame']['boards']:
                    #iii. append the board and dump the json data
                    settings[str(ctx.guild.id)]['chessGame']['boards'][args[1]] = args[2]
                    dumpSettings()
                    await ctx.send('Fatto!')
                else:
                    await ctx.sent('La schacchiera esiste già, usa\n`!chess boards` per vedere le scacchiere\n`!chess editboard <name> <FEN>` per modificare una scacchiera')
            else:
                await ctx.send("Usage: `!chess add <name> <FEN>`")
            return 0
        
        elif args[0] == 'renameboard' or args[0] == 'rename': #rename a board
            #i. avoid indexError because of the dumb user
            if len(args) == 3:
                #ii. copy the FEN
                value = settings[str(ctx.guild.id)]['chessGame']['boards'][args[1]]
                
                #iii. delete the board
                del settings[str(ctx.guild.id)]['chessGame']['boards'][args[1]]#it does not exist yet
                
                #iv. create a new board with the same FEN, but a new name and dump the json data
                settings[str(ctx.guild.id)]['chessGame']['boards'][args[2]] = value
                dumpSettings()
                await ctx.send('Fatto!')
            else:
                await ctx.send("Usage: `!chess rename <name> <newname>`")
            return 0
        
        elif args[0] == 'editboard' or args[0] == 'edit': #edit a board
           #i. avoid indexError because of the dumb user
            if len(args) == 3:
                #ii. Check if board exists, if not notify the user
                if args[1] not in  settings[str(ctx.guild.id)]['chessGame']['boards']:
                    await ctx.send(f"Non posso modificare qualcosa che non esiste ({args[1]})")
                    return -2

                #iii. edit the FEN, and dump the data
                settings[str(ctx.guild.id)]['chessGame']['boards'][args[1]] = args[2]
                dumpSettings()
                await ctx.send('Fatto!')
            else:
                await ctx.send("Usage: `!chess edit <name> <newFEN>`")
            return 0
        
        elif args[0] == 'deleteboard' or args[0] == 'delete': #deletes a board
            #i. avoid indexError because of the dumb user
            if len(args) == 2:
                #ii. Check if board exists, if not notify the user
                if args[1] in settings[str(ctx.guild.id)]['chessGame']['boards']:

                    #delete the board, dump the settings and send the FEN in chat
                    fen = settings[str(ctx.guild.id)]['chessGame']['boards'].pop(args[1])
                    dumpSettings()
                    await ctx.send(f'Fatto! FEN: {fen}')
                else:
                    await ctx.send(f"Non posso eliminare qualcosa che non esiste ({args[1]})")
                    return -2
            else:
                await ctx.send("Usage: `!chess delete <name>`")
            return 0
        
        #b. settings
        for i in args:
            if i.lower()[:4] == 'fen=':
                gameFEN = i[4:]
                print(f'found FEN -> {gameFEN}')

            if i.lower()[:6] == 'board=':
                gameBoard = i[6:]
                print(f'found board -> {gameFEN}')
            
            if i.lower()[:7] == 'design=':
                design = i[7:]
                print(f'found design -> {design}')

    #2C. double-check the data retreived
    board = ()
    if gameFEN != '': #if fen is provided, check if valid
        if('k' not in gameFEN or 'K' not in gameFEN):
            embed = discord.Embed(
                title = 'Problema con il FEN: manca il Re!',
                description= f'Re mancante: {"black" if "k" not in gameFEN else ""} {"white" if "K" not in gameFEN else ""}',
                color = 0xd32c41)
            await ctx.send(embed=embed)
            return -1
        #else, fen is valid
        board = ('FEN', gameFEN)

    else: #else, use board name
        #i. check if the board name is saved in guild data
        if gameBoard in settings[str(ctx.guild.id)]['chessGame']['boards']: #board in guild data
            board = ('FEN', settings[str(ctx.guild.id)]['chessGame']['boards'][gameBoard])
        #ii. if not, check if it's present in the global data
        elif chessBridge.doesBoardExist(gameBoard): #board in global data
            board = ('BOARD', gameBoard)
        #iii. if not, the user is dumb
        else: #board not found
            embed = discord.Embed(title = f'Errore 404, non trovo {gameBoard} tra le scacchiere salvare 😢\n riprova',color = 0xd32c41)
            await ctx.send(embed=embed)
            return -1
    
    designName = design
    if designName != 'default': #if user asked for a design, check if it exists
        #give priority to guild designs
        if design in settings[str(ctx.guild.id)]['chessGame']['designs']:
            designName = design
            design = settings[str(ctx.guild.id)]['chessGame']['designs'][design]
            design = chessBridge.chessMain.gameRenderer.renderBoard(design, ctx.message.id)
        elif not chessBridge.chessMain.gameRenderer.doesDesignExist(design):
            designName = 'default'
            design = 'default'
        else:
            designName = design
    

# 3. All seems good, now let's send the embed to find some players
    #3A. Challenge one user
    if challenge['type'] == 'User': 
        challengedUser = ctx.guild.get_member(int(challenge['challenged'])) #await bot.fetch_user(challenged)
        embed = discord.Embed(title = f'@{challengedUser.name}, sei stato sfidato da {ctx.message.author}!\nUsate una reazione per unirti ad un team (max 1 per squadra)',
            description=f'Scacchiera: {board[1]}, design: {designName}',
            color = 0x0a7ace)
        
    #3B. Challenge one guild
    elif challenge['type'] == 'Role':
        challengedRole = ctx.guild.get_role(int(challenge['challenged']))
        embed = discord.Embed(title = f'@{challengedRole.name}, siete stati sfidati da {ctx.message.author}!\nUno di voi può unirsi alla partita!',
            description=f'Scacchiera: {board[1]}, design: {designName}',
            color = 0x0a7ace)

    #3C. Challenge everyone
    else:
        embed = discord.Embed(title = f'Cerco giocatori per una partita di scacchi! ♟,\nUsa una reazione per unirti ad un team (max 1 per squadra)',
            description=f'Scacchiera: {board[1]}, design: {designName}',
            color = 0x0a7ace).set_footer(text=f'Partita richiesta da {ctx.message.author}')
    
    #3D. SEND THE EMBED FINALLY
    playerFetchMsg = await ctx.send(embed=embed)
    
#4. Await player joins
    #4A. setting up
    reactions = ('⚪', '🌑') #('🤍', '🖤')
    r1, r2 = reactions

    availableTeams = [reactions[0], reactions[1]] # Needed to avoid players from joining the same team
    players = [0, 0] #this will store discord.Members

    print('chessGame: challenge["whitelist"]')
    print(challenge['whitelist'])

    #add reactions to the embed that people can use as buttons to join the teams
    await playerFetchMsg.add_reaction(r1)
    await playerFetchMsg.add_reaction(r2)
    await playerFetchMsg.add_reaction("❌") #if the author changes their mind


    def fetchChecker(reaction, user) -> bool: #this is one fat checker damn
        """Checks if user team join request is valid"""

        # async def remove(reaction, user): #remove invalid reactions
        #     await reaction.remove(user)   #will figure out some way

        print('chessGame: check1')
        print(f'chessGame: Check: {reaction}, {user}\nchallenge["whitelist"]: {challenge["whitelist"]}\navailable: {availableTeams}\n--------')
        
        #1- prevent bot from joining teams
        if (user == bot.user): 
            return False

        if(str(reaction.emoji) == "❌" and user == ctx.message.author):
            return True #only the author can cancel the search

        #2- check if color is still available (prevent two players from joining the same team)
        if(str(reaction.emoji) not in availableTeams):
            return False #remember to remove the reaction before every return True

        userID = int(user.id)
        
        #3a- If player challenged a user:
        if(challenge['type'] == 'User'): 
            #check if joining player is in whitelist
            if userID not in challenge['whitelist']: return False
            
            challenge['whitelist'].remove(userID) #prevent user from rejoining another team
            availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
            return True

        #3b- If player challenged a role:
        elif(challenge['type'] == 'Role'):
            challengedRole = challenge['challenged'] #challeng has only one entry containing the role id
            
            #if the user joining is the author:
            if user == ctx.message.author and challenge['authorJoined'] == False: #the message author can join even if he does not have the role
                print('chessGame: User is author') #check the user BEFORE the role, so if the user has the role it does not get deleted
                challenge['authorJoined'] = True #prevent author from joining 2 teams
                availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
                return True 
            
            #if the user joining isn't the author but has the role requested
            elif user.get_role(challengedRole) != None: #user has the role  
                print('chessGame: User has required role')
                challenge['whitelist'] = [] #delete the role to prevent two players with the role from joining (keeping out the author)
                availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
                return True

            print(f'chessGame: User {user.name} is not allowerd to join (Role challenge)')
            return False

        #3c- If player challenged everyone:
        else: #no need to check who joins (can also play with yourself)
            availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
            return True

        # fetchChecker end #

    #4B. await user joins (with reactions)
    async def stopsearch():
        embed.title = "Ricerca annullata"
        embed.description = ""
        embed.color = 0xdc143c

        designFolder = f'{chessBridge.chessMain.gameRenderer.spritesFolder}{design}'
        if design.find('\\') != -1 or design.find('/') != -1:
            shutil.rmtree(designFolder)
        await playerFetchMsg.clear_reactions()
        await playerFetchMsg.edit(embed=embed)

    try:
        #i. await first player
        r1, players[0] = await bot.wait_for('reaction_add', timeout=60.0, check=fetchChecker)
        if str(r1.emoji) == "❌": 
            await stopsearch()
            return -2
        embed.description += f'\n{players[0]} si è unito a {r1}!'
        await playerFetchMsg.edit(embed=embed)
        

        #ii. await second player
        r2, players[1] = await bot.wait_for('reaction_add', timeout=60.0, check=fetchChecker)
        if str(r2.emoji) == "❌": 
            await stopsearch()
            return -2
        embed.description += f'\n{players[1]} si è unito a {r2}!\nGenerating game please wait...'
        embed.set_footer(text = 'tutti i caricamenti sono ovviamente falsissimi.')
        
        embed.color = 0x77b255
        await playerFetchMsg.edit(embed=embed)
        #iii. fake sleep for professionality
        await asyncio.sleep(random.randrange(2,4))

    except asyncio.TimeoutError: #players did not join in time
        embed = discord.Embed(
            title = 'Non ci sono abbastanza giocatori.',
            colour = 0xdc143c
        )
        await ctx.send(embed=embed)
        await playerFetchMsg.delete()
        return -1

    else: #players did join in time

        if r1 == reactions[0]: #first player choose white
            player1 = players[1] #white
            player2 = players[0] #black
        else: #first player choose black
            player1 = players[0] #white
            player2 = players[1] #black

        #iv. Send an embed with the details of the game
        embed = discord.Embed(
            title = f'Giocatori trovati\n{r1} {player1} :vs: {player2} {r2}',
            description=f"Impostazioni:\n- Scacchiera: {board[1]}, Design: {designName}",
            colour = 0x27E039
        )
        
        #v. start a thread where the game will be disputed, join the players in there
        thread = await ctx.send(embed=embed)
        gameThread = await thread.create_thread(name=(f'{str(player1)[:-5]} -VS- {str(player2)[:-5]}'), auto_archive_duration=60, reason='Scacchi')
        await gameThread.add_user(player1)
        await gameThread.add_user(player2)
        await playerFetchMsg.delete()
        mainThreadEmbed = (thread, embed)

#5. FINALLY, start the game
        await chessBridge.loadGame(gameThread, bot, [player1, player2], mainThreadEmbed, board, design)
        #                                        #send them backwards (info on chessBrige.py) [black, white]
        await gameThread.edit(archived=True, locked=True)
        designFolder = f'{chessBridge.chessMain.gameRenderer.spritesFolder}{design}'
        if design.find('\\') != -1 or design.find('/') != -1:
            shutil.rmtree(designFolder)

@bot.event   ## DETECT AND RESPOND TO MSG
async def on_message(message : discord.Message):
    await bot.process_commands(message)

    respSettings = settings[str(message.guild.id)]["responseSettings"]

    #don't respond to self, commands, messages with less than 2 words
    if message.author == bot.user or message.content[0] in ['!', "/", "?", '|', '$', "&", ">", "<"] or len(message.content.split()) < 2: return

    

    if 'word' in message.content: #for future implementation, respond to specific string
        pass
        
#---------------------------------------------- This is specific to a server
    if message.author.id == 438269159126859776 and message.guild.id == 694106741436186665:
        if random.randrange(1, 100) < respSettings["response_to_bots_perc"]:
            await asyncio.sleep(random.randrange(1, 3))
            m = ''
            with open('botFiles/antiButt.txt', 'r') as lines:
                m = random.choice(lines.read().splitlines())
            await message.reply(m, mention_author=False)
            if random.randrange(1, 100) < respSettings["response_to_bots_perc"]/2:
                r = random.choice(['🤣', '😂', '🤢', '🤡'])
                await message.add_reaction(r)
        return
##---------------------------------------------- you can safely delete until here
    
    #if guild does not want bot responses and sender is a bot, ignore the message
    if message.author.bot and not respSettings["will_respond_to_bots"]: return 0

    #culificazione
    articoli = ['il', 'lo', 'la', 'i', 'gli', 'le'] #Italian specific
 
    if random.randrange(1, 100) > respSettings["response_perc"]: #implement % of answering
        return

    msg = message.content.split() #trasforma messaggio in lista
    
    for i in range(len(msg) // 2): #culifico al massimo metà delle parole
        scelta = random.randrange(1, len(msg)) #scegli una parola

        # se la parola scelta è un articolo (e non è l'ultima parola), cambio la prossima parola
        # e.g "ciao sono il meccanico" (se prendo la parola DOPO "il") -> "ciao sono il culo"   
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

        if(random.randrange(1, 100) > respSettings['other_response']):
           i+=1
        i+=1

    msg = " ".join(msg) #trasforma messaggio in stringa

    await message.reply(msg, mention_author=False)
    print('responded')
    log(f'[INFO]: responded to message <resp_rate: {respSettings["response_perc"]}%>')


loadSettings()

# updateSettings("694106741436186665", 'response', 534) #testing purposes

bot.run(TOKEN)
