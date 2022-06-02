import asyncio
import os
import shutil
import json
import random
import copy
import sys
import traceback
import codecs
import discord #using py-cord dev version (discord.py v2.0.0-alpha)
from discord.utils import get
from discord.ext import commands
from typing import Union
from PIL import Image, ImageOps, ImageDraw, ImageFont

from mPrint import mPrint as mp
def mPrint(tag, value):mp(tag, 'bot', value)

#generate .env file if first startup:
if not os.path.isfile(".env"):
    mPrint('WARN', '.env file not found, add your tokens there.')
    with open('.env', 'w') as f:
        f.write("DISCORD_TOKEN={}\nSPOTIFY_ID={}\nSPOTIFY_SECRET={}\nGENIOUS_SECRET={}\n")
    sys.exit()

#custom modules
import chessBridge
import musicBridge


myServer = True

try: #This is specific to my own server, you can delete those lines as they do nothing for you
    import myStuff
except ModuleNotFoundError:
    myServer = False

#oh boy for whoever is looking at this, good luck
#I'm  not reorganizing the code for now (maybe willdo)

#Sensitive data is stored in a ".env" file
TOKEN = os.getenv('DISCORD_TOKEN')[1:-1]

#TODO what if user has not the keys, same for spotify in spotifyParser.py
GENIOUS = os.getenv('GENIOUS_SECRET')[1:-1]

SETTINGS_TEMPLATE = {"id":{"responseSettings":{"join_message":"A %name% piace il culo!","join_image":True,"leave_message":"Salutiamo felicemente il coglione di %name%","response_perc":35,"other_response":9,"response_to_bots_perc":35,"will_respond_to_bots":True,"use_global_words":True,"custom_words":[],"buttbot_replied":[]},"chessGame":{"default_board": "default","boards":{},"designs":{}},"saved_playlists":{},"youtube_search_overwrite":{}}}

intents = discord.Intents.all()
intents.members = True
intents.messages = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!'),
    intents=intents,
    owner_id=348199387543109654,
    status=discord.Status.online,
    activity = discord.Activity(type=discord.ActivityType.listening, name="!help")
)
# slash = SlashCommand(bot, sync_commands=True)

bot.remove_command("help")

settingsFile = "botFiles/guildsData.json"

global settings
settings = {}
with open(settingsFile, 'a'): pass #make setting file if it does not exist

with codecs.open('botFiles/lang.json', 'r', 'utf-8') as f:
    strings : dict[str:str] = json.load(f)['IT']#TODO add setting to change the language



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



#TODO deprecate this and just use dumpSettings()
def createSettings(id : int):
    id = int(id)
    with open(settingsFile, 'r') as f:
        temp = json.load(f)
    temp[id] = SETTINGS_TEMPLATE["id"]

    loadSettings()
  
def checkSettingsIntegrity(id : int):
    id = int(id)
    mPrint('DEBUG', f'Checking guildData integrity of ({id})')

    settingsToCheck = copy.deepcopy(settings[id])
    
    #check if there is more data than there should
    for key in settingsToCheck:
        if(key not in SETTINGS_TEMPLATE["id"]): #check if there is a key that should not be there (avoid useless data)
            del settings[id][key]
            mPrint('DEBUG', f'Deleting: {key}')

        if(type(settingsToCheck[key]) == dict):
            if(key in ["saved_playlists", "youtube_search_overwrite"]): continue #whitelist
            for subkey in settingsToCheck[key]:
                if(subkey not in SETTINGS_TEMPLATE["id"][key]): #check if there is a subkey that should not be there (avoid useless data)
                    del settings[id][key][subkey]
                    mPrint('DEBUG', f'Deleting: {subkey}')

    #check if data is missing
    for key in SETTINGS_TEMPLATE["id"]:
        if(key not in settings[id]): #check if there is a key that should not be there (avoid useless data)
            settings[id][key] = SETTINGS_TEMPLATE["id"][key]
            mPrint('DEBUG', f'Missing key: {key}')

        #it it's a dict also check it's keys
        if(type(SETTINGS_TEMPLATE["id"][key]) == dict):
            for subkey in SETTINGS_TEMPLATE["id"][key]:
                if(subkey not in settings[id][key]): #check if there is a key that should not be there (avoid useless data)
                    settings[id][key][subkey] = SETTINGS_TEMPLATE["id"][key][subkey]
                    mPrint('DEBUG', f'Missing subkey: {subkey}')

    dumpSettings()

    mPrint('DEBUG', 'Done.')

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

def getJoinImageData(membername) -> tuple[Image.Image, ImageFont.truetype, tuple[str, list[int]], tuple[int, list[int]]]:
    image_path = 'botFiles/join_images/'
    images = os.listdir(image_path)
    image_path = f'{image_path}{random.choice(images)}'

    if image_path[-5:] == '.json': 
        image_path = image_path[:-5] + '.png'
    image = Image.open(image_path)

    if os.path.isfile(f'{image_path[:-4]}.json'):
        with open(f'{image_path[:-4]}.json', 'r') as f:
            data = json.load(f)
    else:
        mPrint('WARN', f'{image_path[:-4]} HAS NO JSON EQUIVALENT, CREATE ONE TO ENSURE THE IMAGE IS GOOD')
        data = {
            "avatar_position": [10, 10],
            "avatar_size": 300,
            "text_position": [400,50],
            "text": "Benvenuto %name%!",
            "font_size": 50
        }

    font = ImageFont.truetype("botFiles/georgia.ttf", data["font_size"], encoding='utf-8')
    if '%name%' in data["text"]:
        data["text"] = data["text"].replace('%name%', membername, -1)

    return (
        image, 
        font, 
        [data["text"], data["text_position"]],
        (data["avatar_size"], data["avatar_position"])
    )

