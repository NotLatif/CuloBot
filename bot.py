import asyncio
import os
import json
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

#TODO add "customwords": [,] to settings for server distinct words

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

settingsFile = "settingsData.json"
settings = {}
with open(settingsFile, 'a'): pass #make setting file if it does not exist

def updateSettings(id, setting = None, value = None, reset = False, category = "responseSettings"):
    id = str(id)
    if setting != None:
        for s in settings[id][category]:
            if s == setting:
                settings[id][category][s] = value
        print('settings updated for ' + str(id))
        with open(settingsFile, 'w') as f:
            json.dump(settings, f, indent=2)
        return
    
    elif reset: #if only id is given, we want to append a new server
        template = {"id": {"responseSettings": {"response":35,"other_response":20,"responsetobots":25,"willRepondToBots":True},"chessGame": {"test": False}}}
        with open(settingsFile, 'r') as f:
            temp = json.load(f)
        temp[id] = template["id"]
        with open(settingsFile, 'w') as fp:
            json.dump(temp, fp , indent=2)
    

def loadSettings():
    template = {"id": "placeholder"}
    global settings
    try:
        with open(settingsFile, 'r') as f:
            settings = json.load(f)
    except json.JSONDecodeError: #file is empty
        with open(settingsFile, 'w') as fp:
            json.dump(template, fp , indent=2)
        return 0

loadSettings()     

# updateSettings("694106741436186665", 'response', 534) #testing purposes

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

        

"""
settings:
response = int:         % di probabilità di culificare un messaggio (0 <= int <= 100)
                        - default: 35, minimo 2 parole
other_response = int:   % di possibilità di culificare più di una parola   (0 <= int <= 100)
                        - default: 50, 1 culo ogni due parole
                        - ogni parola ha il 50% di probabilità di essere cambiata rispetto alla precedente                       
"""
    

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
        if (str(guild.id) not in settings):
            print('^ Generating settings for guild')
            updateSettings(str(guild.id, reset=True))


    #channel = bot.get_channel(972610894930538507)
    #await channel.send("hello world")

@bot.event 
async def on_member_join(member : discord.Member):
    await member.guild.system_channel.send(f'A {member.name} piace il culo.')   
    print("join detected")

