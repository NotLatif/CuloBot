import sys
import discord
from discord.ext import commands
import traceback
import asyncio
from random import shuffle
#import lyricsgenius as lg

sys.path.insert(0, 'music/')
import spotifyParser
import youtubeParser
import musicPlayer

from mPrint import mPrint as mp
def mPrint(tag, text):
    mp(tag, 'musicBridge', text)

def parseUrl(url):
    if 'spotify.com' in url:
        try:
            tracks = spotifyParser.getSongs(url)
        except Exception:
            mPrint('ERROR', f"Spotify parser error:\nurl = {url}\n{traceback.format_exc()}")
            return None

    elif 'youtube.com' in url:
        try:
            tracks = youtubeParser.getSongs(url)
        except Exception:
            mPrint('ERROR', f"Youtube parser error:\nurl = {url}\n{traceback.format_exc()}")
            return None


    return tracks

async def play(url, ctx : commands.Context, bot : discord.Client, GENIOUS_KEY : str):
    #genius = lg.Genius('Client_Access_Token_Goes_Here', skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True)

    tracks = parseUrl(url)
    if tracks == None:
        await ctx.send(f"An error occurred while looking for song(s).")
        return
    shuffle(tracks)

    last5 = ''
    for i in range(6):
        last5 += f"**{i}**- `                                      `\n"
        #last5 += f'**{i}**- {x["trackName"]} [by: {x["artist"]}]\n'
     
    embed = discord.Embed(
        title=f'Loading...',
        description=f'Now Playing: **{tracks[0]["trackName"]}**\n▂▂▂▂▂▂▂▂▂▂ (00:00 - 00:00)\n',
        color=0xff866f
    )

    if( tracks[0]["artist"] != ''):
        embed.add_field(name='Author:', value=f'{tracks[0]["artist"]}', inline=True)
    if ( last5 != "" ):
        embed.add_field(name='Last 5 in queue', value=f'{last5}', inline=False)
    embed.set_footer(text='🍑 the best bot 🎶 https://notlatif.github.io/CuloBot/#MusicBot')
     
    try: #try connecting to vc
        vchannel = bot.get_channel(ctx.author.voice.channel.id)
    except AttributeError:
        await ctx.send('Devi essere in un culo vocale per usare questo comando.')
        await ctx.message.add_reaction('❌')
        return
    except discord.ClientException:
        await ctx.send('Sono già in un altro canale vocale.')
        await ctx.message.add_reaction('❌')
    else:
        voice : discord.VoiceClient = await vchannel.connect()
        await ctx.message.add_reaction('🍑')

    embedMSG = await ctx.send(embed=embed)

    emojis = {
        "stop": "⏹",
        "previous": "⏮",
        "play_pause": "⏯",
        "skip": "⏭",
        "shuffle": "🔀",
        "loop": "🔂",
        "loop queue": "🔁",
    }
    

    player = musicPlayer.Player(voice, tracks)
    messageHandler = musicPlayer.MessageHandler(player, embedMSG)
    
    try:
        playerTask = asyncio.create_task(player.starter())
        messageTask = asyncio.create_task(messageHandler.start())

    except Exception:
        await voice.disconnect()
        voice.cleanup()
        mPrint('ERROR', traceback.format_exc())
        return

    def check(m : discord.Message):	#check if message was sent in thread using ID
        return m.author != bot.user and m.channel.id == ctx.channel.id

    def checkEmoji(reaction : discord.Reaction, user):
        return user != bot.user and reaction.message.id == embedMSG.id


    async def actions(pTask : asyncio.Task, userMessage : discord.Message, textInput = True):
        
        if textInput:
            userInput = userMessage.content
        else:
            userInput = userMessage

        mPrint('TEST', f'{userInput}; {textInput}')

        if len(userInput.split()) == 0:
            return

        if userInput.split()[0] == 'previous':
            mPrint('USER', 'previous song')
            pTask.cancel()
            if pTask.cancelled() == False: 
                mPrint("WARN", "task was not closed.")
                pTask.cancel()
            
            if(player.currentSong != player.previousSong):
                player.queue.insert(0, player.currentSong)
            player.queue.insert(0, player.previousSong)
            
            pTask = asyncio.create_task(player.skip())
            await messageHandler.updateEmbed()

        if userInput.split()[0] == 'skip':
            mPrint('USER', 'skipped song')
            skip = userInput.split()
            pTask.cancel()
            if pTask.cancelled() == False: 
                mPrint("WARN", "task was not closed.")
                pTask.cancel()
            
            if len(skip) == 2 and skip[1].isnumeric():
                for x in range(int(skip[1])-1):
                    player.queue.pop(0)
                pTask = asyncio.create_task(player.skip())
                return

            pTask = asyncio.create_task(player.skip())
            await messageHandler.updateEmbed()

        # elif userInput == 'lyrics':
        #     await ctx.send("currently unsupported")
        #     return
        #     song = player.currentSong["search"]
        #     if(GENIOUS_KEY != ''):
        #         try:
        #             genius = lg.Genius(GENIOUS_KEY)
        #             x = genius.search_songs(song)['hits'][0]['result']['url']
        #             lyrics = genius.lyrics(song_url=x)
        #             await ctx.send(f"```{lyrics}```")

        #         except Exception:
        #             await userMessage.reply('An error occurred')
        #             ex, val, tb = sys.exc_info()
        #             mPrint('ERROR', traceback.format_exc())
        #     else:
        #         mPrint('ERROR', 'ERROR KEY NOT FOUND FOR GENIOUS LYRICS')

        elif userInput == 'shuffle':
            player.shuffle()
            if textInput:
                await userMessage.add_reaction('🔀')
            await messageHandler.updateEmbed()

        elif userInput == 'pause':# and userMessage.author.id and userMessage.author.id in [348199387543109654, 974754149646344232]
            if player.isPaused == False:
                player.pause()
                await messageHandler.updateEmbed()

        elif userInput == 'resume': # and userMessage.author.id and userMessage.author.id in [348199387543109654, 974754149646344232]
            if player.isPaused:
                player.resume()
                await messageHandler.updateEmbed()

        elif userInput == 'stop':
            await player.stop()
            pTask.cancel()
            messageTask.cancel()
            return 0
        
        elif userInput == 'clear':
            player.clear()
            await messageHandler.updateEmbed()

        elif userInput.split()[0] == 'loop': # and userMessage.author.id and userMessage.author.id in [348199387543109654, 974754149646344232]
            request = userInput.split()
            if len(request) == 1:
                player.loop = True if player.loop == False else False
                player.loopQueue = False
                if textInput:
                    await userMessage.add_reaction('🔂')    

            elif request[1] == 'queue':
                player.loopQueue = True if player.loopQueue == False else False
                player.loop = False
                if textInput:
                    await userMessage.add_reaction('🔁')
                
            elif request[1] in ['song', 'track']:
                player.loop = True if player.loop == False else False
                player.loopQueue = False
                if textInput:
                    await userMessage.add_reaction('🔂')
            
            await messageHandler.updateEmbed()

        elif userInput == 'restart': # and userMessage.author.id and userMessage.author.id in [348199387543109654, 974754149646344232]
            player.restart()
            if textInput:
                await userMessage.add_reaction('⏪')    
            await messageHandler.updateEmbed()

        elif userInput == 'queue':
            messageHandler.embedMSG = await ctx.send(embed=messageHandler.getEmbed())
        
        elif userInput.split()[0] == 'precision' and userMessage.author.id in [348199387543109654, 974754149646344232]:
            if len(userInput.split()) == 2:
                messageHandler.timelinePrecision = int(userInput.split()[1])
            await messageHandler.updateEmbed()

        elif userInput.split()[0] == 'remove':
            request = userInput.split()
            if len(request) == 1:
                await ctx.send("Usage: remove [x]")
                return
            player.queue.pop(request[1]+1)
            await messageHandler.updateEmbed()
        
        elif userInput.split()[0] == 'mv':
            request = userInput.split()
            if len(request) != 3: await ctx.send("Usage: mv start end; eg. mv 3 1")
            if not request[1].isnumeric() or not request[2].isnumeric():
                await ctx.send("Usage: mv start end; eg. mv 3 1")
            try:
                temp = player.queue[int(request[2])-1]
                player.queue[int(request[1])-1] = player.queue[int(request[2])-1]
                player.queue[int(request[2])-1] = temp
            except IndexError:
                await ctx.send("Errore, la queue non ha così tante canzoni.")
            await messageHandler.updateEmbed()

        elif userInput.split()[0] in ['!play', '!p', 'play', 'p']:
            request = userInput.split()
            if len(request) == 1:
                userMessage.reply("Devi darmi un link bro")
            else:
                request = ' '.join(request[1:])
                mPrint('DEBUG', f'Queueedit: {request}')
                tracks = parseUrl(request)
                if tracks == None:
                    await userMessage.reply("An error occurred while looking for the songs")
                    return
                for t in tracks:
                    player.queue.append(t)
                await userMessage.add_reaction('🍑')
                await messageHandler.updateEmbed()
        
        elif userInput.split()[0] in ['!playnext', '!pnext', 'playnext', 'pnext']:
            request = userInput.split()
            if len(request) == 1:
                userMessage.reply("Devi darmi un link bro")
            else:
                request = ' '.join(request[1:])
                mPrint('DEBUG', f'QueueEdit: {request}')
                tracks = parseUrl(request)
                if tracks == None:
                    await userMessage.reply("An error occurred while looking for the songs")
                    return
                player.queue = tracks + player.queue
                await userMessage.add_reaction('🍑')
                await messageHandler.updateEmbed()

    async def userInput(pTask):
        while True:
            try:
                userMessage : discord.Message = await bot.wait_for('message', check=check)
                if player.endOfPlaylist:
                    return	
            except Exception:
                await voice.disconnect()
                voice.cleanup()
                mPrint('ERROR', f'USERINPUT WAITFOR EXCEPTION {traceback.format_exc()}')

            await actions(pTask, userMessage)

    async def emojiInput(pTask):
        while True:

            try:
                emoji, user = await bot.wait_for('reaction_add', check=checkEmoji)
                if player.endOfPlaylist:
                    return
                for e in emojis:
                    if str(emoji) == emojis[e]:
                        mPrint('USER', f"EmojiInput: {e}")
                        await actions(pTask, e, False)
                    if str(emoji) == '⏯':
                        if player.isPaused:
                           await actions(pTask, "resume", False)
                        else:
                            await actions(pTask, "pause", False)
                        break

                await embedMSG.remove_reaction(str(emoji), user)	

            except Exception:
                await voice.disconnect()
                voice.cleanup()
                mPrint('ERROR', f'EMOJIINPUT WAITFOR EXCEPTION {traceback.format_exc()}')

            
    await asyncio.sleep(0.1)
    asyncio.create_task(userInput(playerTask))

    for e in emojis:
        await embedMSG.add_reaction(emojis[e])

    asyncio.create_task(emojiInput(playerTask))

    

cmds = ['skip', 'shuffle', 'pause', 'resume', 'stop',
'clear', 'loop', 'restart', 'queue', 'remove', 'mv', 
'!playnext', '!pnext', 'playnext', 'pnext', 'play', 'p']

# vc.source = discord.PCMVolumeTransformer(vc.source, 1)

