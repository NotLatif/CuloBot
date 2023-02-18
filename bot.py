#version in line 1 of ./changelog.md
import asyncio
import os
import shutil
import json
import random
import copy
import sys
import traceback
import discord
from discord.utils import get
from datetime import datetime
from discord import app_commands
from typing import Union

#custom modules
sys.path.insert(0, 'utils/')
sys.path.insert(0, 'music/')
sys.path.insert(0, 'chessGame/')
#utils
import config
import getevn
from config import Colors as col
from mPrint import mPrint as mp
from lang import it as lang # Change it with your language, currently supported: it
#music and chessGame
import chessBridge
import musicBridge

def mPrint(tag, value):mp(tag, 'bot', value)

try: #This is specific to my own server, if you want to delete it search for the string "ZXCV"
    import NotLatif
    CUSTOM_MODULES = True
except ModuleNotFoundError:
    CUSTOM_MODULES = False

TOKEN = getevn.getenv('DISCORD_TOKEN', True)
OWNER_ID = int(getevn.getenv('OWNER_ID')) #(optional) needed for the bot to send you feedback when users use /feedback command
                                          # you will still see user-submitted feedback in the feedback.log file (will be createt automatically if not present)

intents = discord.Intents.all()
intents.members = True
intents.messages = True

settingsFile = "botFiles/guildsData.json"

global settings
settings = {}
with open(settingsFile, 'a'): pass #make guild setting file if it does not exist

SETTINGS_TEMPLATE = {"id":{"responseSettings":{"disabled_channels":[],"join_message":"%name% likes butt!","leave_message":"Bye %name%, never come back","send_join_msg":False,"send_leave_msg":False,"response_perc":35,"other_response":9,"response_to_bots_perc":35,"will_respond_to_bots":False,"use_global_words":False,"custom_words":["butt"]},"chessGame":{"disabled_channels":[],"default_board":"default","boards":{},"default_design":"default","designs":{}},"musicbot":{"player_shuffle": True,"enable_database":False,"disabled_channels":[],"saved_playlists":{},"youtube_search_overwrite":{},"timeline_precision": 14}}}


#Useful funtions
def dumpSettings(): #only use this function to save data to guildData.json (This should avoid conflicts with coroutines idk)
    """Saves the settings to file"""
    dump = {str(k): settings[k] for k in settings}
    with open(settingsFile, 'w') as f:
        json.dump(dump, f, indent=2)

def loadSettings():
    template = {}
    global settings
    try:
        with open(settingsFile, 'r') as f:
            settings = json.load(f)
    except json.JSONDecodeError: #file is empty FIXME testing, what if file is not empty and it's a decode error?
        with open(settingsFile, 'w') as fp:
            json.dump(template, fp , indent=2)
        return 0

    settings = {int(k): settings[k] for k in settings}

def createSettings(id : int): #creates settings for new guilds
    id = int(id)
    with open(settingsFile, 'r') as f:
        temp = json.load(f)
    temp[id] = SETTINGS_TEMPLATE["id"]

    with open(settingsFile, 'w') as f:
        json.dump(temp, f, indent=2)

    loadSettings()
  
def checkSettingsIntegrity(id : int):
    id = int(id)
    mPrint('DEBUG', f'Checking guildData integrity')

    try:
        settingsToCheck = copy.deepcopy(settings[id])
    except KeyError:
        mPrint('FATAL', f'Settings for guild were not initialized correctly\n{traceback.format_exc()}')
        sys.exit(-1)

    #check if there is more data than there should
    for key in settingsToCheck:
        if(key not in SETTINGS_TEMPLATE["id"]): #check if there is a key that should not be there (avoid useless data)
            del settings[id][key]
            mPrint('DEBUG', f'Deleting: {key}')

        if(type(settingsToCheck[key]) == dict):
            #if(key in ["saved_playlists", "youtube_search_overwrite"]): continue #whitelist
            for subkey in settingsToCheck[key]:
                if(subkey not in SETTINGS_TEMPLATE["id"][key]): #check if there is a subkey that should not be there (avoid useless data)
                    del settings[id][key][subkey]
                    mPrint('DEBUG', f'Deleting: {subkey}')

    #check if data is missing
    for key in SETTINGS_TEMPLATE["id"]:
        if(key not in settings[id]): #check if there is a key that should not be there (avoid useless data)
            settings[id][key] = SETTINGS_TEMPLATE["id"][key]
            mPrint('DEBUG', f'Creating key: {key}')

        #it it's a dict also check it's keys
        if(type(SETTINGS_TEMPLATE["id"][key]) == dict):
            for subkey in SETTINGS_TEMPLATE["id"][key]:
                if(subkey not in settings[id][key]): #check if there is a key that should not be there (avoid useless data)
                    settings[id][key][subkey] = SETTINGS_TEMPLATE["id"][key][subkey]
                    mPrint('DEBUG', f'Creating subkey: {subkey}')

    dumpSettings()

    mPrint('INFO', f'GuildSettings for {id} seem good.')

def getWord(all=False) -> Union[str, list]:
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


#           -----           DISCORD BOT            -----       #
class MyBot(discord.Client):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.isReady = False

    async def on_error(self, *args, **kwargs):
        mPrint('ERROR', f"DISCORDPY on_error:\n{traceback.format_exc()}")
        mPrint('WARN', "ARGS:")
        for x in args:
            mPrint('ERROR', {x})

    async def on_guild_join(self, guild:discord.Guild):
        mPrint("INFO", f"Joined guild {guild.name} (id: {guild.id})")

        members = '\n - '.join([member.name for member in guild.members])
        mPrint('DEBUG', f'Guild Members:\n - {members}')
        if (int(guild.id) not in settings):
            mPrint('DEBUG', f'^ Generating settings for guild {int(guild.id)}')
            createSettings(int(guild.id))
        else:
            mPrint('DEBUG', f'settings for {int(guild.id)} are present in {settings}')

        checkSettingsIntegrity(int(guild.id))

        # voice_client : discord.VoiceClient = get(bot.voice_clients, guild=guild)
        # if voice_client != None and voice_client.is_connected():
        #     await voice_client.disconnect()

    async def on_guild_remove(self, guild:discord.Guild):
        pass
    
    async def on_ready(self):
        try:
            self.dev = await bot.fetch_user(OWNER_ID)
        except discord.errors.NotFound:
            self.dev = None
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))
        await tree.sync()

        mPrint("DEBUG", "Called on_ready")
        if len(sys.argv) == 5 and sys.argv[1] == "RESTART":
            mPrint("INFO", "BOT WAS RESTARTED")
            guild = await bot.fetch_guild(sys.argv[2])
            channel = await guild.fetch_channel(sys.argv[3])
            message = await channel.fetch_message(sys.argv[4])
            await message.reply("Bot restarted")
            
        mPrint("INFO", f'Connected to {len(bot.guilds)} guild(s):')
        for guild in bot.guilds:
            mPrint('DEBUG', f'Checking {guild.id}')
            if (int(guild.id) not in settings):
                mPrint('DEBUG', f'^ Generating settings')
                createSettings(int(guild.id))
            else:
                mPrint('DEBUG', f'settings for are present.')

            checkSettingsIntegrity(int(guild.id))
        
        if not self.isReady:
            # Ensure that on_ready will only run 1 time
            self.isReady = True

    async def on_member_join(self, member : discord.Member):
        if settings[int(member.guild.id)]['responseSettings']['send_join_msg']:
            joinString:str = settings[int(member.guild.id)]['responseSettings']['join_message']
            joinString = joinString.replace('%name%', member.name)
            await member.guild.system_channel.send(joinString)
#--------------------------------- This is specific to my server---# ZXCV
        if CUSTOM_MODULES and member.guild.id == 694106741436186665:          #  There is another block like this 
            await NotLatif.joinImageSend(member, member.guild)     #    a little below this one
#--------------------------------- you can safely delete this------# 

    async def on_member_remove(self, member : discord.Member):
        if settings[int(member.guild.id)]['responseSettings']['send_leave_msg']:
            leaveString:str = settings[int(member.guild.id)]['responseSettings']['leave_message']
            leaveString= leaveString.replace('%name%', member.name)
            await member.guild.system_channel.send(leaveString)
    
    async def on_guild_available(self, guild : discord.Guild):
        pass

    async def on_message(self, message : discord.Message):
        if len(message.content.split())==0: return
        global settings

        try:
            respSettings = settings[int(message.guild.id)]["responseSettings"]
        except AttributeError:
            return #this gets triggered with ephemeral messages