async def joinImageSend(member : discord.Member, guild : discord.Guild, channel : discord.TextChannel = None):
    imagepath = f'botFiles/{member.id}.png'
    try:
        await member.avatar.save(imagepath)
    except AttributeError:
        await member.default_avatar.save(imagepath)

    #load join image and add text
    joinImage, font, textData, avatarData = getJoinImageData(member.name)

    ImageDraw.Draw(joinImage).text((textData[1][0], textData[1][1]),f"{textData[0]}",(255,255,255),font=font)
    
    #edit avatar and paste it to joinimage
    mask = Image.open('botFiles/avatar_mask.png').convert("L").resize((avatarData[0],avatarData[0]))
    avatar = Image.open(imagepath).convert('RGBA').resize((avatarData[0],avatarData[0]))
    avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
    avatar.putalpha(mask)
    joinImage.paste(avatar, (avatarData[1][0],avatarData[1][1]), avatar)

    #send image to discord and delete it
    joinImage.save(imagepath)

    joinImage.close()
    mask.close()
    avatar.close()

    f = discord.File(imagepath)
    if channel == None:
        await guild.system_channel.send(file=f)
    else:
        await channel.send(file=f)
    os.remove(imagepath)

#           -----           DISCORD BOT COROUTINES           -----       #
@bot.event #exception logger
async def on_error(event, *args, **kwargs):
    mPrint('ERROR', f"DISCORDPY on_error:\n{traceback.format_exc()}")
    mPrint('WARN', "ARGS:")
    for x in args:
        mPrint('ERROR', {x})

@bot.event   ## BOT ONLINE
async def on_ready():
    if len(sys.argv) == 5 and sys.argv[1] == "RESTART":
        mPrint("INFO", "BOT WAS RESTARTED")
        guild = await bot.fetch_guild(sys.argv[2])
        channel = await guild.fetch_channel(sys.argv[3])
        message = await channel.fetch_message(sys.argv[4])
        await message.reply("Bot restarted")
        
    for guild in bot.guilds:
        mPrint("INFO",
            f'\nConnected to the following guild:\n'
            f'{guild.name} (id: {guild.id})'
        )

        members = '\n - '.join([member.name for member in guild.members])
        mPrint('DEBUG', f'Guild Members:\n - {members}')
        if (int(guild.id) not in settings):
            mPrint('DEBUG', '^ Generating settings for guild')
            createSettings(int(guild.id))

        checkSettingsIntegrity(int(guild.id))

@bot.event
async def on_member_join(member : discord.Member):
    mPrint("INFO", "join detected")
    joinString = settings[int(member.guild.id)]['responseSettings']['join_message']
    
    if(joinString != ''):
        joinString= joinString.replace('%name%', member.name)
        await member.guild.system_channel.send(joinString)

    if settings[int(member.guild.id)]['responseSettings']['join_image']:
        await joinImageSend(member, member.guild)

@bot.event
async def on_member_remove(member : discord.Member):
    leaveString = settings[int(member.guild.id)]['responseSettings']['leave_message']
    if(leaveString == ''): return
    leaveString= leaveString.replace('%name%', member.name)
    
    await member.guild.system_channel.send(leaveString)   
    mPrint("INFO", "join detected") 
    
@bot.command(name='getimage')
async def test(ctx : commands.Context):
    if ctx.author.id != 348199387543109654:
        return
    user = ctx.message.content.split()[1][2:-1]
    member = await ctx.guild.fetch_member(int(user))
    await joinImageSend(member, ctx.guild, ctx.channel)

@bot.command(name='bot_restart')
async def test(ctx : commands.Context):
    #ONLY FOR TESTING PURPOSES. DO NOT ABUSE THIS COMMAND
    if ctx.message.author.id == 348199387543109654 or ctx.guild.id == 694106741436186665:
        mPrint("WARN", "RESTARTING BOT")
        await ctx.send("WARNING, THIS COMMAND IS DISTRUPRIVE OF SERVICE BUT...\nok papi please wait...")
        os.system(f"bot.py RESTART {ctx.guild.id} {ctx.channel.id} {ctx.message.id}")
        sys.exit()

@bot.command(name='rawdump')
async def rawDump(ctx : commands.Context):
    await ctx.send(f'```JSON dump for {ctx.guild.name}:\n{json.dumps(settings[int(ctx.guild.id)], indent=3)}```')

@bot.command(name='joinmsg')
async def joinmsg(ctx : commands.Context):
    args = ctx.message.content.split()
    if len(args) == 1:
        #if join message is not empty
        if(settings[int(ctx.guild.id)]['responseSettings']['join_message'] != ''):
            await ctx.send(settings[int(ctx.guild.id)]['responseSettings']['join_message'])
        else:
            await ctx.send(strings['bot.joinmsg.none'])
    else:
        if args[1] == 'help':
            await ctx.send(strings["bot.joinmsg.info"])
            return
        elif args[1].lower() == 'false':
            settings[int(ctx.guild.id)]['responseSettings']['join_message'] = ''
            await ctx.send(strings["bot.joinmsg.deactivated"])
            return
        settings[int(ctx.guild.id)]['responseSettings']['join_message'] = ' '.join(args[1:])
        dumpSettings()
        await ctx.send(strings["bot.joinmsg.new_message"].replace("$str0", settings[int(ctx.guild.id)]['responseSettings']['join_message']))

