import sys
import traceback
import asyncio
import json
import discord
from random import shuffle as queueshuffle

#import lyricsgenius as lg

sys.path.insert(0, 'music/')
import spotifyParser
import youtubeParser
import musicPlayer
from config import Colors as col

from mPrint import mPrint as mp
def mPrint(tag, text):
    mp(tag, 'musicBridge', text)

def parseUrl(url) -> list:
    """return a list of tracks found from an url, if the song is only 1, returns a list of one element"""
    if 'spotify.com' in url:
        try:
            tracks = spotifyParser.getSongs(url)
            if tracks == -1:
                mPrint('FATAL', "SPOTIFY AUTH FAILED, add your keys in the .env file if you want to enable spotify functionalities")
                return None
        except Exception:
            mPrint('ERROR', f"Spotify parser error:\nurl = {url}\n{traceback.format_exc()}")
            return None
    else:
        try:
            tracks = youtubeParser.getSongs(url)
        except Exception:
            mPrint('ERROR', f"Youtube parser error:\nurl = {url}\n{traceback.format_exc()}")
            return None

    return tracks

def evalUrl(url) -> bool:
    """Returns ture if the url is valid, else false"""
    resp = parseUrl(url)
    if resp == None: 
        return False
    return True

async def play(url : str, interaction : discord.Interaction, bot : discord.Client, shuffle : bool, precision : int, overwritten : tuple[str:str]):
    channel = interaction.channel
    #genius = lg.Genius('Client_Access_Token_Goes_Here', skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True)

    #Search tracks from url
    tracks : list[dict] = []

    if type(url) == list: #saved playlists are a list of links
        for t in url:
            songs = parseUrl(t)
            for s in songs:
                tracks.append(s)

    else: #user asked for a specific song/link
        tracks = parseUrl(url)
    
    #check if tracks
    if tracks == None:
        await interaction.followup.send(f"An error occurred while looking for song(s) please retry.", ephemeral=True)
        mPrint("WARN", f"play function did not find the track requested {url}")
        return
    
    queue : dict[int:dict] = {} #{"0": track}
    for i, t in enumerate(tracks):
        queue[int(i)] = t


    queuePlaceholder = ''
    for i in range(6):
        queuePlaceholder += f"**{i}**- `                                      `\n"
     
    if precision != 0:
        desc = f'Now Playing: `                                      `\n▂▂▂▂▂▂▂▂▂▂ (00:00 - 00:00)\n'
    else:
        desc = f'Now Playing: `                                      `\n'
        
    embed = discord.Embed(
        title=f'Loading...',
        description=desc,
        color=col.red
    )

    embed.add_field(name='Author:', value=f'`               `', inline=True)
    embed.add_field(name='Last 5 in queue', value=f'{queuePlaceholder}', inline=False)
    embed.set_footer(text='🍑 the best bot 🎶 https://notlatif.github.io/CuloBot/#MusicBot')
     
    try: #try connecting to vc
        vchannel = bot.get_channel(interaction.user.voice.channel.id)
    except AttributeError:
        await interaction.followup.send('Devi essere in un culo vocale per usare questo comando.', ephemeral=True)
        return
    except discord.ClientException:
        await interaction.followup.send('Sono già in un altro canale vocale.', ephemeral=True)
        return
    else:
        voice : discord.VoiceClient = await vchannel.connect()

    emojis = {
        "stop": "⏹",
        "previous": "⏮",
        "play_pause": "⏯",
        "skip": "⏭",
        "shuffle": "🔀",
        "loop": "🔂",
        "loop queue": "🔁",
        #"report": "⁉", #temporarely disabled
    }

    await interaction.followup.send("Queue avviata", ephemeral=False)
    embedMSG = await channel.send(embed=embed)

    player = musicPlayer.Player(voice, queue, overwritten, shuffle)
    messageHandler = musicPlayer.MessageHandler(player, embedMSG, vchannel, precision)
    
    try:
        playerTask = asyncio.create_task(player.starter())
        messageTask = asyncio.create_task(messageHandler.start())

    except:
        await voice.disconnect()
        voice.cleanup()
        mPrint('FATAL', f'Error while creating tasks for player and message\n{traceback.format_exc()}')
        return

    def check(m : discord.Message):	#check if message was sent in the same channel as the play embed
        return m.author != bot.user and m.channel.id == channel.id

    def checkEmoji(reaction : discord.Reaction, user): #check if reaction was added to the right message
        return user != bot.user and reaction.message.id == messageHandler.embedMSG.id

    async def actions(pTask : asyncio.Task, userMessage : discord.Message, textInput = True):
        if textInput:
            userInput = userMessage.content.replace('!', '')
        else:
            userInput = userMessage

        mPrint('DEBUG', f'User input: {userInput}; isText: {textInput} <if false, it was an impot from emoji')

        if len(userInput.split()) == 0: return

        if userInput.split()[0] == 'report':
            if not player.wasReported:
                track = player.currentSong
                player.wasReported = True
                await channel.send('**Se la canzone è ancora in riproduzione**, puoi sistemarla tu usando `!suggest <youtube url>`')
                mPrint('SONGERROR', f'User reported song link discrepancy:\nSOURCE URL: {track["base_link"]}\nQUERY: {track["search"]}\nRESULT: {player.videoUrl}')
                await messageHandler.updateEmbed()

        elif userInput.split()[0] == 'suggest':
            await channel.typing()
            mPrint('INFO', userInput.split())
            if len(userInput.split()) == 2:
                suggestion = [player.currentSong['search'], userInput.split()[1]]
                with open('botFiles/guildsData.json', 'r') as f:
                    data = json.load(f)[interaction.guild.id]['youtube_search_overwrite']
                
                data[suggestion[0]] = suggestion[1]
                with open(f'botFiles/suggestions/{str(interaction.guild.id)}.json', 'w') as f:
                    json.dump(data, f, indent=2)

            else:
                await channel.send('Usage: !suggest <youtube url>')

        elif userInput.split()[0] == 'previous':
            mPrint('USER', 'previous song')
            mPrint('TEST', f'previous song {player.previousSongId}')
            
            player.queueOrder.insert(0, player.previousSongId)

            pTask = asyncio.create_task(player.skip())
            await messageHandler.updateEmbed()

        elif userInput.split()[0] == 'skip':
            mPrint('USER', 'skipped song')
            skip = userInput.split()
            pTask.cancel()
            if pTask.cancelled() == False: 
                mPrint("WARN", "task was not closed.")
                pTask.cancel()

            player.loop = False

            if len(skip) == 2 and skip[1].isnumeric():
                for x in range(int(skip[1])-1):
                    if player.loopQueue:
                        mPrint("TEST", f'multipleskipping: appending {player.queueOrder[0]} to end (loopQueue)')
                        player.queueOrder.append(player.queueOrder[0])
                        del player.queueOrder[0]
                    else:
                        mPrint("TEST", f'multipleskipping: removing {player.queueOrder[0]}')
                        del player.queueOrder[0]
                pTask = asyncio.create_task(player.skip())
                return

            pTask = asyncio.create_task(player.skip())
            await messageHandler.updateEmbed()

        # elif userInput == 'lyrics':
        #     await channel.send("currently unsupported")
        #     return
        #     song = player.currentSong["search"]
        #     if(GENIOUS_KEY != ''):
        #         try:
        #             genius = lg.Genius(GENIOUS_KEY)
        #             x = genius.search_songs(song)['hits'][0]['result']['url']
        #             lyrics = genius.lyrics(song_url=x)
        #             await channel.send(f"```{lyrics}```")

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

        elif userInput == 'pause':
            if player.isPaused == False:
                player.pause()
                await messageHandler.updateEmbed()

        elif userInput == 'resume':
            if player.isPaused:
                player.resume()
                await messageHandler.updateEmbed()

        elif userInput == 'stop':
            await messageHandler.updateEmbed(True)
            await player.stop()
            pTask.cancel()
            messageTask.cancel()
            return 0

        elif userInput == 'clear':
            player.clear()
            await messageHandler.updateEmbed()

        elif userInput.split()[0] == 'loop':
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

        elif userInput == 'restart':
            player.restart()
            if textInput:
                await userMessage.add_reaction('⏪')    
            await messageHandler.updateEmbed()

        elif userInput == 'queue':
            await messageHandler.embedMSG.clear_reactions()
            await messageHandler.embedMSG.edit(embed=messageHandler.getEmbed(move=True))
            messageHandler.ready = False
            messageHandler.embedMSG = await channel.send(embed=messageHandler.getEmbed())
            
            for e in emojis: 
                await messageHandler.embedMSG.add_reaction(emojis[e])

            messageHandler.ready = True
            await messageHandler.updateEmbed()
        
        elif userInput.split()[0] == 'precision' and userMessage.author.id in [348199387543109654, 974754149646344232]:
            if len(userInput.split()) == 2:
                messageHandler.timelinePrecision = int(userInput.split()[1])
            await messageHandler.updateEmbed()

        elif userInput.split()[0] == 'remove':
            request = userInput.split()
            if len(request) == 1:
                await channel.send("Usage: remove [x]")
                return
            player.queueOrder.pop(int(request[1])-1)
            await messageHandler.updateEmbed()
        
        elif userInput.split()[0] == 'mv':
            request = userInput.split()
            if len(request) != 3: await channel.send("Usage: mv start end; eg. mv 3 1")
            if not request[1].isnumeric() or not request[2].isnumeric():
                await channel.send("Usage: mv start end; eg. mv 3 1")
            try:
                temp = player.queueOrder[int(request[1])-1]
                player.queueOrder[int(request[1])-1] = player.queueOrder[int(request[2])-1]
                player.queueOrder[int(request[2])-1] = temp
            except IndexError:
                await channel.send("Errore, la queue non ha così tante canzoni.")
            await messageHandler.updateEmbed()

        elif userInput.split()[0] in ['play', 'p']:
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
                
                if player.isShuffled:
                    queueshuffle(tracks)

                startindex = len(player.queueOrder)
                for i, t in enumerate(tracks):
                    player.queue[i+startindex] = t
                    player.queueOrder.append(i+startindex)

                await userMessage.add_reaction('🍑')
                await messageHandler.updateEmbed()
        
        elif userInput.split()[0] in ['playnext', 'pnext']:
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
                
                if player.isShuffled:
                    queueshuffle(tracks)

                startindex = len(player.queueOrder)
                for i, t in enumerate(tracks):
                    player.queue[i+startindex] = t
                    player.queueOrder.insert(0, i+startindex)
                    mPrint('TEST', f'inserting {i+startindex} @ 0 : {player.queueOrder[:3]}')
                    
                await userMessage.add_reaction('🍑')
                await messageHandler.updateEmbed(pnext=True)

    async def userInput(pTask):
        while True:
            try:
                userMessage : discord.Message = await bot.wait_for('message', check=check)
                if player.endOfPlaylist:
                    return	
            except Exception:
                await voice.disconnect()
                voice.cleanup()
                mPrint('FATAL', f'USERINPUT WAITFOR EXCEPTION {traceback.format_exc()}')

            await actions(pTask, userMessage)

    async def emojiInput(pTask):
        while True:
            try:
                emoji, user = await bot.wait_for('reaction_add', check=checkEmoji)
                if player.endOfPlaylist:
                    return
                await messageHandler.embedMSG.remove_reaction(str(emoji), user)	
                if user not in voice.channel.members:
                    continue
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
                

            except Exception:
                await voice.disconnect()
                voice.cleanup()
                mPrint('FATAL', f'EMOJIINPUT WAITFOR EXCEPTION {traceback.format_exc()}')

            
    await asyncio.sleep(0.1)
    asyncio.create_task(userInput(playerTask))

    for e in emojis:
        await messageHandler.embedMSG.add_reaction(emojis[e])
    messageHandler.ready = True
    await messageHandler.updateEmbed()

    asyncio.create_task(emojiInput(playerTask))

cmds = ['!skip', '!shuffle', '!pause', '!resume','!stop', '!clear',
 '!loop', '!restart', '!queue', '!remove', '!mv', '!playnext', '!pnext', '!play', '!p']


old_cmds = ['skip', '!skip', 'shuffle', '!shuffle', 'pause', '!pause',
'resume', '!resume', 'stop', '!stop', 'clear', '!clear',
'loop', '!loop', 'restart', '!restart', 'queue', '!queue',
'remove', '!remove', 'mv', '!mv',
'!playnext', '!pnext', 'playnext', 'pnext', 'play', 'p']