#--------------------------------- This is specific to my server---# ZXCV
        if CUSTOM_MODULES and message.content[0] == '!' and  message.author.id == 348199387543109654:
            await NotLatif.parseCmd(message, settings)
            return
#--------------------------------- you can safely delete this------# 

        if message.channel.id in settings[message.guild.id]['responseSettings']['disabled_channels']:
            return #module is in blacklist for this channel

        #don't respond to self, commands, messages with less than 2 words
        if message.author.id == bot.user.id or message.content[0] in ["!", "/", "?", "|", '$', "&", ">", "<"] or len(message.content.split()) < 2:
            return

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
        mPrint('DEBUG', f'Ho risposto ad un messaggio.')


bot = MyBot(intents = intents)
tree = app_commands.CommandTree(bot)



#           -----           DISCORD BOT SLASH COMMANDS           -----       #

@tree.command(name="join-msg", description=lang.slash.join_msg)
async def joinmsg(interaction : discord.Interaction, message : str = None, enabled : bool = None):
    mPrint('CMDS', f'called /join-msg {message}')
    guildID = int(interaction.guild.id)

    if enabled != None:
        settings[guildID]['responseSettings']['send_join_msg'] = enabled
        dumpSettings()

    if message != None: #edit join-message or show help
        settings[guildID]['responseSettings']['join_message'] = message
        dumpSettings()

    embed = discord.Embed(
        title=lang.commands.join_msg_embed_title,
        description=lang.commands.join_msg_embed_desc(settings[guildID]['responseSettings']['send_join_msg'], settings[guildID]['responseSettings']['join_message']),
        color=col.orange
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="leave-msg", description=lang.slash.leave_msg)
async def leavemsg(interaction : discord.Interaction, message : str = None, enabled : bool = None):
    mPrint('CMDS', f'called /leave-msg {message}')
    guildID = int(interaction.guild.id)

    if enabled != None:
        settings[guildID]['responseSettings']['send_leave_msg'] = enabled
        dumpSettings()

    if message != None: #edit join-message or show help
        settings[guildID]['responseSettings']['leave_message'] = message
        dumpSettings()
    
    embed = discord.Embed(
        title=lang.commands.leave_msg_embed_title,
        description=lang.commands.leave_msg_embed_desc(settings[guildID]['responseSettings']['send_leave_msg'], settings[guildID]['responseSettings']['leave_message']),
        color=col.orange
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="respond-perc", description=lang.slash.respond_perc)
async def responsePerc(interaction : discord.Interaction, value : int = -1):
    mPrint('CMDS', f'called /respond-perc {value}')
    guildID = int(interaction.guild.id)

    respSettings = settings[guildID]["responseSettings"] #readonly 

    if(value == -1):
        await interaction.response.send_message(lang.commands.resp_info(str(respSettings["response_perc"])))
        return
    
    elif (respSettings['response_perc'] == value):
        await interaction.response.send_message(lang.nothing_changed)
        return
    #else
    #keep value between 0 and 100
    value = 100 if value > 100 else 0 if value < 0 else value

    await interaction.response.send_message(lang.commands.resp_newperc(value))

    mPrint('INFO', f'{interaction.user.name} set response to {value}%')
    settings[guildID]['responseSettings']['response_perc'] = value
    dumpSettings()

@tree.command(name="respond-to-bots", description=lang.slash.respond_to_bots)
async def botRespToggle(interaction : discord.Interaction, value : bool):
    mPrint('CMDS', f'called /respond-to-bots {value}')
    guildID = int(interaction.guild.id)
        
    if value == True:
        response = lang.commands.resp_resp_to_bots_affirmative
    else:
        response = lang.commands.resp_resp_to_bots_negative
    await interaction.response.send_message(response)

    settings[guildID]['responseSettings']['will_respond_to_bots'] = value
    dumpSettings()
    return

@tree.command(name="respond-to-bots-perc", description=lang.slash.respond_to_bots_perc)
async def botRespPerc(interaction : discord.Interaction, value : int = -1):
    mPrint('CMDS', f'called /respond-to-bots-perc {value}')
    guildID = int(interaction.guild.id)

    if value == -1:
        await interaction.response.send_message(
            lang.commands.resp_to_bots_info(
                settings[guildID]["responseSettings"]["will_respond_to_bots"],
                settings[guildID]["responseSettings"]["response_to_bots_perc"]
            )
        )
        
        return

    #else
    #keep value between 0 and 100
    value = 100 if value > 100 else 0 if value < 0 else value

    await interaction.response.send_message(lang.commands.resp_to_bots_edit(value))
    settings[guildID]['responseSettings']['response_to_bots_perc'] = value
    dumpSettings()
    return

@tree.command(name="dictionary", description=lang.slash.dictionary)
async def dictionary(interaction : discord.Interaction):
    mPrint('CMDS', f'called /dictionary')
    guildID = int(interaction.guild.id)

    #1. Send a description
    custom_words = settings[guildID]['responseSettings']['custom_words']
    description = lang.commands.words_info(interaction.guild.name)

    if not settings[guildID]['responseSettings']['use_global_words']:
        description += lang.commands.words_use_global_words(interaction.guild.name)
        
    embed = discord.Embed(
        title = lang.commands.words_known_words,
        description = description,
        colour = col.orange
    )

    value = ''
    #2a. get the global words
    botWords = getWord(True)

    #2b. if the guild uses the global words, append them to value
    if settings[guildID]['responseSettings']['use_global_words']:
        #is server uses default words
        value = '\n'.join(botWords)
        embed.add_field(name = lang.commands.words_bot_words, value=value)
        value = '' 

    #2c. append the guild(local) words to value
    for i, cw in enumerate(custom_words):
        value += f'[`{i}`]: {cw}\n'
    if value == '': value=lang.commands.words_guild_words
    embed.add_field(name = lang.commands.words_guild_words(interaction.guild.name), value=value)
    
    #3. send the words
    await interaction.response.send_message(embed=embed)

@tree.command(name="dictionary-add", description=lang.slash.dictionary_add)
async def dictionary_add(interaction : discord.Interaction, new_word : str):
    """
    Aggiunge una parola al dizionario.
    
    :param new_word: La parola che si vuole aggiungere
    """
    mPrint('CMDS', f'called /dictionary add {new_word}')
    guildID = int(interaction.guild.id)

    settings[guildID]['responseSettings']['custom_words'].append(new_word)
    await interaction.response.send_message(lang.commands.words_learned, ephemeral=True)
    dumpSettings()
    return

@tree.command(name="dictionary-edit", description=lang.slash.dictionary_edit)
async def dictionary_edit(interaction : discord.Interaction, id : int, new_word : str):
    """
    Modifica una parola del dizionario.
    
    :param id: L'id della parola che vuoi modificare
    :param new_word: La parola che vuoi rimpiazzare
    """
    mPrint('CMDS', f'called /dictionary edit {id}, {new_word}')
    guildID = int(interaction.guild.id)

    editWord = id
    if len(settings[guildID]['responseSettings']['custom_words']) > editWord:
        settings[guildID]['responseSettings']['custom_words'][editWord] = new_word
        dumpSettings()
        await interaction.response.send_message(lang.done, ephemeral=True)
    else:
        await interaction.response.send_message(lang.commands.words_id_not_found, ephemeral=True)
    return

@tree.command(name="dictionary-del", description=lang.slash.dictionary_del)
async def dictionary_del(interaction : discord.Interaction, id : int):
    """
    It deletes a word from the dictionary.

    :param id: L'id della parola che vuoi eliminare
    """
    mPrint('CMDS', f'called /dictionary del {id}')
    guildID = int(interaction.guild.id)

    delWord = id
    if len(settings[guildID]['responseSettings']['custom_words']) > delWord:
        del settings[guildID]['responseSettings']['custom_words'][delWord]
        dumpSettings()
        await interaction.response.send_message(lang.done, ephemeral=True)
    else:
        await interaction.response.send_message(lang.commands.words_id_not_found, ephemeral=True)
    return