@bot.command(name='leavemsg')
async def leavemsg(ctx : commands.Context):
    args = ctx.message.content.split()
    if len(args) == 1:
        #if join message is not empty
        if(settings[int(ctx.guild.id)]['responseSettings']['leave_message'] != ''):
            await ctx.send(settings[int(ctx.guild.id)]['responseSettings']['leave_message'])
        else:
            await ctx.send(strings["bot.leavemsg.none"])
    else:
        if args[1] == 'help':
            await ctx.send(strings["bot.leavemsg.info"])
            return
        elif args[1].lower() == 'false':
            settings[int(ctx.guild.id)]['responseSettings']['leave_message'] = ''
            await ctx.send(strings["bot.joinmsg.deactivated"])
            return
        settings[int(ctx.guild.id)]['responseSettings']['leave_message'] = ' '.join(args[1:])
        dumpSettings()
        await ctx.send(strings["bot.leavemsg.new_message"].replace("$str0", settings[int(ctx.guild.id)]['responseSettings']['leave_message']))

@bot.command(name='joinimage')
async def joinmsg(ctx : commands.Context):
    args = ctx.message.content.split()
    if len(args) != 1:
        if args[2].lower == 'true':
            settings[int(ctx.guild.id)]['responseSettings']['join_image'] = True
        else:
            settings[int(ctx.guild.id)]['responseSettings']['join_image'] = False
        dumpSettings()

    await ctx.send(f"joinimage: {settings[int(ctx.guild.id)]['responseSettings']['join_image']}")

@bot.command(name='resp') 
async def perc(ctx : commands.Context):  ## RESP command
    arg = ctx.message.content.replace('!resp', '')
    respSettings = settings[int(ctx.guild.id)]["responseSettings"]

    if(arg == ''):
        await ctx.send(strings["bot.resp.info"].replace("$perc", str(respSettings["response_perc"])))
        return
    
    arg = arg.lower().split()

    affirmative = ['true', 'yes', 'si', 'vero']
    negative = ['false', 'no', 'false']
    validResponse = False
    if(arg[0].strip('s') == 'bot'):
        mPrint("DEBUG", f"resp comand: {arg}")
        if len(arg) == 1:
            await ctx.send(strings["bot.resp.resp_to_bots.info"].replace("$s1",respSettings["will_respond_to_bots"]).replace("$s2", f'{respSettings["response_to_bots_perc"] if respSettings["will_respond_to_bots"] else 0}'))
            return

        if(arg[1].isnumeric()):
            await ctx.send(strings["bot.resp.resp_to_bots.edit"].replace('$s1', f'{arg[1]}'))
            settings[ctx.guild.id]['responseSettings']['response_to_bots_perc'] = int(arg[1])
            dumpSettings()
            #updateSettings(int(ctx.guild.id), 'response_to_bots_perc', int(arg[1]))
            return
        
        if arg[1] in affirmative:
            response = strings['bot.resp.resp_to_bots.affirmative']
            validResponse = True
            r = True
        elif arg[1] in negative:
            response = strings['bot.resp.resp_to_bots.negative']
            validResponse = True
            r = False
        else:
            response = strings['bot.resp.resp_to_bots.invalid']
            r = -1
        await ctx.send(response)
        if validResponse and r != -1:
            settings[ctx.guild.id]['responseSettings']['will_respond_to_bots'] = r
            dumpSettings()
            # updateSettings(ctx.guild.id, 'will_respond_to_bots', arg[1])
            return

    newPerc = int(arg[0].strip("%"))

    if (respSettings['response_perc'] == newPerc):
        await ctx.send(strings['nothing_changed'])
        return

    await ctx.send(strings['bot.resp.newperc'].replace("$s2", str(newPerc)))

    mPrint('INFO', f'{ctx.author} set response to {arg}%')

    settings[ctx.guild.id]['responseSettings']['will_respond_to_bots'] = r
    dumpSettings()

    settings[int(ctx.guild.id)]['resp_settings']['response_perc'] = newPerc #TODO add a command for other_perc
    dumpSettings()


@bot.command(name='words', aliases=['parole'])
async def words(ctx : commands.Context): #send an embed with the words that the bot knows
    args = ctx.message.content.split()
    if len(args) > 1: #add new words
        newWord = ' '.join(args[1:])
        if args[1].lower() == 'del':
            delWord = int(args[2])
            if len(settings[int(ctx.guild.id)]['responseSettings']['custom_words']) > delWord:
                del settings[int(ctx.guild.id)]['responseSettings']['custom_words'][delWord]
                await ctx.send(strings['done'])
            else:
                await ctx.send(strings['bot.words.id_not_found'])
            return
        
        if args[1].lower() == 'edit':
            editWord = int(args[2])
            if len(settings[int(ctx.guild.id)]['responseSettings']['custom_words']) > editWord:
                settings[int(ctx.guild.id)]['responseSettings']['custom_words'][editWord] = ' '.join(args[3:])
                await ctx.send(strings['done'])
            else:
                await ctx.send(strings['bot.words.id_not_found'])
            return

        if args[1].lower() == 'add':
            newWord = ' '.join(args[2:])
        
        if args[1].lower() == 'usedefault':
            if len(args) == 3:
                settings[int(ctx.guild.id)]["responseSettings"]["use_global_words"] = args[2]
                await ctx.send(f'useDefault: {args[2]}')
                dumpSettings()
                return
            else:
                await ctx.send(f'usage: `!words useDefault [true|false]`')
        
        settings[int(ctx.guild.id)]['responseSettings']['custom_words'].append(newWord)
        await ctx.send(strings['bot.words.learned'])
        dumpSettings()
        return

    #1. Send a description
    custom_words = settings[int(ctx.guild.id)]['responseSettings']['custom_words']
    description = strings['bot.words.info'].replace('$s1', ctx.guild.name)

    if not settings[int(ctx.guild.id)]['responseSettings']['use_global_words']:
       description += strings['bot.words.use_global_words'].replace('$s1', ctx.guild.name)
        
    embed = discord.Embed(
        title = strings['bot.words.known_words'],
        description = description,
        colour = 0xf39641
    )

    value = ''
    #2a. get the global words
    botWords = getWord(True)

    #2b. if the guild uses the global words, append them to value
    if settings[int(ctx.guild.id)]['responseSettings']['use_global_words']:
        #is server uses default words
        value = '\n'.join(botWords)
        embed.add_field(name = strings['bot.words.bot_words'], value=value)
        value = '' 

    #2c. append the guild(local) words to value
    for i, cw in enumerate(custom_words):
        value += f'[`{i}`]: {cw}\n'
    if value == '': value=strings['bot.words.no_guild_words']
    embed.add_field(name = strings['bot.words.guild_words'].replace('$s1', ctx.guild.name), value=value)
    
    #3. send the words
    await ctx.send(embed=embed)