@bot.command(name='resp') 
async def perc(ctx):  ## BOT COMMAND
    arg = ctx.message.content.replace('!resp', '')
    setting = settings[str(ctx.guild.id)]["responseSettings"]

    if(arg == ''):
        await ctx.send(f'Rispondo il {setting["response"]}% delle volte')
        return
    
    arg = arg.lower().split()

    affirmative = ['true', 'yes', 'si', 'vero']
    negative = ['false', 'no', 'false']
    validResponse = False
    if(arg[0].strip('s') == 'bot'):
        print(arg)
        if len(arg) == 1:
            await ctx.send(f'Risposta ai bot: {setting["willRepondToBots"]}\nRispondo ai bot il {setting["responsetobots"] if setting["willRepondToBots"] else 0}% delle volte')
            return

        if(arg[1].isnumeric()):
            await ctx.send(f'Okay, risponderò ai bot il {arg[1]}% delle volte')
            updateSettings(str(ctx.guild.id), 'responsetobots', int(arg[1]))
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
            updateSettings(ctx.guild.id, 'willRepondToBots', arg[1])
            return

    newPerc = int(arg[0].strip("%"))

    if (setting['response'] == newPerc):
        await ctx.send(f"non è cambiato niente.")
        return

    setting["response"] = newPerc
    await ctx.send(f"ok, risponderò il {newPerc}% delle volte")

    log(f'[INFO]: {ctx.author} set response to {arg}%')
    updateSettings(str(ctx.guild.id) , 'response', newPerc)
    updateSettings(str(ctx.guild.id) , 'other_response', newPerc//2)

@bot.command(name = 'help')
async def embedpages(ctx):
    page1 = discord.Embed (
        title = 'CuloBot',
        description = 'I comandi vanno preceduti da "!", questo bot fa uso di ignoranza artificiale',
        colour = 0xf39641
    ).set_footer(text='Ogni cosa è stata creata da @NotLatif, se riscontrare bug sapete a chi dare la colpa.')
    page2 = discord.Embed(
        title = 'CuloBot',
        description = 'I comandi vanno preceduti da "!", questo bot fa uso di ignoranza artificiale',
        colour = 0xf39641
    ).set_footer(text='Ogni cosa è stata creata da @NotLatif, se riscontrare bug sapete a chi dare la colpa.')
    page3 = discord.Embed(
        title = 'CuloBot',
        description = 'I comandi vanno preceduti da "!", questo bot fa uso di ignoranza artificiale',
        colour = 0xf39641
    ).set_footer(text='Ogni cosa è stata creata da @NotLatif, se riscontrare bug sapete a chi dare la colpa.')
    

    page1.set_thumbnail(url='https://i.pinimg.com/originals/b5/46/3c/b5463c3591ec63cf076ac48179e3b0db.png')
    page1.set_author(name='Help', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page2.set_thumbnail(url='https://i.pinimg.com/originals/b5/46/3c/b5463c3591ec63cf076ac48179e3b0db.png')
    page2.set_author(name='Help', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page3.set_thumbnail(url='https://i.pinimg.com/originals/b5/46/3c/b5463c3591ec63cf076ac48179e3b0db.png')
    page3.set_author(name='Help', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    
    page1.add_field(name='!resp', value='Chiedi al bot la percentuale di culificazione', inline=False)
    page1.add_field(name='!resp [x]%', value='Imposta la percentuale di culificazione a [x]%', inline=False)
    page1.add_field(name='!resp bot', value= 'controlla le percentuale di risposta verso gli altri bot', inline=False)
    page1.add_field(name='!resp bot [x]%', value= 'Imposta la percentuale di culificazione contro altri bot a [x]%', inline=False)
    page1.add_field(name='!resp bot [True|False]', value= 'abilita/disabilita le culificazioni di messaggi di altri bot', inline=False)



    page2.add_field(name='!ping', value='Pong!', inline=False)
    page2.add_field(name='!chess', value='Gioca a scacchi contro un amico', inline=False)
    page2.add_field(name='!chess [@user]', value='Sfida una persona a scacchi!', inline=False)
    page2.add_field(name='!chess [@role]', value='Sfida un ruolo a scacchi!', inline=False)


    page1.add_field(name='Source code', value="https://github.com/NotLatif/CuloBot", inline=False)
    page1.add_field(name='Problemi? lascia un feedback qui', value="https://github.com/NotLatif/CuloBot/issues", inline=False)
    

    pages = [page1, page2, page3]

    msg = await ctx.send(embed = page1)

    await msg.add_reaction('⏮')
    await msg.add_reaction('◀')
    await msg.add_reaction('▶')
    await msg.add_reaction('⏭')
    
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
async def ping(ctx):
    pingms = round(bot.latency*1000)
    await ctx.send(f'Pong! {pingms}ms')
    log(f'[INFO]: ping detected: {pingms} ms')

@bot.command(name='user')
async def user(ctx):
    await ctx.send(f'User: {bot.user}')

@bot.command(name='chess', pass_context=True)
async def chessGame(ctx, args=''):
    challenge = { #need dict otherwise script dumps some of the variables idk
        'type': 'Everyone', 
        'challenged' : None, #challenged user/role id
        'whitelist' : [], #list of user ids (int) (or 1 role id)
        'authorJoined': False, #Needed when type = 'Role
    }
    print(f'chessGame: issued command: chess\nauthor: {ctx.message.author.id}, args: {args}')

    #detect any challenges
    if(args != '' and args[:2] == '<@'):
        if (args[:3] == '<@&'): #user challenged role
            challenge['type'] = 'Role'
            challenge['challenged'] = int(args[3:-1])
            challenge['whitelist'].append(int(challenge['challenged'])) #when checking: Delete if (user != author) so that author has a chance to join when multiple users with the role attempt to join
            await ctx.send(f'{ctx.message.author} Ha sfidato <@&{challenge["challenged"]}> a scacchi!')

        else:  #user challenged user
            challenge['type'] = 'User'
            challenge['challenged'] = int(args[2:-1])
            challenge['whitelist'].append(int(ctx.message.author.id))
            challenge['whitelist'].append(int(challenge['challenged'])) #when checking: delete users from here as they join
            await ctx.send(f'{ctx.message.author} Ha sfidato <@{challenge["challenged"]}> a scacchi!')
    
    # Send the embed
    if challenge['type'] == 'User': #challenge one User
        await ctx.message.delete()
        challengedUser = ctx.guild.get_member(int(challenge['challenged'])) #await bot.fetch_user(challenged)
        embed = discord.Embed(title = f'@{challengedUser.name}, sei stato sfidato da {ctx.message.author}!\nUsate una reazione per unirti ad un team (max 1 per squadra)',
            color = 0x0a7ace)
        
    elif challenge['type'] == 'Role': #challenge one Role
        await ctx.message.delete()
        challengedRole = ctx.guild.get_role(int(challenge['challenged']))
        embed = discord.Embed(title = f'@{challengedRole.name}, siete stati sfidati da {ctx.message.author}!\nUno di voi può unirsi alla partita!',
            color = 0x0a7ace)

    else: #challenge everyone
        embed = discord.Embed(title = 'Cerco giocatori per una partita di scacchi! ♟,\nUsa una reazione per unirti ad un team (max 1 per squadra)',
            color = 0x0a7ace).set_footer(text=f'Partita richiesta da {ctx.message.author}')
    
    playerFetchMsg = await ctx.send(embed=embed)
    
    reactions = ('⚪', '🌑') #('🤍', '🖤')
    r1, r2 = reactions
    await playerFetchMsg.add_reaction(r1)
    await playerFetchMsg.add_reaction(r2)

    availableTeams = [reactions[0], reactions[1]]
    print('chessGame: challenge["whitelist"]')
    print(challenge['whitelist'])

    def fetchChecker(reaction, user) -> bool: #this is one fat checker damn
        # async def remove(reaction, user): #remove invalid reactions
        #     await reaction.remove(user)   #will figure out some way

        userID = int(user.id)
        print('chessGame: check1')
        print(f'chessGame: Check: {reaction}, {user}\nchallenge["whitelist"]: {challenge["whitelist"]}\navailable: {availableTeams}\n--------')
        if (user == bot.user): #prevent bot from joining teams
            return False

        #check if color is still available
        if(str(reaction.emoji) not in availableTeams):
            return False #remember to remove the reaction before every return True

        #whitelisted join (user mentions someone)
        if(challenge['type'] == 'User'): #check if joining player is in list
            if userID not in challenge['whitelist']: return False
            
            challenge['whitelist'].remove(userID) #prevent user from rejoining another team
            availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
            return True

        elif(challenge['type'] == 'Role'):
            challengedRole = challenge['challenged'] #the only entry
            
            if user == ctx.message.author and challenge['authorJoined'] == False: #the message author can join even if he does not have the role
                print('chessGame: User is author') #check the user BEFORE the role, so if the user has the role it does not get deleted
                challenge['authorJoined'] = True #prevent author from joining 2 teams
                availableTeams.remove(str(reaction.emoji))
                return True 
            
            elif user.get_role(challengedRole) != None: #user has the role  
                print('chessGame: User has required role')
                challenge['whitelist'] = [] #delete the role so that message author can join
                availableTeams.remove(str(reaction.emoji))
                return True

            print(f'chessGame: User {user.name} is not allowerd to join (Role challenge)')
            return False

        else: #no need to check who joins (can also play with yourself)
            availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
            return True


    players = [0, 0]
    try:    #I need two wait_for (one for each team)
        r1, players[0] = await bot.wait_for('reaction_add', timeout=60.0, check=fetchChecker)
        embed.description = f'{players[0]} si è unito a {r1}!'
        await playerFetchMsg.edit(embed=embed)

        r2, players[1] = await bot.wait_for('reaction_add', timeout=60.0, check=fetchChecker)
        embed.description += f'\n{players[1]} si è unito a {r2}!\nGenerating game please wait...'
        embed.set_footer(text = 'tutti i caricamenti sono ovviamente falsissimi.')
        embed.color = 0x77b255
        
        await playerFetchMsg.edit(embed=embed)
        await asyncio.sleep(random.randrange(2,4))

    except asyncio.TimeoutError:
        embed = discord.Embed(
            title = 'Non ci sono abbastanza giocatori.',
            colour = 0xdc143c
        )
        await ctx.send(embed=embed)
        await playerFetchMsg.delete()
        return -1
    else:
        if r1 == reactions[0]: #first player choose white
            player1 = players[1] #white
            player2 = players[0] #black
        else: #first player choose black
            player1 = players[0] #white
            player2 = players[1] #black

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

    #game main                                  #send them backwards (info on chessBrige.py) [black, white]
    await chessBridge.loadGame(gameThread, bot, [player2, player1], mainThreadEmbed)


@bot.event   ## DETECT AND RESPOND TO MSG
async def on_message(message : discord.Message):
    setting = settings[str(message.guild.id)]["responseSettings"]

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
        if random.randrange(1, 100) < setting["responsetobots"]: #implement % of answering
            await asyncio.sleep(random.randrange(1, 3))
            m = ''
            with open('antiButt.txt', 'r') as lines:
                m = random.choice(lines.read().splitlines())
            await message.reply(m, mention_author=False)
            if random.randrange(1, 100) < setting["responsetobots"]/2:
                r = random.choice(['🤣', '😂', '🤢', '🤡'])
                await message.add_reaction(r)
        return

    #culificazione
    articoli = ['il', 'lo', 'la', 'i', 'gli', 'le']
    if message.author == bot.user or len(message.content.split()) < 2 or message.content[0] == '!':
        return  #don't respond to: self, strings with < 2 words, commands
 
    if random.randrange(1, 100) > setting["response"]: #implement % of answering
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

        if(random.randrange(1, 100) > setting['other_response']):
           i+=1
        i+=1

    msg = " ".join(msg) #trasforma messaggio in stringa

    await message.reply(msg, mention_author=False)
    print('responded')
    log(f'[INFO]: responded to message <resp_rate: {setting["response"]}%>')


bot.run(TOKEN)

#TODO comando per vedere la lista delle parole
#TODO comando per togliere/aggiungere parole dalla lista