@tree.command(name="dictionary-useglobal", description=lang.slash.dictionary_use_global)
async def dictionary_default(interaction : discord.Interaction, value : bool ):
    mPrint('CMDS', f'called /dictionary useglobal {value}')
    guildID = int(interaction.guild.id)

    settings[guildID]["responseSettings"]["use_global_words"] = value
    await interaction.response.send_message(f'useDefault: {value}', ephemeral=True)
    dumpSettings()
    return

@tree.command(name="chess", description=lang.slash.chess)
async def chess(interaction : discord.Interaction, challenge : Union[discord.Role, discord.User] = None):
    """
    :param challenge: Il ruolo o l'utente da sfidare
    :param fen: Il layout delle pedine nella scacchiera (Se numerico indica uno dei FEN salvati)
    :param design: Il nome del design della scacchiera
    """
    mPrint('CMDS', f'called /chess: ch: {challenge}')
    guildID = int(interaction.guild.id)

    if interaction.channel.id in settings[guildID]['chessGame']['disabled_channels']:
        await interaction.response.send_message(lang.module_not_enabled, ephemeral=True)
        return

    await interaction.channel.typing()
#1. Prepare the variables
    #info about the player challenging another player or a role to a match
    class Challenge:
        type = 0             #can be: 0-> Everyone / 1-> Role / 2-> Player
        whitelist = []       #list of user ids (int) (or 1 role id) 
        authorJoined = False #Needed when type = 1

    challengeData = Challenge()

    #2A. parse challenges
    if challenge == None:
        mPrint('DEBUG', 'Challenged everyone')
        challengeData.type = 0

    elif '<@&' in challenge.mention: #user challenged role
        mPrint('DEBUG', f'challenged role: {challenge.id} ({challenge.name})')
        challengeData.type = 1
        challengeData.whitelist.append(challenge.id)
        
    else: #user challenged user
        mPrint('DEBUG', f'challenged user: {challenge.id} ({challenge.name})')
        challengeData.type = 2
        challengeData.whitelist.append(interaction.user.id)
        challengeData.whitelist.append(challenge.id)

    #useful for FENs: eg   (!chess) game fen="bla bla bla" < str.strip will return ["game", "fen=bla", "bla", "bla"]
    # args = splitString(args)                    #wheras splitString will return ["game", "fen=", "bla", "bla", "bla"]

    #Ask user if he wants FEN and/or design
    class GameData():
        selectedLayout = None
        selectedDesign = None
    gameData = GameData()

    #FEN options
    globalBoards = chessBridge.getBoards()
    guildBoards = settings[guildID]['chessGame']['boards']
    layoutChoices = discord.ui.Select(options=[], placeholder=lang.chess.layout_render_select)

    for layout in globalBoards: #global layouts
        isDefault = False
        if layout == settings[guildID]["chessGame"]["default_board"]:
            isDefault = True
            gameData.selectedLayout = globalBoards[layout]
        layoutChoices.add_option(label=f"FEN: {layout}", description=globalBoards[layout], value=globalBoards[layout], default=isDefault)

    for layout in guildBoards: #guild layouts
        isDefault = False
        if layout == settings[guildID]["chessGame"]["default_board"]:
            isDefault = True
            gameData.selectedLayout = guildBoards[layout]
        layoutChoices.add_option(label=f"FEN: {layout}", description=guildBoards[layout], value=guildBoards[layout], default=isDefault)

    #Design options
    globalDesigns = chessBridge.chessMain.getDesignNames()
    guildDesigns = settings[guildID]['chessGame']['designs']
    designChoices = discord.ui.Select(options=[], placeholder=lang.chess.design_render_select)

    for design in globalDesigns: #guild layouts
        isDefault = False
        if design == settings[guildID]["chessGame"]["default_design"]:
            isDefault = True
            gameData.selectedDesign = design
        designChoices.add_option(label=f"Design: {design}", value=design, default=isDefault)
    for design in guildDesigns: #guild layouts
        isDefault = False
        if design == settings[guildID]["chessGame"]["default_design"]:
            isDefault = True
            gameData.selectedDesign = design
        designChoices.add_option(label=f"Design: {design}", description=str(guildDesigns[design]), value=design, default=isDefault)

    #handlers for select choices
    async def layoutChoice(interaction : discord.Interaction):
        gameData.selectedLayout = str(layoutChoices.values[0])
        mPrint('DEBUG', f'Selected layout {gameData.selectedLayout}')
        await interaction.response.defer()

    async def designChoice(interaction : discord.Interaction):
        gameData.selectedDesign = str(designChoices.values[0])
        mPrint('DEBUG', f'Selected design {gameData.selectedDesign}')
        
        await interaction.response.defer()

    layoutChoices.callback = layoutChoice
    designChoices.callback = designChoice

    async def btn_cancel(interaction : discord.Interaction): #User cancels matchmaking
        confirm.disabled = True
        cancel.disabled = True
        layoutChoices.disabled = True
        designChoices.disabled = True
        await interaction.response.edit_message(view=view)
        return

    async def btn_confirm(interaction : discord.Interaction): # When user confirms the data this function starts the game
        if (gameData.selectedDesign != None) and (gameData.selectedLayout != None):
            confirm.disabled = True
            cancel.disabled = True
            layoutChoices.disabled = True
            designChoices.disabled = True
            await interaction.response.edit_message(view=view)
            await interaction.channel.typing()
            await startGame(interaction, gameData.selectedLayout, gameData.selectedDesign)
        else:
            await interaction.response.send_message("You have to choose a design and layout", ephemeral=True)
        return

    confirm = discord.ui.Button(label="Conferma", style = discord.ButtonStyle.primary)
    confirm.callback = btn_confirm

    cancel = discord.ui.Button(label="Annulla", style=discord.ButtonStyle.danger)
    cancel.callback = btn_cancel

    view = discord.ui.View()
    view.add_item(layoutChoices)
    view.add_item(designChoices)
    view.add_item(confirm)
    view.add_item(cancel)

    await interaction.response.send_message(view=view, ephemeral=True)
    
    async def startGame(interaction:discord.Interaction, gameFEN, gameDesign):
        designName = gameDesign
    #2C. double-check the data retreived
        board = ()
        if gameFEN != '': #if fen is provided, check if valid
            if('k' not in gameFEN or 'K' not in gameFEN):
                print(gameFEN)
                embed = discord.Embed(
                    title = lang.chess.embedTitle_fen_king_missing,
                    description= lang.chess.embedDesc_fen_king_missing("black" if "k" not in gameFEN else "", "white" if "K" not in gameFEN else ""),
                    color = col.red
                )
                await interaction.response.send_message(embed=embed)
                return -1
            #else, fen is valid
            board = ('FEN', gameFEN)

        mPrint('TEST', f'Design {gameDesign} ')
        if gameDesign != 'default': #if user asked for a design, check if it exists
            #give priority to guild designs
            if gameDesign in settings[guildID]['chessGame']['designs']:
                mPrint('TEST', f'Found Local design {gameDesign} ')
                colors = settings[guildID]['chessGame']['designs'][gameDesign]
                gameDesign = chessBridge.chessMain.gameRenderer.renderBoard(colors, interaction.id)
            elif chessBridge.chessMain.gameRenderer.doesDesignExist(gameDesign):
                mPrint('TEST', f'Found Global design {gameDesign}')
                gameDesign = chessBridge.chessMain.gameRenderer.getGlobalDesign(gameDesign) 
            else:
                mPrint('TEST', f'Design not found')
                gameDesign = 'default'
        
    # 3. All seems good, now let's send the embed to find some players
        #3A. Challenge one user
        class Challenge:
            type = 0             #can be: 0-> Everyone / 1-> Role / 2-> Player
            whitelist = []       #list of user ids (int) (or 1 role id) 
            authorJoined = False #Needed when type = 1

        if challengeData.type == 2: 
            embed = discord.Embed(title = f'{challenge.name}, sei stato sfidato da {interaction.user.name}!\nUsate una reazione per unirti ad un team (max 1 per squadra)',
                description=f'Scacchiera: {gameFEN}, design: {designName}',
                color = col.blu
            )
            
        #3B. Challenge one guild
        elif challengeData.type == 1:
            embed = discord.Embed(title = f'{challenge.name}, siete stati sfidati da {interaction.user.name}!\nUno di voi può unirsi alla partita!',
                description=f'Scacchiera: {gameFEN}, design: {designName}',
                color = col.blu
            )

        #3C. Challenge everyone
        else:
            embed = discord.Embed(title = f'Cerco giocatori per una partita di scacchi! ♟,\nUsa una reazione per unirti ad un team (max 1 per squadra)',
                description=f'Scacchiera: {gameFEN}, design: {designName}',
                color = col.blu).set_footer(text=f'Partita richiesta da {interaction.user.name}')
                        
        #3D. SEND THE EMBED FINALLY
        if challengeData.type != 0:
            await interaction.channel.send(f'{interaction.user} Ha sfidato {challenge.mention} a scacchi!')
        playerFetchMsg = await interaction.channel.send(embed=embed)

    #4. Await player joins
        #4A. setting up
        reactions = ('⚪', '🌑') #('🤍', '🖤')
        r1, r2 = reactions

        availableTeams = [reactions[0], reactions[1]] # Needed to avoid players from joining the same team
        players = [0, 0] #this will store discord.Members

        mPrint('DEBUG','chessGame: challenge whitelist')
        mPrint('DEBUG', challengeData.whitelist)

        #add reactions to the embed that people can use as buttons to join the teams
        await playerFetchMsg.add_reaction(r1)
        await playerFetchMsg.add_reaction(r2)
        await playerFetchMsg.add_reaction("❌") #if the author changes their mind


        def fetchChecker(reaction : discord.Reaction, user : Union[discord.Member, discord.User]) -> bool: #this is one fat checker damn
            """Checks if user team join request is valid"""

            # async def remove(reaction, user): #remove invalid reactions
            #     await reaction.remove(user)   #will figure out some way

            mPrint('DEBUG', f'chessGame: Check: {reaction}, {user}\nchallenge whitelist: {challengeData.whitelist}\navailable: {availableTeams}\n--------')
            
            #1- prevent bot from joining teams
            if (user == bot.user): 
                return False
            
            if (reaction.message.id != playerFetchMsg.id): #the reaction was given to another message
                return False

            if(str(reaction.emoji) == "❌" and user == interaction.user):
                return True #only the author can cancel the search

            #2- check if color is still available (prevent two players from joining the same team)
            if(str(reaction.emoji) not in availableTeams):
                return False #remember to remove the reaction before every return True

            userID = int(user.id)
            
            #3a- If player challenged a user:
            if(challengeData.type == 2): #0 everyone, 1 role, 2 user
                #check if joining player is in whitelist
                if userID not in challengeData.whitelist: return False
                
                challengeData.whitelist.remove(userID) #prevent user from rejoining another team
                availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
                return True

            #3b- If player challenged a role:
            elif(challengeData.type == 1):
                challengedRole = challenge.id #challenge has only one entry containing the role id
                
                #if the user joining is the author:
                if user == interaction.user and challengeData.authorJoined == False: #the message author can join even if he does not have the role
                    mPrint('DEBUG', 'chessGame: User is author') #check the user BEFORE the role, so if the user has the role it does not get deleted
                    challengeData.authorJoined = True #prevent author from joining 2 teams
                    availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
                    return True 
                
                #if the user joining isn't the author but has the role requested
                elif user.get_role(challengedRole) != None: #user has the role  
                    mPrint('DEBUG', 'chessGame: User has required role')
                    challengeData.whitelist = [] #delete the role to prevent two players with the role from joining (keeping out the author)
                    availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
                    return True

                mPrint('WARN',f'chessGame: User {user.name} is not allowerd to join (Role challenge)')
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
            embed.color = col.red

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
            
            embed.color = col.green
            await playerFetchMsg.edit(embed=embed)
            #iii. fake sleep for professionality
            await asyncio.sleep(random.randrange(0,2))

        except asyncio.TimeoutError: #players did not join in time
            embed = discord.Embed(
                title = 'Non ci sono abbastanza giocatori.',
                colour = col.red
            )
            await interaction.channel.send(embed=embed)
            await playerFetchMsg.delete()
            return -1

        else: #players did join in time

            if str(r1.emoji) == reactions[0]: #first player choose white
                player1 = players[1] #white
                player2 = players[0] #black
            else: #first player choose black
                player1 = players[0] #white
                player2 = players[1] #black
            mPrint('INFO', f'p1: {player1}\np2: {player2}')

            #iv. Send an embed with the details of the game
            embed = discord.Embed(
                title = f'Giocatori trovati\n{r1} {player1} :vs: {player2} {r2}',
                description=f"Impostazioni:\n- Scacchiera: {gameFEN}, Design: {gameDesign}",
                colour = col.green
            )
            
            #v. start a thread where the game will be disputed, join the players in there
            thread = await interaction.channel.send(embed=embed)
            gameThread = await thread.create_thread(name=(f'{str(player1)[:-5]} -VS- {str(player2)[:-5]}'), auto_archive_duration=60, reason='Scacchi')
            await gameThread.add_user(player1)
            await gameThread.add_user(player2)
            await playerFetchMsg.delete()
            mainThreadEmbed = (thread, embed)

    #5. FINALLY, start the game
            mPrint('TEST', f'design: {gameDesign}')
            await chessBridge.loadGame(gameThread, bot, [player1, player2], mainThreadEmbed, board, gameDesign)
            #                                        #send them backwards (info on chessBrige.py) [black, white]
            await gameThread.edit(archived=True, locked=True)
            designFolder = f'{chessBridge.chessMain.gameRenderer.spritesFolder}{gameDesign}'
            if gameDesign.find('\\') != -1 or design.find('/') != -1:
                shutil.rmtree(designFolder)