@bot.command(name = 'help')
async def embedpages(ctx : commands.Context):
    e = discord.Embed (
        title = 'CuloBot',
        description = strings["bot.help.description"],
        colour = 0xf39641
    ).set_footer(text=strings["bot.help.footer"])
    
    e.set_thumbnail(url='https://i.pinimg.com/originals/b5/46/3c/b5463c3591ec63cf076ac48179e3b0db.png')

    page0 = e.copy().set_author(name='Help 0/5, Info', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page1 = e.copy().set_author(name='Help 1/5, Culo!', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page2 = e.copy().set_author(name='Help 2/5, Music!', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page3 = e.copy().set_author(name='Help 3/5, CHECKMATE', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page4 = e.copy().set_author(name='Help 4/5, Misc', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    
    #Page 0 Info
    page0.add_field(name=strings["bot.help.advice"][0], value=strings["bot.help.advice"][1])

    #Page 1 settings
    page1.add_field(name='!resp', value=strings["bot.help.resp.info"], inline=False)#ok
    page1.add_field(name='!resp [x]%', value=strings["bot.help.resp.set"], inline=False)#ok
    page1.add_field(name='!resp bot', value=strings["bot.help.resp.bots.info"], inline=False)#ok
    page1.add_field(name='!resp bot [x]%', value=strings["bot.help.resp.bots.set"], inline=False)#ok
    page1.add_field(name='!resp bot [True|False]', value=strings["bot.help.resp.bots.bool"], inline=False)#ok
    page1.add_field(name='!resp useDefault [True|False]', value=strings["bot.help.resp.use_default_words"], inline=False)#ok

    page1.add_field(name='!words', value=strings["bot.help.words.words"], inline=False)
    page1.add_field(name='!words [add <words>|del <id>|edit<id> <word>]', value=strings["bot.help.words.edit"], inline=False)
    page1.add_field(name=strings["bot.help.words.structure"][0], value=strings["bot.help.words.structure"][1], inline=False)

    #Page 2 music
    page2.add_field(name='!playlist', value=strings["bot.help.playlist.info"], inline=False)#ok
    page2.add_field(name='!playlist [add|edit] <name> <link>', value=strings["bot.help.playlist.edit"], inline=False)#ok
    page2.add_field(name='!playlist [remove|del] <name>', value=strings["bot.help.playlist.remove"], inline=False)#ok
    page2.add_field(name='!play <song>', value=strings["bot.help.playlist.play"], inline=False)#ok
    page2.add_field(name='!p <song>', value=strings["bot.help.playlist.p"], inline=False)#ok
    page2.add_field(name=strings["bot.help.player.info"][0], value=strings["bot.help.player.info"][1], inline=False)#ok
    page2.add_field(name='skip [x]', value=strings["bot.help.player.skip"], inline=False)#ok
    #page2.add_field(name='lyrics', value=strings["bot.help.player.lyrics"], inline=False)#ok
    page2.add_field(name='shuffle', value=strings["bot.help.player.shuffle"], inline=False)#ok
    page2.add_field(name='pause', value=strings["bot.help.player.pause"], inline=False)#ok
    page2.add_field(name='resume', value=strings["bot.help.player.resume"], inline=False)#ok
    page2.add_field(name='stop', value=strings["bot.help.player.stop"], inline=False)#ok
    page2.add_field(name='clear', value=strings["bot.help.player.clear"], inline=False)#ok
    page2.add_field(name='loop [song | queue]', value=strings["bot.help.player.loop"], inline=False)#ok
    page2.add_field(name='restart', value=strings["bot.help.player.restart"], inline=False)#ok
    page2.add_field(name='queue', value=strings["bot.help.player.queue"], inline=False)#ok
    page2.add_field(name='remove <x>', value=strings["bot.help.player.remove"], inline=False)#ok
    page2.add_field(name='mv <x> <y>', value=strings["bot.help.player.mv"], inline=False)#ok
    page2.add_field(name='!play <song>', value=strings["bot.help.player.play"], inline=False)#ok
    page2.add_field(name='!p <song>', value=strings["bot.help.player.p"], inline=False)#ok
    page2.add_field(name='!playnext <song>', value=strings["bot.help.player.playnext"], inline=False)#ok
    page2.add_field(name='!pnext <song>', value=strings["bot.help.player.pnext"], inline=False)#ok
    
    #TODO continue adding translations

    #Page 3 chess
    page3.add_field(name='!chess [@user | @role] [fen="<FEN>"] [board=<boardname>] [design=<deisgn>]', 
    value='Gioca ad una partita di scacchi!\n\
     [@user]: Sfida una persona a scacchi\n\
     [@role]: Sfida un ruolo a scacchi\n\
     [fen="<FEN>"]: usa una scacchiera preimpostata\n\
     [board=<boardname>]: usa una delle scacchiere salvate\n\
     [design=<design>: usa uno dei design disponibili', inline=False)#ok
    page3.add_field(name='e.g.:', value='```!chess board=board2\n!chess\n!chess @Admin\n!chess fen="k7/8/8/8/8/8/8/7K"```')

    page3.add_field(name='!chess boards', value='vedi i FEN disponibili', inline=False)#ok
    page3.add_field(name='!chess design [see|add|del|edit]', value='vedi le scacchiere disponibili `!chess design` per più informazioni', inline=False)#ok
    page3.add_field(name='!chess see <name | FEN>', value='genera l\'immagine della scacchiera', inline=False)#ok
    page3.add_field(name='!chess add <name> <FEN>', value='aggiungi una scacchiera', inline=False)#ok
    page3.add_field(name='!chess remove <name>', value='rimuovi una scacchiera', inline=False)#ok
    page3.add_field(name='!chess rename <name> <newName>', value='rinomina una scacchiera', inline=False)#ok
    page3.add_field(name='!chess edit <name> <FEN>', value='modifica una scacchiera', inline=False)#ok

    #Page 4 misc
    page4.add_field(name='!ping', value='Pong!', inline=False)#ok
    page4.add_field(name='!rawdump', value='manda un messaggio con tutti i dati salvati di questo server', inline=False)#ok
    page4.add_field(name='joinmsg [msg]', value="Mostra il messaggio di benvenuto del bot, usa `!joinmsg help` per più informazioni\n", inline=False)
    page4.add_field(name='leavemsg [msg]', value="Mostra il messaggio di addio del bot, usa `!joinmsg help` per più informazioni\n", inline=False)
    page4.add_field(name='joinimage [True|False]', value="Specifica se il bot può inviare o meno un immagine casuale quando entra qualcuno nel server\n", inline=False)

    #fotter for page 1
    page0.add_field(name='Source code', value="https://github.com/NotLatif/CuloBot", inline=False)
    page0.add_field(name='Problemi? lascia un feedback qui', value="https://github.com/NotLatif/CuloBot/issues", inline=False)
    
    page1.add_field(name='Source code', value="https://github.com/NotLatif/CuloBot", inline=False)
    page1.add_field(name='Problemi? lascia un feedback qui', value="https://github.com/NotLatif/CuloBot/issues", inline=False)
    
    pages = [page0, page1, page2, page3, page4]

    msg = await ctx.send(embed = pages[0])

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
            if i < len(pages) - 1:
                i += 1
                await msg.edit(embed = pages[i])
        elif str(emoji) == '⏭':
            i = len(pages) -1
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
    mPrint('INFO', f'ping detected: {pingms} ms')

@bot.command(name='chess', pass_context=True) #CHESS GAME (very long def)
async def chessGame(ctx : commands.Context):
    await ctx.channel.typing()
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
    mPrint('DEBUG', f'chessGame: issued command: chess\nauthor: {ctx.message.author.id}, args: {args}')

    #useful for FENs: eg   (!chess) game fen="bla bla bla" < str.strip will return ["game", "fen=bla", "bla", "bla"]
    args = splitString(args)                    #wheras splitString will return ["game", "fen=", "bla", "bla", "bla"]
    gameFEN = ''
    gameBoard = settings[int(ctx.guild.id)]["chessGame"]["default_board"]
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
            if settings[int(ctx.guild.id)]['chessGame']['boards'] != {}:
                guildBoards = ''
                for b in settings[int(ctx.guild.id)]['chessGame']['boards']:
                    guildBoards += f"**{b}**: {settings[int(ctx.guild.id)]['chessGame']['boards'][b]}\n"
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
                if settings[int(ctx.guild.id)]['chessGame']['designs'] != {}:
                    guildDesigns = ''
                    for b in settings[int(ctx.guild.id)]['chessGame']['designs']:
                        guildDesigns += f"**{b}**: {settings[int(ctx.guild.id)]['chessGame']['designs'][b]}\n"
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
                    if args[2] in settings[int(ctx.guild.id)]['chessGame']['designs']:
                        colors = settings[int(ctx.guild.id)]['chessGame']['designs'][args[2]]
                        designPath = chessBridge.chessMain.gameRenderer.renderBoard(colors, ctx.message.id)
                        with open(designPath+'chessboard.png', "rb") as fh:
                            f = discord.File(fh, filename=(designPath + 'chessboard.png'))
                            await ctx.send(file=f)
                        shutil.rmtree(designPath, ignore_errors=False, onerror=None)
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
                        if d in settings[int(ctx.guild.id)]['chessGame']['designs']:
                            design = settings[int(ctx.guild.id)]['chessGame']['designs'].pop(d)
                            await ctx.send(f'Ho eliminato {d}: {design}')
                            dumpSettings()
                        else:
                            await ctx.send("Design non trovato, usa `!chess design` per vedere i design disponibili")
                else:
                    await ctx.send('Usage: `!chess design del <name>`')
                return 0
            
            def parseHEX(hex1, hex2) -> list:
                colors = [hex1, hex2]
                possible = ['#', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
                for i, hex in enumerate(colors): #foreach color
                    mPrint('DEBUG', f'parsing hex {hex}')
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
                    if args[2] in settings[int(ctx.guild.id)]['chessGame']['designs']:
                        colors = parseHEX(args[3], args[4])
                        if colors == '0':
                            await ctx.send(f"Invalid hex {args[3]} {args[4]}")
                            return -2
                        settings[int(ctx.guild.id)]['chessGame']['designs'][args[2]] = colors
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
                    if args[2] in settings[int(ctx.guild.id)]['chessGame']['designs']:
                        await ctx.send(f'Il design esiste già. Usa `!chess design edit {args[2]} {args[3]} {args[4]} se vuoi modificarlo`')
                        return -2
                    colors = parseHEX(args[3], args[4])
                    if colors == '0':
                        await ctx.send(f"Invalid hex {args[3]} {args[4]}")
                        return -2
                    settings[int(ctx.guild.id)]['chessGame']['designs'][args[2]] = colors
                    await ctx.send(f"Design aggiunto: **{args[2]}**: {colors}")
                    dumpSettings()
                else:
                    await ctx.send('Usage: `!chess design add <nome> <colore1> <colore2>`\ne.g.:`!chess design edit test1 #24AB34 #8E24FF`')
                return 0

        elif args[0] == 'seeboard' or args[0] == 'see': # renders a FEN and send it in chat
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
                mPrint('DEBUG', f'rendered image: {image}')

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
                if args[1] not in settings[int(ctx.guild.id)]['chessGame']['boards']:
                    #iii. append the board and dump the json data
                    settings[int(ctx.guild.id)]['chessGame']['boards'][args[1]] = args[2]
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
                value = settings[int(ctx.guild.id)]['chessGame']['boards'][args[1]]
                
                #iii. delete the board
                del settings[int(ctx.guild.id)]['chessGame']['boards'][args[1]]#it does not exist yet
                
                #iv. create a new board with the same FEN, but a new name and dump the json data
                settings[int(ctx.guild.id)]['chessGame']['boards'][args[2]] = value
                dumpSettings()
                await ctx.send('Fatto!')
            else:
                await ctx.send("Usage: `!chess rename <name> <newname>`")
            return 0
        
        elif args[0] == 'editboard' or args[0] == 'edit': #edit a board
           #i. avoid indexError because of the dumb user
            if len(args) == 3:
                #ii. Check if board exists, if not notify the user
                if args[1] not in  settings[int(ctx.guild.id)]['chessGame']['boards']:
                    await ctx.send(f"Non posso modificare qualcosa che non esiste ({args[1]})")
                    return -2

                #iii. edit the FEN, and dump the data
                settings[int(ctx.guild.id)]['chessGame']['boards'][args[1]] = args[2]
                dumpSettings()
                await ctx.send('Fatto!')
            else:
                await ctx.send("Usage: `!chess edit <name> <newFEN>`")
            return 0
        
        elif args[0] == 'deleteboard' or args[0] == 'delete': #deletes a board
            #i. avoid indexError because of the dumb user
            if len(args) == 2:
                #ii. Check if board exists, if not notify the user
                if args[1] in settings[int(ctx.guild.id)]['chessGame']['boards']:

                    #delete the board, dump the settings and send the FEN in chat
                    fen = settings[int(ctx.guild.id)]['chessGame']['boards'].pop(args[1])
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
                mPrint('DEBUG', f'found FEN -> {gameFEN}')

            if i.lower()[:6] == 'board=':
                gameBoard = i[6:]
                mPrint('DEBUG', f'found board -> {gameFEN}')
            
            if i.lower()[:7] == 'design=':
                design = i[7:]
                mPrint('DEBUG', f'found design -> {design}')

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
        if gameBoard in settings[int(ctx.guild.id)]['chessGame']['boards']: #board in guild data
            board = ('FEN', settings[int(ctx.guild.id)]['chessGame']['boards'][gameBoard])
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
        if design in settings[int(ctx.guild.id)]['chessGame']['designs']:
            designName = design
            design = settings[int(ctx.guild.id)]['chessGame']['designs'][design]
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

    mPrint('DEBUG','chessGame: challenge["whitelist"]')
    mPrint('DEBUG', challenge['whitelist'])

    #add reactions to the embed that people can use as buttons to join the teams
    await playerFetchMsg.add_reaction(r1)
    await playerFetchMsg.add_reaction(r2)
    await playerFetchMsg.add_reaction("❌") #if the author changes their mind


    def fetchChecker(reaction : discord.Reaction, user : Union[discord.Member, discord.User]) -> bool: #this is one fat checker damn
        """Checks if user team join request is valid"""

        # async def remove(reaction, user): #remove invalid reactions
        #     await reaction.remove(user)   #will figure out some way

        mPrint('DEBUG', f'chessGame: Check: {reaction}, {user}\nchallenge["whitelist"]: {challenge["whitelist"]}\navailable: {availableTeams}\n--------')
        
        #1- prevent bot from joining teams
        if (user == bot.user): 
            return False
        
        if (reaction.message.id != playerFetchMsg.id): #the reaction was given to another message
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
                mPrint('DEBUG', 'chessGame: User is author') #check the user BEFORE the role, so if the user has the role it does not get deleted
                challenge['authorJoined'] = True #prevent author from joining 2 teams
                availableTeams.remove(str(reaction.emoji)) #prevent player/s from joining the same team
                return True 
            
            #if the user joining isn't the author but has the role requested
            elif user.get_role(challengedRole) != None: #user has the role  
                mPrint('DEBUG', 'chessGame: User has required role')
                challenge['whitelist'] = [] #delete the role to prevent two players with the role from joining (keeping out the author)
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
        await asyncio.sleep(random.randrange(0,2))

    except asyncio.TimeoutError: #players did not join in time
        embed = discord.Embed(
            title = 'Non ci sono abbastanza giocatori.',
            colour = 0xdc143c
        )
        await ctx.send(embed=embed)
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

@bot.command(name='playlist', pass_context=True, aliases=['playlists']) #
async def playSong(ctx : commands.Context):
    request = ctx.message.content.split()
    await ctx.channel.typing()
    if len(request) == 1: #send the playlist list list to user
        embed = discord.Embed(
            title=f"Saved playlists for {ctx.guild.name}",
            description="**Commands:** \n!playlist [add|edit] <name> <link>\n!playlist remove <name>",
            color=0x1ed760
        )
        for plist in settings[int(ctx.guild.id)]["saved_playlists"]:
            urls=''
            for i, t in enumerate(settings[int(ctx.guild.id)]["saved_playlists"][plist]):
                urls += f'**{i}**: {t}\n' 
            embed.add_field(name=plist, value=urls, inline=False)
        await ctx.send(embed=embed)
        return    

    else:
        if request[1] == "add":
            #!playlist add <name> <url1[,url2, ..., urln]> TODO help
            if len(request) >= 4: #create playlist with songs/playlistsT
                tracks = []
                errors = ''
                for x in request[3:]: #foreach song/splaylist
                    #search for the song/playlist to make sure it won't fail when playing it and add it to the list
                    isUrlValid = musicBridge.evalUrl(x)
                    if isUrlValid == False:
                        errors += f"Error: Could not find song/playlist {x}\n"
                    else:
                        if "open.spotify.com" not in x and "youtube.com" not in x:
                            mPrint('MUSIC', f'Searching for user requested song: ({x})')
                            x = musicBridge.musicPlayer.youtubeParser.searchYTurl(x)
                        tracks.append(x)
                
                if errors != '':
                    embed = discord.Embed(
                        title="ERRORS:",
                        description=errors,
                        color=0xff0000
                    )
                    await ctx.send(embed=embed)

                if tracks == []:
                    await ctx.send('Error: every song/playlist failed')
                    return

                trackList = ''
                for i, t in enumerate(tracks):
                    trackList += f"\n**{i}**. {t}"

                #Save the song/playlist URL in a list of one element and inform the user
                settings[int(ctx.guild.id)]["saved_playlists"][request[2]] = tracks
                
                embed = discord.Embed(title = f"Playlist {request[2]}: ", description=trackList)
                await ctx.send(f"Playlist {request[2]} -> {trackList}")
                dumpSettings()
                await ctx.message.add_reaction("👌")
                return
            else:
                await ctx.send('Usage: !playlist add <name> <url1> [url2] [url3] ... [urln]')

        elif request[1] in ["remove", "del"]:
            if len(request) == 3:
                try:
                    del settings[int(ctx.guild.id)]["saved_playlists"][request[2]]
                    await ctx.send(f"Deleted {request[2]}.")
                    dumpSettings()
                except KeyError:
                    await ctx.send("La playlist non esisteva.")
                return

        # operations on existing playlist !playlist <name> [add|remove]
        elif request[1] in settings[int(ctx.guild.id)]["saved_playlists"]:
            if len(request) > 2:
                #!playlist <name> add <url1[, url2, ..., urln]> TODO help
                if request[2] == 'add': #append a song to the playlist request[2]
                    if len(request) >= 3:
                        tracks = []
                        errors = ''
                        for x in request[3:]: #!playlist <name> add <url1[, url2, ..., urln]> TODO help
                            print(x)
                            isUrlValid = musicBridge.evalUrl(x)
                            if isUrlValid == False: #404
                                errors += f"Error: Could not find song/playlist {x}\n"
                                return
                            elif x in settings[int(ctx.guild.id)]["saved_playlists"][request[1]]:
                                errors += f"Error: Song {x} is already present in {request[1]}\n"
                            else:
                                if "open.spotify.com" not in x and "youtube.com" not in x:
                                    mPrint('MUSIC', f'Searching for user requested song: ({x})')
                                    x = musicBridge.musicPlayer.youtubeParser.searchYTurl(x)
                                tracks.append(x)
                            
                        if errors != '':
                            embed = discord.Embed(
                                title="ERRORS:",
                                description=errors,
                                color=0xff0000
                            )
                            await ctx.send(embed=embed)

                        if tracks == []:
                            await ctx.send('FATAL, every song/playlist failed, playlist was not modified.')
                            return
                        trackList = ''

                        #append the song/playlist URL in a list of one element and inform the user
                        #add the new urls to the settings
                        for t in tracks:
                            settings[int(ctx.guild.id)]["saved_playlists"][request[1]].append(t)
                        #prepare message and send the playlist to the server
                        for i, t in enumerate(settings[int(ctx.guild.id)]["saved_playlists"][request[1]]):
                            trackList += f"\n**{i}**. {t}"
                        embed = discord.Embed(title = f"Playlist {request[1]}: ", description=trackList)
                        await ctx.send(embed=embed)
                        dumpSettings()
                        await ctx.message.add_reaction("👌")
                        return
                    else:
                        await ctx.send("Usage: !playlist <name> add <url1[, url2, ..., urln]>")
                
                elif request[2] == 'remove': #!playlist <name> remove TODO help
                    if len(request) == 3:
                        tracks = settings[int(ctx.guild.id)]["saved_playlists"][request[1]]
                        del settings[int(ctx.guild.id)]["saved_playlists"][request[1]]
                        trackList = ''
                        for i, t in enumerate(tracks):
                            trackList += f"\n**{i}**. {t}"
                        embed = discord.Embed(
                            title=f"❌Deleted playlist {request[1]}❌",
                            description=trackList
                        )
                        await ctx.send(embed=embed)
                        dumpSettings()
                        return

                    elif len(request) == 4: #!playlist <name> remove [urlindex] TODO help
                        if request[3].isnumeric() and int(request[3]) < len(settings[int(ctx.guild.id)]["saved_playlists"][request[1]]):
                            trackList = ''
                            for i, t in enumerate(settings[int(ctx.guild.id)]["saved_playlists"][request[1]]):
                                if i == int(request[3]): 
                                    trackList += f"\n❌ **{i}**. {t}"
                                else:
                                    trackList += f"\n**{i}**. {t}"
                            
                            settings[int(ctx.guild.id)]["saved_playlists"][request[1]].pop(int(request[3]))
                            
                            if len(settings[int(ctx.guild.id)]["saved_playlists"][request[1]]) == 0:
                                del settings[int(ctx.guild.id)]["saved_playlists"][request[1]]

                            embed = discord.Embed(
                                title=f"Removed from playlist {request[1]}:",
                                description=trackList
                            )
                            await ctx.send(embed=embed)
                            dumpSettings()
                            return
                        else:
                            await ctx.send(f'!playlist <name> remove [id]<id must be a number, you can see the track ids with !playlist {request[1]}')
                    else:
                        await ctx.send('Usage: !playlist <name> remove [id], se id non è presente elimina tutta la playlist')
                    
            else: #!playlist <name> TODO help
                tracks = settings[int(ctx.guild.id)]["saved_playlists"][request[1]]
                trackList = ''
                for i, t in enumerate(tracks):
                    trackList += f"\n**{i}**. {t}"
                embed = discord.Embed(
                    title=f"Playlist {request[1]}",
                    description=trackList
                )
                await ctx.send(embed=embed)
        
        else:
            await ctx.send("Playlist does not exist.")
    
@bot.command(name='play', pass_context=True, aliases=['p']) #Player
async def playSong(ctx : commands.Context):
    await ctx.channel.typing()
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected():
        return

    request = ctx.message.content.split()
    if len(request) == 1:
        await ctx.send("Usage: !play <song>\nsong can be: [spotify URL | youtube URL | name of a saved playlist | name of the song]")
    else:
        #user searched a link
        playContent = ''
        if "open.spotify.com" in request[1] or "youtube.com" in request[1] or "youtu.be" in request[1]:
            mPrint('INFO', f'FOUND SUPPORTED URL: {request[1]}')
            playContent = ctx.message.content.split()[1]

        #user wants a saved playlist
        elif request[1] in settings[int(ctx.guild.id)]["saved_playlists"]:
            trackURL_list : list = settings[int(ctx.guild.id)]["saved_playlists"][request[1]]
            mPrint('INFO', f'FOUND SAVED PLAYLIST: {trackURL_list}')
            playContent = trackURL_list
        
        #user wants to search for a song
        else:
            mPrint('MUSIC', f'Searching for user requested song: ({" ".join(request[1:])})')
            trackURL = musicBridge.musicPlayer.youtubeParser.searchYTurl(' '.join(request[1:]))
            mPrint('INFO', f'SEARCHED SONG URL: {trackURL}')
            playContent = trackURL
        
        await musicBridge.play(playContent, ctx, bot, settings[int(ctx.guild.id)]['youtube_search_overwrite'])

@bot.command(name='suggest', pass_context=True) #Player
async def playSong(ctx : commands.Context):
    await ctx.channel.typing()
    await asyncio.sleep(2) #ensure that file exists
    if os.path.isfile(f'botFiles/{str(ctx.guild.id)}.json'):
        with open(f'botFiles/{str(ctx.guild.id)}.json') as f:
            newOverwrites = json.load(f)
            settings[ctx.guild.id]['youtube_search_overwrite'] = newOverwrites
            dumpSettings()
            await ctx.send('Done')
    else:
        await ctx.send('C\'è stato un errore...')

@bot.event   ## DETECT AND RESPOND TO MSG
async def on_message(message : discord.Message):
    if len(message.content.split()) == 0: return

    global settings

    if message.content.split()[0] in musicBridge.cmds: 
        return #needed to not conflict with music player
    
    await bot.process_commands(message)

    respSettings = settings[int(message.guild.id)]["responseSettings"]

#--------------------------------- This is specific to my server
    if myServer:
        value = await myStuff.parseData(message, settings, respSettings, bot)
        if value != None:
            settings = value
            dumpSettings()
#--------------------------------- you can safely delete this

    #don't respond to self, commands, messages with less than 2 words
    if message.author == bot.user or message.content[0] in ['!', "/", "?", '|', '$', "&", ">", "<"] or len(message.content.split()) < 2: 
        return

    if 'word' in message.content: #for future implementation, respond to specific string
        pass
    
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
    mPrint('DEBUG', f'responded to message <resp_rate: {respSettings["response_perc"]}%>')


loadSettings()
try:
    bot.run(TOKEN)
except:
    mPrint('FATAL', f'Discord key absent or wrong. Unauthorized\n{traceback.format_exc()}')

#Birthday: 07/May/2022