@tree.command(name="chess-layout", description=lang.slash.chess_layout)
@app_commands.choices(sub_command=[
        app_commands.Choice(name=lang.choices.info, value="0"),
        app_commands.Choice(name=lang.choices.render, value="1"),
        app_commands.Choice(name=lang.choices.add, value="2"),
        app_commands.Choice(name=lang.choices.edit, value="3"),
        app_commands.Choice(name=lang.choices.remove, value="4"),
])
@app_commands.describe(sub_command=lang.choices.description)
async def chess_layout(interaction : discord.Interaction, sub_command: app_commands.Choice[str]): #, name:str=None, fen:str = None
    mPrint('CMDS', f'called /chess-layout: {sub_command.name}')
    guildID = int(interaction.guild.id)
    response = int(sub_command.value)
    botBoards = chessBridge.getBoards()
    guildBoards = settings[guildID]['chessGame']['boards']
    

    #send saved layouts
    if response == 0: 
        embed = discord.Embed(
            title = lang.chess.layout_description,
            colour = col.orange
        )
        #ii. append the global data boards to the embed
        
        value = ''
        for b in botBoards:
            value += f"**{b}**: {botBoards[b]}\n"
        embed.add_field(name = lang.chess.layout_global_layouts, value=value, inline=False)

        #iii. if guild data has boards, append them to the embed
        if settings[guildID]['chessGame']['boards'] != {}:
            guildBoards = ''
            for b in settings[guildID]['chessGame']['boards']:
                guildBoards += f"**{b}**: {settings[guildID]['chessGame']['boards'][b]}\n"
            embed.add_field(name = lang.chess.layout_guild_layouts(interaction.guild.name), value=guildBoards, inline=False)
        
        #iv. send the embed
        await interaction.response.send_message(embed=embed)
        return 0

    elif response == 1: # renders a FEN and send it in chat
        choices = discord.ui.Select(options= #global layouts
            [discord.SelectOption(label=name, description=botBoards[name], value=botBoards[name]) for name in botBoards],
            placeholder=lang.chess.layout_render_select
        )
        for layout in guildBoards: #guild layouts
            choices.add_option(label=layout, description=guildBoards[layout], value=guildBoards[layout])

        view = discord.ui.View()
        view.add_item(choices)

        async def render_and_send_image(interaction : discord.Interaction):
            mPrint("TEST", choices.values)
            layoutFEN = choices.values[0]
            
            #ii. let the Engine make the image
            try:
                image = chessBridge.getBoardImgPath(layoutFEN, interaction.id)
                mPrint('DEBUG', f'got image path: {image}')
            except Exception:
                await interaction.response.send_message(lang.chess.layout_render_error)
                return -2

            if image == 'Invalid':
                await interaction.response.send_message(f"{lang.chess.layout_render_invalid} {layoutFEN}")
                return -1
            mPrint('DEBUG', f'rendered image: {image}')

            #iii. Send the image to discord
            imgpath = (f'{image[0]}')
            with open(imgpath, "rb") as fh:
                f = discord.File(fh, filename=imgpath)
            #iv. data hoarding is bad
            await interaction.response.send_message(lang.chess.layout_user_rendered(interaction.user.name, layoutFEN), file=f)
            try:
                os.remove(imgpath)
            except PermissionError:
                mPrint('ERROR', f'Could not delete file {imgpath}\n{traceback.format_exc()}')

            try:
                os.remove(imgpath.replace('png', 'log'))
            except PermissionError:
                mPrint('ERROR', f'Could not delete file {imgpath.replace("png", "log")}\n{traceback.format_exc()}')
            
        choices.callback = render_and_send_image
        await interaction.response.send_message(view=view, ephemeral=True)
        return 0

    elif response == 2: # adds a board in the Data
        class NewLayoutData(discord.ui.Modal, title='Inserisci un nuovo layout'):
            name = discord.ui.TextInput(label='Nome', placeholder="Name", style=discord.TextStyle.short, required=True)
            fen = discord.ui.TextInput(label='FEN', placeholder="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 0", default="https://lichess.org/editor", style=discord.TextStyle.long, required=True)

            async def on_submit(self, interaction: discord.Interaction):
                mPrint('TEST', f"{self.name}: {self.fen}")
                if str(self.name) not in settings[guildID]['chessGame']['boards']:
                    #iii. append the board and dump the json data
                    settings[guildID]['chessGame']['boards'][str(self.name)] = str(self.fen)
                    dumpSettings()
                    await interaction.response.send_message(lang.chess.layout_add_done(str(self.name), str(self.fen)))
                else:
                    await interaction.response.send_message(lang.chess.layout_add_exists)

        await interaction.response.send_modal(NewLayoutData())

        return

    elif response == 3: #rename a board
        # setup guild layout in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=name, description=guildBoards[name]) for name in guildBoards],
            placeholder=lang.chess.layout_edit_select
        )
        view = discord.ui.View()
        view.add_item(choices)

        async def edit_board(interaction : discord.Interaction): # This triggers when user selects the board to edit
            layoutname = str(choices.values[0])
            class EditLayoutData(discord.ui.Modal, title=lang.chess.layout_edit_title(layoutname)):
                newfen = discord.ui.TextInput(label=f'Edit the FEN for "{layoutname}"', default=guildBoards[layoutname], style=discord.TextStyle.long, required=True)

                async def on_submit(self, interaction: discord.Interaction): #this triggers when user submits the modal with the new data
                    settings[guildID]['chessGame']['boards'][layoutname] = str(self.newfen)
                    dumpSettings()
                    await interaction.response.send_message(lang.chess.layout_edit_ok(layoutname, str(self.newfen)))
            await interaction.response.send_modal(EditLayoutData())

        choices.callback = edit_board

        if guildBoards != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(lang.chess.layout_no_layouts, ephemeral=True)
        return 0
    
    elif response == 4: #delete a board
        # setup guild layout in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=name, description=guildBoards[name]) for name in guildBoards],
            placeholder=lang.chess.layout_delete_select
        )
        view = discord.ui.View()
        view.add_item(choices)

        async def delete_board(interaction : discord.Interaction): # This triggers when user selects the board to edit
            layoutname = choices.values[0]
            if layoutname in settings[guildID]['chessGame']['boards']:
                fen = settings[guildID]['chessGame']['boards'].pop(layoutname)
                dumpSettings()
                await interaction.response.send_message(lang.chess.layout_delete_ok(layoutname, fen))

        choices.callback = delete_board
        if guildBoards != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(lang.chess.layout_no_layouts, ephemeral=True)
        return 0
    
@tree.command(name="chess-designs", description=lang.slash.chess_designs)
@app_commands.choices(sub_command=[
        app_commands.Choice(name=lang.choices.info, value="0"),
        app_commands.Choice(name=lang.choices.render, value="1"),
        app_commands.Choice(name=lang.choices.add, value="2"),
        app_commands.Choice(name=lang.choices.edit, value="3"),
        app_commands.Choice(name=lang.choices.remove, value="4"),
])
@app_commands.describe(sub_command=lang.choices.description)
async def chess_design(interaction : discord.Interaction, sub_command: app_commands.Choice[str]): #, name:str=None, fen:str = None
    mPrint('CMDS', f'called /chess-designs: {sub_command.name}')
    guildID = int(interaction.guild.id)
    response = int(sub_command.value)

    globalDesigns = chessBridge.chessMain.getDesignNames()
    guildDesigns = settings[guildID]['chessGame']['designs']

    mPrint('TEST', globalDesigns)
    mPrint('TEST', guildDesigns)

    def parseHEX(hex1, hex2) -> list: #helper function
        colors = [hex1, hex2]
        possible = ['#', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        for i, hex in enumerate(colors): #foreach color
            mPrint('DEBUG', f'parsing hex {hex}')
            # if it has not an # add it
            if hex[0] != '#': 
                hex = '#' + hex
            for char in hex: #check if color digits are valid
                if char.lower() not in possible:
                    return '0'
            if len(hex) == 4: #if the hex type is #fff expand it to #ffffff
                hex = f'#{hex[1]}{hex[1]}{hex[2]}{hex[2]}{hex[3]}{hex[3]}'
            if len(hex) != 7:
                return '0'
            colors[i] = hex
        return colors

    if response == 0: #show board designs
        embed = discord.Embed(
            title = lang.chess.design_available,
            colour = col.orange
        )

        #ii. append the global data designs to the embed
        value = ''
        for b in range(len(globalDesigns)):
            value += f"{globalDesigns[b]}\n"

        embed.add_field(name =lang.chess.design_available, value=value, inline=False)

        #iii. if guild data has designs, append them to the embed
        if settings[guildID]['chessGame']['designs'] != {}:
            guildDesigns = ''
            for b in settings[guildID]['chessGame']['designs']:
                guildDesigns += f"**{b}**: {settings[guildID]['chessGame']['designs'][b]}\n"
            embed.add_field(name = f'Design ({interaction.guild.name}):', value=guildDesigns, inline=False)
        
        #iv. send the embed
        await interaction.response.send_message(embed=embed)
        return 0
        
    if response == 1: # Render and send designs
        choices = discord.ui.Select(options= #global layouts
            [discord.SelectOption(label=x, value=x) for x in globalDesigns],
            placeholder=lang.chess.design_render_select
        )
        for design in guildDesigns: #guild layouts
            choices.add_option(label=design, description=str(guildDesigns[design]), value=design)

        view = discord.ui.View()
        view.add_item(choices)

        async def render_and_send_image(interaction : discord.Interaction):
            mPrint("TEST", choices.values)
            designChoice = str(choices.values[0])
            if designChoice in settings[guildID]['chessGame']['designs']: #design exists in guildData
                colors = settings[guildID]['chessGame']['designs'][designChoice]
                designPath = chessBridge.chessMain.gameRenderer.renderBoard(colors, interaction.message.id)
                with open(designPath+'chessboard.png', "rb") as fh:
                    f = discord.File(fh, filename=(designPath + 'chessboard.png'))
                    await interaction.response.send_message(lang.chess.design_generated(interaction.user.name, designChoice), file=f)
                shutil.rmtree(designPath, ignore_errors=False, onerror=None)
                return 0

            #design does not exist in guildData, search if exists in sprites folder
            elif chessBridge.chessMain.gameRenderer.doesDesignExist(designChoice):
                design = f'{chessBridge.chessMain.gameRenderer.spritesFolder}{designChoice}/chessboard.png'
                with open(design, "rb") as fh:
                    f = discord.File(fh, filename=design)
                    await interaction.response.send_message(lang.chess.design_generated(interaction.user.name, designChoice), file=f)
            else:
                await interaction.response.send_message(lang.chess.design_404)
    
        choices.callback = render_and_send_image
        await interaction.response.send_message(view=view, ephemeral=True)
        return 0

    elif response == 2: # adds a design in guildsData
        class NewDesignData(discord.ui.Modal, title='Inserisci un nuovo Design'):
            name = discord.ui.TextInput(label='Nome', placeholder="", style=discord.TextStyle.short, required=True)
            hex1 = discord.ui.TextInput(label='Principale', placeholder="#aabbcc | #abc", style=discord.TextStyle.short, required=True, max_length=7)
            hex2 = discord.ui.TextInput(label='Secondario', placeholder="#11dd33 | #1d3", style=discord.TextStyle.short, required=True, max_length=7)

            async def on_submit(self, interaction: discord.Interaction):
                name = str(self.name)
                col1 = str(self.hex1)
                col2 = str(self.hex2)

                mPrint('TEST', f"{self.name}: {col1} {col2}")
                if name not in settings[guildID]['chessGame']['designs']:#check if already exists
                    #if not, make new design
                    #parse colors
                    colors = parseHEX(col1, col2)
                    if colors == '0':
                        await interaction.response.send_message(lang.chess.design_HEX_invalid(col1, col2), ephemeral=True)
                        return -2
                    settings[guildID]['chessGame']['designs'][name] = colors
                    await interaction.response.send_message(lang.chess.design_add_done(name, colors))
                    dumpSettings()
                    
                else:
                    await interaction.response.send_message(lang.chess.design_add_exists)

        await interaction.response.send_modal(NewDesignData())

        return

    elif response == 3: # edits a design in guildsData
        # setup guild designs in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=design, description=str(guildDesigns[design]), value=design) for design in guildDesigns],
            placeholder=lang.chess.design_edit_select
        )

        view = discord.ui.View()
        view.add_item(choices)

        async def edit_design(interaction : discord.Interaction): # This triggers when user selects the board to edit
            designName = choices.values[0]
            class EditDesignData(discord.ui.Modal, title=lang.chess.design_edit_title(designName)):
                c1 = discord.ui.TextInput(label=f'Primary  ', default=guildDesigns[designName][0], placeholder="#aabbcc | #abc", style=discord.TextStyle.short, required=True, max_length=7)
                c2 = discord.ui.TextInput(label=f'Secondary', default=guildDesigns[designName][1], placeholder="#11dd33 | #1d3", style=discord.TextStyle.short, required=True, max_length=7)

                async def on_submit(self, interaction: discord.Interaction): #this triggers when user submits the modal with the new data
                    col1,col2 = str(self.c1), str(self.c2)
                    colors = parseHEX(col1, col2)
                    if colors == '0':
                        await interaction.response.send_message(lang.chess.design_HEX_invalid(col1, col2), ephemeral=True)
                        return -2
                    #else
                    settings[guildID]['chessGame']['designs'][designName] = [col1, col2]
                    await interaction.response.send_message(lang.chess.design_edit_ok(designName, str([col1, col2])))
            await interaction.response.send_modal(EditDesignData())

        choices.callback = edit_design

        if guildDesigns != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(lang.chess.design_no_designs, ephemeral=True)
        return 0

    elif response == 4: # deletes a design in guildsData
        # setup guild designs in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=design, description=str(guildDesigns[design]), value=design) for design in guildDesigns],
            placeholder=lang.chess.design_delete_select
        )
        view = discord.ui.View()
        view.add_item(choices)

        async def delete_board(interaction : discord.Interaction): # This triggers when user selects the board to edit
            designname = choices.values[0]
            if designname in settings[guildID]['chessGame']['designs']:
                colors = settings[guildID]['chessGame']['designs'].pop(designname)
                dumpSettings()
                await interaction.response.send_message(lang.chess.design_delete_ok(designname, colors))

        choices.callback = delete_board
        if guildDesigns != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(lang.chess.design_no_designs, ephemeral=True)
        return 0

@tree.command(name="playlist", description=lang.slash.playlist)
@app_commands.choices(sub_command=[
        app_commands.Choice(name=lang.choices.info, value="0"),
        app_commands.Choice(name=lang.choices.add, value="1"),
        app_commands.Choice(name=lang.choices.edit, value="2"),
        app_commands.Choice(name=lang.choices.remove, value="3"),
])
async def playlists(interaction : discord.Interaction, sub_command: app_commands.Choice[str]):
    mPrint('CMDS', f'called /playlist: ')
    guildID = int(interaction.guild.id)
    response = int(sub_command.value)

    savedPlaylists = settings[guildID]["musicbot"]["saved_playlists"]

    if response == 0: #send the playlist list list to user
        
        embed = discord.Embed(
            title = lang.music.embedTitle_playlist_saved(interaction.guild.name),
            description = lang.music.embedDesc_playlist_saved,
            color=col.green
        )
        for plist in settings[guildID]["musicbot"]["saved_playlists"]:
            urls=''
            for i, t in enumerate(settings[guildID]["musicbot"]["saved_playlists"][plist]):
                urls += f'**{i}**: {t}\n' 
            embed.add_field(name=plist, value=urls, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return    

    elif response == 1:  #add a new playlist
        class NewPlaylist(discord.ui.Modal, title = lang.music.playlist_create_title):
            name = discord.ui.TextInput(label='Nome', placeholder="", style=discord.TextStyle.short, required=True)
            links = discord.ui.TextInput(label='Tracce', placeholder="Inserisci i link o i nomi delle canzoni uno per riga (spotify/youtube, anche playlist)", style=discord.TextStyle.paragraph, required=True)

            async def on_submit(self, interaction: discord.Interaction):
                name = str(self.name)
                links = str(self.links).split('\n')

                mPrint('TEST', f"{name}: {links}")

                errors = ''
                tracks = []
                for x in links:
                    isUrlValid = musicBridge.evalUrl(x, settings[interaction.guild.id]['musicbot']['youtube_search_overwrite'])

                    if isUrlValid == False:
                        errors += lang.music.playlist_create_404(x)

                    else:
                        if "open.spotify.com" not in x and "youtube.com" not in x:
                            mPrint('MUSIC', f'Searching for user requested song: ({x})')
                            x = musicBridge.youtubeParser.searchYTurl(x, settings[interaction.guild.id]['musicbot']['youtube_search_overwrite'])
                        tracks.append(x)

                if errors != '':
                    embed = discord.Embed(
                        title="ERRORS:",
                        description=errors,
                        color=col.error
                    )

                    if tracks == []:
                        embed.add_field(name='ERROR', value=': every song/playlist failed')
                        interaction.response.send_message(embed=embed, ephemeral=True)

                trackList = ''
                for i, t in enumerate(tracks):
                    trackList += f"\n**{i}**. {t}"

                #Save the song/playlist URL in a list of one element and inform the user
                settings[guildID]["musicbot"]["saved_playlists"][name] = tracks
                dumpSettings()

                embed = discord.Embed(
                    title = f"Playlist {name}: ",
                    description=f"{trackList}\n{errors}",
                    color = col.orange if errors == "" else col.red
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
                return

        await interaction.response.send_modal(NewPlaylist())
        return

    elif response == 2: #edit a playlist
        # get playlists and put them in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=playlist, value=playlist) for playlist in savedPlaylists],
            placeholder=lang.music.playlist_edit_select
        )

        view = discord.ui.View()
        view.add_item(choices)

        async def edit_playlist(interaction : discord.Interaction): # This triggers when user selects which playlist to edit
            playlistName = str(choices.values[0])
            mPrint('TEST', f'playlist name: {playlistName}')
            class EditPlaylistData(discord.ui.Modal, title=lang.music.playlist_edit_title(playlistName)):
                plists = '\n'.join(savedPlaylists[playlistName])
                links = discord.ui.TextInput(label='Tracce', placeholder="Inserisci i link o i nomi delle canzoni uno per riga (spotify/youtube, anche playlist)", default=plists, style=discord.TextStyle.paragraph, required=True)

                async def on_submit(self, interaction: discord.Interaction): #this triggers when user submits the modal with the new data
                    links = str(self.links).split('\n')
                    # this is the same as creating a new playlist

                    mPrint('TEST', f"{playlistName}: {links}")

                    errors = ''
                    tracks = []
                    for x in links:
                        isUrlValid = musicBridge.evalUrl(x, settings[interaction.guild.id]['musicbot']['youtube_search_overwrite'])

                        if isUrlValid == False:
                            errors += lang.music.playlist_create_404(x)

                        else:
                            if "open.spotify.com" not in x and "youtube.com" not in x:
                                mPrint('MUSIC', f'Searching for user requested song: ({x})')
                                x = musicBridge.youtubeParser.searchYTurl(x)
                            tracks.append(x)

                    if errors != '':
                        embed = discord.Embed(
                            title="ERRORS:",
                            description=errors,
                            color=col.error
                        )

                        if tracks == []:
                            await interaction.response.send_message(lang.music.playlist_create_failed, ephemeral=True)
                            return

                    trackList = ''
                    for i, t in enumerate(tracks):
                        trackList += f"\n**{i}**. {t}"

                    #Save the song/playlist URL in a list of one element and inform the user
                    settings[guildID]["musicbot"]["saved_playlists"][playlistName] = tracks
                    dumpSettings()

                    embed = discord.Embed(
                        title = f"Playlist {playlistName}: ",
                        description=f"{trackList}\n{errors}",
                        color = col.orange if errors == "" else col.red
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    
                    return

            await interaction.response.send_modal(EditPlaylistData())

        choices.callback = edit_playlist

        if savedPlaylists != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(lang.music.playlist_404, ephemeral=True)
        return 0

    elif response == 3: #remove a playlist
        # setup guild designs in choices
        choices = discord.ui.Select(options=
            [discord.SelectOption(label=playlist, value=playlist) for playlist in savedPlaylists],
            placeholder=lang.music.playlist_delete_select
        )
        view = discord.ui.View()
        view.add_item(choices)

        async def delete_playlist(interaction : discord.Interaction): # This triggers when user selects the playlist to delete
            playlistName = str(choices.values[0])
            if playlistName in settings[guildID]["musicbot"]['saved_playlists']:
                links = settings[guildID]["musicbot"]['saved_playlists'].pop(playlistName)
                dumpSettings()
                links = "\n".join(links)
                await interaction.response.send_message(lang.music.playlist_delete_ok(playlistName, f'```{links}```'), ephemeral=True)

        choices.callback = delete_playlist
        if savedPlaylists != {}:
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(lang.music.playlist_404, ephemeral=True)
        return 0

    return

@tree.command(name="player-settings", description=lang.slash.player_settings)
@app_commands.choices(setting=[
        app_commands.Choice(name=lang.choices.info, value="0"),
        app_commands.Choice(name=lang.choices.shuffle, value="1"),
        app_commands.Choice(name=lang.choices.precision, value="2"),
])
async def playerSettings(interaction : discord.Interaction, setting : app_commands.Choice[str], value : int = None):
    """
    :param setting: DO NOT INSERT value FOR SHUFFLE 
    """
    mPrint('CMDS', f'called /player-settings: ')
    guildID = int(interaction.guild.id)
    response = int(setting.value)

    if response == 0: #print settings
        embed = discord.Embed(
            title=lang.music.settings_embed_title,
            description="/player-settings",
            color=col.green
        )
        embed.add_field(name="Shuffle: ", value=f"{settings[guildID]['musicbot']['player_shuffle']}", inline=False)
        embed.add_field(name="Precision: ", value=f"{settings[guildID]['musicbot']['timeline_precision']} / {config.timeline_max}", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    elif response == 1: # shuffle setting
        current = bool(settings[guildID]['musicbot']["player_shuffle"])
        choices = discord.ui.Select(options=[
            discord.SelectOption(label="True", description="Il player fa il primo shuffle in automatico", value=True, default=current),
            discord.SelectOption(label="False", description="Il player riproduce le canzoni in ordine", value=False, default=(not current))
            ]
        )
        view = discord.ui.View()
        view.add_item(choices)

        async def shuffle_response(interaction : discord.Interaction):
            mPrint('TEST', f"{choices.values[0]}")
            settings[guildID]['musicbot']["player_shuffle"] = choices.values[0]
            dumpSettings()
            await interaction.response.defer()

        choices.callback = shuffle_response
        await interaction.response.send_message(view=view, ephemeral=True)

    elif response == 2: #precision
        if value == None:
            await interaction.response.send_message(lang.music.settings_arg_needed, ephemeral=True)
            return
        warnmsg = ''
        newPrec = value
        if newPrec > config.timeline_max:
            newPrec = config.timeline_max
            warnmsg = lang.music.settings_timeline_max(config.timeline_max)

        if newPrec < 0:
            newPrec = 0
            warnmsg = lang.music.settings_timeline_min
        
        settings[guildID]['musicbot']["timeline_precision"] = newPrec
        dumpSettings()
        await interaction.response.send_message(lang.music.settings_new_precision(f"{newPrec}{warnmsg}"), ephemeral=True)

    return
    
@tree.command(name="play", description=lang.slash.play)
@app_commands.describe(tracks="URL / Title / saved playlist (/playlist); use , for mutiple items")
async def playSong(interaction : discord.Interaction, tracks : str, shuffle:bool = None):
    guildID = int(interaction.guild.id)
    await interaction.response.defer(ephemeral=True)

    if interaction.channel.id in settings[guildID]['musicbot']['disabled_channels']:
        await interaction.followup.send(lang.module_not_enabled, ephemeral=True)
        return
    
    # Load useful variables
    overwrite = settings[guildID]['musicbot']['youtube_search_overwrite']
    if shuffle == None: shuffle = settings[guildID]['musicbot']["player_shuffle"]
    # else -> shuffle = shuffle
    precision = settings[guildID]['musicbot']["timeline_precision"]
    playlists = settings[guildID]['musicbot']['saved_playlists']

    try:
        userVC = bot.get_channel(interaction.user.voice.channel.id)
    except AttributeError:
        await interaction.followup.send(lang.music.play_user_not_in_vc, ephemeral=True)
        return

    voice_client : discord.VoiceClient = get(bot.voice_clients, guild=interaction.guild)
    if voice_client != None and voice_client.is_connected():
        if userVC!=None and voice_client.channel.id == userVC.id:
            await interaction.followup.send(lang.music.play_wrong_command, ephemeral=True)
        else:
            await interaction.followup.send(lang.music.play_already_connected, ephemeral=True)
        return

    # Check that guidsData[overwritten tracks] are the same of music/suggestions/guildID[overwritten tracks]
    try:
        if not os.path.exists("music/suggestions"):
            os.mkdir('music/suggestions')
        with open(f'music/suggestions/{str(interaction.guild.id)}.json', 'r') as f:
            owTracks = json.load(f)
        for query in owTracks:
            if query not in settings[interaction.guild.id]['musicbot']['youtube_search_overwrite']:
                overwrite[query] = owTracks[query]
                dumpSettings()
    except json.decoder.JSONDecodeError:
        pass #File is probably empty
    except FileNotFoundError:
        pass #File does not exist
    except Exception:
        mPrint('WARN', traceback.format_exc())

    # Get the links
    playlistURLs = musicBridge.getTracksURL(tracks, overwrite, playlists)

    if playlistURLs == None:
        await interaction.followup.send(lang.music.loading_error)
        return -1
    elif playlistURLs == 404:
        await interaction.followup.send(lang.music.play_error_404)
        return -1
    
    #Remove musicbot slash commands if they exist
    cmds = tree.get_commands(guild=interaction.guild)
    if len(cmds) != 0:
        tree.clear_commands(guild=interaction.guild)
        mPrint('TEST', f'Syncing tree')
        await tree.sync(guild=interaction.guild)
        #print(tree.get_commands(guild=interaction.guild))

    #Start music module
    try:
        mPrint('TEST', f'--- playing queue --- \n{playlistURLs}')
        await musicBridge.play(playlistURLs, interaction, bot, tree, shuffle, precision, overwrite, playlists)
        mPrint('TEST', 'musicBridge.play() returned')
    except Exception:
        await interaction.followup.send(lang.music.player.generic_error, ephemeral=True)
        mPrint('ERROR', traceback.format_exc())

@tree.command(name="ping", description="Ping the bot")
async def ping(interaction : discord.Interaction):
    mPrint('CMDS', f'called /ping')

    pingms = round(bot.latency*1000)
    await interaction.response.send_message(f'Pong! {pingms}ms')
    mPrint('INFO', f'ping detected: {pingms} ms')

@tree.command(name="module-info", description=lang.slash.module_info)
@app_commands.default_permissions()
async def module_info(interaction : discord.Interaction):
    guildID = int(interaction.guild.id)
    await interaction.response.defer(ephemeral=True)

    embed=discord.Embed(
        title=f"CuloBot modules for {interaction.guild.name}",
        description=lang.commands.module_info_embedDesc,
        color=col.orange
    )

    #get all guild channels
    allChannels = await interaction.guild.fetch_channels()
    #extract only the TextChannels
    allChannels:list[discord.TextChannel] = [x for x in allChannels if x.type == discord.ChannelType.text]
    allChannelsID:list[int] = [x.id for x in allChannels if x.type == discord.ChannelType.text]

    responseChannels = ""
    #foreach disabled channel (id)
    for channelID in settings[guildID]['responseSettings']['disabled_channels']:
        #if channel id is present in the guild
        for guildCh in allChannels:
            if channelID == guildCh.id:
                responseChannels = responseChannels + f"{guildCh.mention}\n"
                break
        #clean guildsData from no-longer existing channels:
        if channelID not in allChannelsID:
            mPrint('DEBUG', f'found removed channel {ch}')
            settings[guildID]['responseSettings']['disabled_channels'].remove(ch)
    #Add N/A if string
    responseChannels = lang.commands.module_info_no_blacklisted if responseChannels == "" else responseChannels

    chessChannels = ""
    #foreach disabled channel (id)
    for ch in settings[guildID]['chessGame']['disabled_channels']:
        #if channel id is present in the guild
        for guildCh in allChannels:
            if ch == guildCh.id:
                chessChannels = chessChannels + f"{guildCh.mention}\n"
                break
        #clean guildsData from no-longer existing channels:
        if ch not in allChannelsID:
            mPrint('DEBUG', f'found removed channel {ch}')
            settings[guildID]['chessGame']['disabled_channels'].remove(ch)
    #Add N/A if string
    chessChannels = lang.commands.module_info_no_blacklisted if chessChannels == "" else chessChannels

    musicChannels = ""
    #foreach disabled channel (id)
    for ch in settings[guildID]['musicbot']['disabled_channels']:
        #if channel id is present in the guild
        for guildCh in allChannels:
            if ch == guildCh.id:
                musicChannels = musicChannels + f"{guildCh.mention}\n"
                break
        #clean guildsData from no-longer existing channels:
        if ch not in allChannelsID:
            mPrint('DEBUG', f'found removed channel {ch}')
            settings[guildID]['musicbot']['disabled_channels'].remove(ch)
    #Add N/A if string
    musicChannels = lang.commands.module_info_no_blacklisted if musicChannels == "" else musicChannels


    embed.add_field(name="**Chat replies:**", value=responseChannels, inline=False)
    embed.add_field(name="**Chess:**", value=chessChannels, inline=False)
    embed.add_field(name="**Music Bot:**", value=musicChannels, inline=False)
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="module", description=lang.slash.module)
@app_commands.choices(modules=[
        app_commands.Choice(name=lang.choices.all, value="0"),
        app_commands.Choice(name=lang.choices.reply, value="1"),
        app_commands.Choice(name=lang.choices.chess, value="2"),
        app_commands.Choice(name=lang.choices.music, value="3"),
])
@app_commands.default_permissions()
async def module_settings(interaction : discord.Interaction, modules:app_commands.Choice[str], channel:discord.TextChannel=None, enable:bool=None):
    """
    :param channel: on which text channel (default=every channel)
    :param enable: whether to enable or disable the module
    """
    mPrint('CMDS', f'called /module: {modules.name})')
    guildID = int(interaction.guild.id)
    response = int(modules.value)
    await interaction.response.defer(ephemeral=True)

    wantedModules = ""
    if response == 0:
        wantedModules = ['responseSettings', 'chessGame', 'musicbot']
    elif response == 1:
        wantedModules = ['responseSettings']
    elif response == 2:
        wantedModules = ['chessGame']
    elif response == 3:
        wantedModules = ['musicbot']
    else:
        mPrint('ERROR', f'Invalid response "{response}" for module_settings()')
        return

    if len(wantedModules) == 1:
        module = wantedModules[0]
        if enable == None: #send info about the module
            resp = lang.commands.module_disabled_in_channel(modules.name) 
            for ch in settings[guildID][module]['disabled_channels']:
                channel = await bot.fetch_channel(ch)
                resp = resp + f"{channel.mention}\n"
            await interaction.followup.send(resp, ephemeral=True)
            return
        elif channel == None: #change setting for every channel
            if enable == False: #user wants to disable setting in every channel
                allChannels = await interaction.guild.fetch_channels()
                settings[guildID][module]['disabled_channels'] = []
                for c in allChannels:
                    if c.type == discord.ChannelType.text:
                        settings[guildID][module]['disabled_channels'].append(c.id)
                dumpSettings()
                await interaction.followup.send(lang.commands.module_disabled_all_channels(modules.name), ephemeral=True)
            else: #user wants to enable setting in every channel
                settings[guildID][module]['disabled_channels'] = []
                dumpSettings()
                await interaction.followup.send(lang.commands.module_enabled_all_channels(modules.name), ephemeral=True)
        else: #change setting for specific channel
            if channel.id in settings[guildID][module]['disabled_channels']: #channel was already disabled
                if enable == False:
                    await interaction.followup.send(lang.commands.module_already_disabled(modules.name, channel.mention), ephemeral=True)
                    pass #channel was already enabled
                else:
                    settings[guildID][module]['disabled_channels'].remove(channel.id)
                    dumpSettings()
                    await interaction.followup.send(lang.commands.module_now_enabled(modules.name, channel.mention), ephemeral=True)
            else: #channel was enabled
                if enable == False:
                    settings[guildID][module]['disabled_channels'].append(channel.id)
                    dumpSettings()
                    await interaction.followup.send(lang.commands.module_now_disabled(modules.name, channel.mention), ephemeral=True)
                else:
                    await interaction.followup.send(lang.commands.module_already_enabled(modules.name, channel.mention), ephemeral=True)
                    pass #channel was already disabled
    else:
        if enable == None:
            await interaction.followup.send(lang.commands.module_arg_missing, ephemeral=True)
            return
        try:
            allChannels = await interaction.guild.fetch_channels()
            for module in wantedModules:
                if channel == None: #change every module for every channel
                    if enable == False: #user wants to disable setting in every channel
                        settings[guildID][module]['disabled_channels'] = []
                        for ch in allChannels:
                            if ch.type == discord.ChannelType.text:
                                settings[guildID][module]['disabled_channels'].append(ch.id)
                        
                    else: #user wants to enable setting in every channel
                        settings[guildID][module]['disabled_channels'] = []
                        
                else: #change setting for specific channel
                    if channel.id in settings[guildID][module]['disabled_channels']: #channel was disabled
                        if enable == False:
                            pass #channel was already disabled
                        else:
                            settings[guildID][module]['disabled_channels'].remove(channel.id)
                            
                    else: #channel was enabled
                        if enable == False:
                            settings[guildID][module]['disabled_channels'].append(channel.id)
                        else:
                            pass #channel was already disabled
            dumpSettings()
            await interaction.followup.send(lang.commands.module_done)
        except Exception:
            mPrint('ERROR', f'0x1000\n{traceback.format_exc()}')
            await interaction.followup.send(lang.commands.module_error, ephemeral=True)

@tree.command(name="feedback", description=lang.slash.feedback)
@app_commands.choices(category=[
        app_commands.Choice(name="Bug report", value="0"),
        app_commands.Choice(name="Feature request", value="1"),
        app_commands.Choice(name="Other", value="2"),
])
async def feedback(interaction : discord.Interaction, category:app_commands.Choice[str]):
    """
    :param category: PRESS ENTER AFTER SELECTING CATEGORY
    """
    class Feedback(discord.ui.Modal, title='Invia il feedback'):
        input = discord.ui.TextInput(label="This form is anonymous", style=discord.TextStyle.long, required=True, placeholder="If you want a reply, add your name#0000 in this form")
 
        async def on_submit(self, interaction: discord.Interaction):
            now = datetime.now().strftime("[%d/%m/%y %H:%M:%S]")
            message = f"{now}-({interaction.id})\nUser submitted feedback **{category.name}**\n`{str(self.input.value)}`\n"
            try:
                if bot.dev != None:
                    await bot.dev.send(message)
            except Exception:
                await bot.dev.send(f"Someone sent a feedback: ID -> {interaction.id}")


            mPrint('INFO', message)
            with open('feedback.log', 'a') as f:
                f.writelines(message)

            await interaction.response.send_message(f'Thank you for your feedback ❤', ephemeral=True)
 
    await interaction.response.send_modal(Feedback())

    return


loadSettings()
try:
    bot.run(TOKEN)
except:
    mPrint('FATAL', f'Discord key absent or wrong. Unauthorized\n{traceback.format_exc()}')


#Birthday: 07/May/2022
