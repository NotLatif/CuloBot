import traceback
import asyncio
import json
from typing import Any, Optional, Union
import discord
import discord.ui
from discord import app_commands
from random import shuffle as queueshuffle

import spotifyParser
import youtubeParser
import musicPlayer
import musicObjects
from config import Colors as col

from mPrint import mPrint as mp
def mPrint(tag, text):
    mp(tag, 'musicBridge', text)

def getTracksURL(userQuery:str, overwritten, playlists : dict[str, list[str]]) -> Union[list[str], None]:
    """Parses user input and retuns a list of URLs"""
    #user searched a link
    if ',' in userQuery: #multiple search items
        links = userQuery.replace(" ", "").split(',') # NOTE: this also removes spaces between words eg."myplaylist"
    else: #one search item
        links = [userQuery]

    toReturn = []
    for search in links:
        mPrint('DEBUG', f"{search=}")
        if "spotify.com" in search or "youtube.com" in search or "youtu.be" in search:
            mPrint('INFO', f'FOUND SUPPORTED URL: {search}')
            toReturn.append(search)
        
        #user wants a saved playlist (playlists can have multiple tracks)
        elif search in [key.replace(" ", "") for key in playlists]:
            for k in playlists:
                if k.replace(" ", "") == userQuery:
                    key = k
                    break
            mPrint('INFO', f'FOUND SAVED PLAYLIST: {playlists[key]}')
            for track in playlists[key]:
                toReturn.append(track)
        
        #user submitted a youtube query
        else:
            mPrint('MUSIC', f'Searching for user requested song: ({search})')
            trackURL = youtubeParser.searchYTurl(search, overwritten)
            if trackURL == None:
                return 404
            mPrint('INFO', f'SEARCHED SONG URL: {trackURL}')
            toReturn.append(trackURL)

    return toReturn

def getTracksFromURL(url, overwritten) -> Union[list[musicObjects.Track], None]:
    """return a list of track objects found from an url, if the song is only 1, returns a list of one element"""
    #TODO check if url is a playlist
    if 'spotify.com' in url:
        try:
            tracks = spotifyParser.getTracks(url, overwritten)
            if tracks == -1:
                mPrint('ERROR', "SPOTIFY AUTH FAILED, add your keys in the .env file if you want to enable spotify functionalities")
                return None
            elif tracks == -2:
                mPrint('ERROR', "The spotify link could not be parsed correctly")
                return None

        except Exception:
            mPrint('ERROR', f"Spotify parser error:\nurl = {url}\n{traceback.format_exc()}")
            return None
    else:
        try:
            tracks = youtubeParser.getTracks(url)
            if tracks == None:
                mPrint('ERROR', f'Youtube parser error for: {url}')
                return None
        except Exception:
            mPrint('ERROR', f"Youtube parser error:\nurl = {url}\n{traceback.format_exc()}")
            return None

    return tracks

def evalUrl(url, ow) -> bool:
    """Returns ture if the url is valid, else false"""
    resp = getTracksFromURL(url, ow)
    if resp == None: 
        return False
    return True

async def play(
        urlList : list[str], 
        interaction : discord.Interaction, 
        bot : discord.Client,
        tree : app_commands.CommandTree, 
        shuffle : bool, 
        precision : int, 
        guildOverwritten : tuple[str,str],
        guildPlaylists : dict[str, list[str]],
        enableDataBase : bool
    ):
    embedChannel = interaction.channel

    # initialize queue
    queue = musicObjects.Queue()
    queue.isShuffle = shuffle

    if type(urlList) == list:
        for url in urlList:
            #foreach urls find the songs it links to
            tracks = getTracksFromURL(url, guildOverwritten)
            if tracks == None:
                #console logs were processed earlier, no need to print more
                #alert user
                await interaction.followup.send("There was an error processing the url")
                return -1
            for t in tracks:
                queue.addTrack(t)

        if shuffle:
            queue.shuffleQueue()

    else:
        #This should never get triggered
        await interaction.followup.send("Unsupported `track`")
        mPrint("ERROR", f"Expected track of type list but got {type(urlList)} instead")
        return -1

    #check that queue is not empty; this is probably redundant
    if len(queue.queue) == 0:
        await interaction.followup.send(f"An error occurred while looking for song(s) please retry.", ephemeral=True)
        mPrint("WARN", f"play function did not find the track requested {url}")
        return

    mPrint('INFO',f"There are {len(queue)} songs in queue:")

    #make graphical interface for loading
    if precision != 0:
        desc = f'Now Playing: `                                      `\n▂▂▂▂▂▂▂▂▂▂ (00:00 - 00:00)\n'
    else:
        desc = f'Now Playing: `                                      `\n'
        
    embed = discord.Embed(
        title=f'Loading...',
        description=desc,
        color=col.red
    )

    queuePlaceholder = ''
    for i in range(6):
        queuePlaceholder += f"**{i}**- `                                      `\n"

    embed.add_field(name='Author:', value=f'`               `', inline=True)
    embed.add_field(name='Last 5 in queue', value=f'{queuePlaceholder}', inline=False)
    embed.set_footer(text='🍑 the best bot 🎶 https://notlatif.github.io/CuloBot/#MusicBot')
     
    try: #try connecting to vc
        vchannel = bot.get_channel(interaction.user.voice.channel.id)
        voiceClient : discord.VoiceClient = await vchannel.connect()
    except AttributeError:
        await interaction.followup.send('Devi essere in un canale vocale per usare questo comando.', ephemeral=True)
        return
    except discord.ClientException:
        await interaction.followup.send('Sono già in un altro canale vocale.', ephemeral=True)
        return
    
    #Define commands enum
    class Commands: # ALL IDs MUST BE UNIQUE
        previous = 0,
        play_pause = 1,
        skip = 2,
        stop = 3,
        shuffle = 4,
        loop_one = 5,
        loop_queue = 6,
        report = 7,
        clear_queue = 8,
        resend_queue = 9,
        #remove = 10,   #Currently not supported
        move = 11,
        add_song = 12,
        loop = 13
        pause = 14
        resume = 15

    #Define buttons
    buttonsCommands: dict[int, tuple[str, int, discord.ButtonStyle | None]] = {
        #cmd  : [emoji, row, optional(style)]
        Commands.previous:   ("⏮", 1),
        Commands.play_pause: ("⏯", 1),
        Commands.skip:       ("⏭", 1),
        Commands.stop:       ("⏹", 1, discord.ButtonStyle.red),
        Commands.shuffle:    ("🔀", 2),
        Commands.loop_one:   ("🔂", 2),
        Commands.loop_queue: ("🔁", 2),
        Commands.report:     ("⁉", 2),
    }

    # Make Button constructor
    class EmbedButtons(discord.ui.Button):
        def __init__(self, *, style: discord.ButtonStyle = discord.ButtonStyle.secondary, label: Optional[str] = None, disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None, emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None, row: Optional[int] = None, command:str):
            if len(label) > 80:
                label = label[:80]
            super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
            self.command = command
        
        async def callback(self, interaction: discord.Interaction) -> Any:
            #This will be called at button press
            try:
                #Check that user and bot are in the same vc
                if interaction.user.voice.channel.id == voiceClient.channel.id:
                    if self.command == Commands.report:
                        await actions(self.command, interaction)
                    else:
                        await interaction.response.defer()
                        await actions(self.command)

                    await interaction.edit_original_message(content="")
            except AttributeError:
                #user was not in a voice channel
                pass
            
    # Create discord view
    view = discord.ui.View(timeout=None)

    # Add buttons to view
    # buttons : list[discord.ui.Button] = []
    for b in buttonsCommands:
        try:
            style = buttonsCommands[b][2]
        except IndexError:
            style = discord.ButtonStyle.secondary

        btn = EmbedButtons(label="", style=style, emoji=buttonsCommands[b][0], row=buttonsCommands[b][1], custom_id=f"{interaction.id}:playerbuttons:{b}", command=b)
        # buttons.append(btn)
        view.add_item(btn)

    #send embed with view
    await interaction.followup.send("Queue avviata", ephemeral=False)
    embedMSG = await embedChannel.send(embed=embed, view=view)

    # Create Player and Embed handlers
    player = musicPlayer.Player(voiceClient, queue)
    messageHandler = musicPlayer.MessageHandler(player, embedMSG, queue, precision, view)
    
    try:
        messageTask = asyncio.create_task(messageHandler.start())
    except:
        await voiceClient.disconnect()
        voiceClient.cleanup()
        mPrint('FATAL', f'Error while creating tasks for player and message\n{traceback.format_exc()}')
        return

    # Define actions
    async def actions(action:Commands, arg1 = None, arg2 = None, arg3 = None):
        mPrint('DEBUG', f"Requested action: {action=} {arg1=} {arg2=}")
        if action == Commands.previous:
            mPrint('USER', 'Skipping to previous song')
            player.previous()

        elif action == Commands.skip:
            times = arg1 if arg1 != None else 1
            mPrint('USER', f'Skipping {times} song(s)')
            
            if player.queue.isLooped() == 1:
                # if looping one, remove loop
                player.queue.setLoop(0)

            player.skip(times)

        elif action == Commands.shuffle:
            player.shuffle()
            await messageHandler.updateEmbed()

        elif action == Commands.play_pause:
            player.play_pause()
            await messageHandler.updateEmbed()

        elif action == Commands.pause:
            player.pause()
            await messageHandler.updateEmbed()

        elif action == Commands.resume:
            player.resume()
            await messageHandler.updateEmbed()

        elif action == Commands.stop:
            await messageHandler.updateEmbed(True)
            player.stop()
            messageTask.cancel()
            await voiceClient.disconnect()
            return 0

        elif action == Commands.clear_queue:
            player.clear()
            await messageHandler.updateEmbed()

        elif action == Commands.loop_one:
            if player.queue.isLooped() == 1:
                player.queue.setLoop(0)
            else:
                player.queue.setLoop(1)
            await messageHandler.updateEmbed()

        elif action == Commands.loop_queue:
            if player.queue.isLooped() == 2:
                player.queue.setLoop(0)
            else:
                player.queue.setLoop(2)
            await messageHandler.updateEmbed()

        elif action == Commands.loop:
            if arg1 == None:
                if player.queue.isLooped() == 0: # NO
                    arg1 = 2
                elif player.queue.isLooped() == 1: # ONE
                    arg1 = 0
                else: # YES
                    arg1 = 0

            player.queue.setLoop(int(arg1))
            await messageHandler.updateEmbed()

        elif action == Commands.resend_queue:
            await messageHandler.embedMSG.clear_reactions()
            await messageHandler.embedMSG.edit(embed=messageHandler.getEmbed(move=True))
            messageHandler.ready = False
            messageHandler.embedMSG = await embedChannel.send(embed=messageHandler.getEmbed())

            messageHandler.ready = True
            await messageHandler.updateEmbed()
        
        elif action == Commands.move:
            player.queue.move(int(arg1), int(arg2))
            await messageHandler.updateEmbed()

        elif action == Commands.add_song:
            url = arg1
            index = 0 if arg2 == None else arg2
            shuffle = arg3

            tracks : list[musicObjects.Track] = []
            for url in getTracksURL(url, guildOverwritten, guildPlaylists):
                t = getTracksFromURL(url, guildOverwritten)
                if t != None:
                    for track in t:
                        tracks.append(track)

            # Search did not find any track
            if tracks == []: return None

            #if shuffle is not passed and playershuffle is enabled: shuffle
            #elif player requested shuffle: shuffle; else: don't shuffle (implied)
            if shuffle == None and queue.isShuffle: queueshuffle(tracks)
            elif shuffle: queueshuffle(tracks)

            for t in tracks:
                mPrint('TEST', f'Adding track: {t.title}@{index}')
                player.queue.addTrack(t, index)
                index += 1
            
            await messageHandler.updateEmbed(pnext=index)
            return tracks
        
        elif action == Commands.report:
            interaction :discord.Interaction = arg1
            reportedTrack = player.currentTrack
            class Feedback(discord.ui.Modal, title='Grazie per la segnalazione!'):
                input = discord.ui.TextInput(label="Se vuoi puoi dare un link come suggerimento", style=discord.TextStyle.short, required=False, placeholder='https://www.youtube.com/')
                
                async def on_submit(self, interaction: discord.Interaction):
                    message = f"({interaction.id}) (guild:{interaction.guild.id})\nUser reported song discrepancy\nurl:{player.currentTrack.getVideoUrl()}\nSuggestion: {str(self.input.value)}\n"
                    if self.input.value != None:
                        suggestion = self.input.value

                        with open('botFiles/guildsData.json', 'r') as f:
                            overwriteData = json.load(f)[str(interaction.guild.id)]['musicbot']['youtube_search_overwrite']
                        
                        overwriteData[player.currentTrack.getQuery()] = suggestion
                        with open(f'music/suggestions/{str(interaction.guild.id)}.json', 'w') as f:
                            json.dump(overwriteData, f, indent=2)
                        
                        if getTracksURL(self.input.value, guildOverwritten, guildPlaylists) != None:
                            await actions(Commands.add_song, self.input.value, 0)
                            if reportedTrack == player.currentTrack:
                                await actions(Commands.skip)

                    ## add spotify url to data in the message
                    try:
                        await bot.dev.send(message)
                    except Exception:
                        mPrint('ERROR', traceback.format_exc())

                    mPrint('INFO', f"User reported discrepancy for song {player.currentTrack.getQuery()}")
                    await interaction.response.send_message("Thanks for your suggestion!", ephemeral=True)

            await interaction.response.send_modal(Feedback())

    # SLASH COMMANDS
    def checkAuthor(interaction:discord.Interaction):
        #Check that the user sent the message in the right channel and is connected in the right vc
        try:
            return interaction.channel.id == embedChannel.id and interaction.user.voice.channel.id == voiceClient.channel.id
        except AttributeError:
            return False
        
    @tree.command(name="prev", description="Vai alla traccia precedente", guild=interaction.guild)
    async def prev(interaction : discord.Interaction):
        if checkAuthor(interaction):
            await interaction.response.defer(ephemeral=True)
            await actions(Commands.previous)
            await interaction.followup.send("Done")

    @tree.command(name="skip", description="Vai alla traccia successiva", guild=interaction.guild)
    async def skip(interaction : discord.Interaction, times:int=1):
        """
        :param times: quante volte skippare
        """
        if checkAuthor(interaction):
            await interaction.response.defer(ephemeral=True)
            await actions(Commands.skip, times)
            await interaction.followup.send(f"Skipped {times} tracks", ephemeral=True)

    @tree.command(name="shuffle", description="Attiva/Disattiva lo shuffle", guild=interaction.guild)
    async def queue_shuffle(interaction : discord.Interaction):
        if checkAuthor(interaction):
            await interaction.response.defer(ephemeral=True)
            await actions(Commands.shuffle)
            await interaction.followup.send("Done")

    @tree.command(name="play_pause", guild=interaction.guild)
    async def play_pause(interaction : discord.Interaction):
        if checkAuthor(interaction):
            await interaction.response.defer(ephemeral=True)
            await actions(Commands.play_pause)
            await interaction.followup.send("Paused" if player.isPaused else "Resumed", ephemeral=True)   

    @tree.command(name="pause", guild=interaction.guild)
    async def pause(interaction : discord.Interaction):
        if checkAuthor(interaction):
            await interaction.response.defer(ephemeral=True)
            await actions(Commands.pause)
            await interaction.followup.send("Paused", ephemeral=True)  

    @tree.command(name="resume", guild=interaction.guild)
    async def resume(interaction : discord.Interaction):
        if checkAuthor(interaction):
            await interaction.response.defer(ephemeral=True)
            await actions(Commands.resume)
            await interaction.followup.send("Resumed", ephemeral=True)  

    @tree.command(name="stop", description="Cancella la playlist e ferma la riproduzione", guild=interaction.guild)
    async def stop(interaction : discord.Interaction):
        if checkAuthor(interaction):
            await interaction.response.defer(ephemeral=True)
            await actions(Commands.stop)
            await interaction.followup.send("Stopped queue.", ephemeral=True)

    @tree.command(name="clear_queue", description="Cancella la playlist", guild=interaction.guild)
    async def clear(interaction : discord.Interaction):
        if checkAuthor(interaction):
            await interaction.response.defer(ephemeral=True)
            await actions(Commands.clear_queue)
            await interaction.followup.send("Cleared Queue.", ephemeral=True)

    @tree.command(name="loop", guild=interaction.guild)
    @app_commands.choices(mode=[
        app_commands.Choice(name="No", value="0"),
        app_commands.Choice(name="One song", value="1"),
        app_commands.Choice(name="Playlist", value="2"),])
    async def loop(interaction : discord.Interaction, mode:str):
        if checkAuthor(interaction):
            await interaction.response.defer(ephemeral=True)
            await actions(Commands.loop, int(mode))
            await interaction.followup.send(f"Ok")

    @tree.command(name="move", description="Scambia due tracce", guild=interaction.guild)
    async def clear(interaction : discord.Interaction, traccia1:int, traccia2:int):
        if checkAuthor(interaction):
            await interaction.response.defer(ephemeral=True)
            await actions(Commands.move, traccia1, traccia2)
            await interaction.followup.send(f"Ho scambiato {traccia1} con {traccia2}", ephemeral=True)

    @tree.command(name="add_song", description="Aggiungi canzone in queue", guild=interaction.guild)
    async def add_song(interaction : discord.Interaction, url:str, position:str = '0', shuffle:bool = None):
        """
        :param position: Usa 'END' per aggiungere una traccia alla fine (default: 0)
        """
        if 'end' in position.lower():
            position = len(player.queue)
        
        if type(position) == str and not position.isnumeric():
            mPrint('WARN', f'User used unsupported value for addsong {position} defaulting to 0')
            position = 0

        if checkAuthor(interaction):
            await interaction.response.defer(ephemeral=True)
            resp = await actions(Commands.add_song, url, int(position), shuffle)

            if resp == None:
                await interaction.followup.send(f"C'è stato un errore durante la ricerca della traccia {url}", ephemeral=True)
                return
            else:
                if len(resp) == 1:
                    try: message = f"Ho aggiunto {resp[0]} in queue"
                    except AttributeError: message = 'Fatto'
                else:
                    message = f"Fatto"
                await interaction.followup.send(message, ephemeral=True)
            
    @tree.command(name="report", description="Avvisa che la canzone trovata su youtube è sbagliata.", guild=interaction.guild)
    async def report(interaction : discord.Interaction):
        if checkAuthor(interaction):
            await actions(Commands.report, interaction)

    mPrint('INFO', 'syncing commands')
    asyncio.create_task(tree.sync(guild=interaction.guild))

    # @bot.event
    # async def on_interaction(interaction : discord.Interaction):
    #     mPrint('TEST', f"{interaction.id=}")


    val = player.playQueue()
    mPrint('TEST', f"player.playQueue() returned with code {val}")
    messageHandler.ready = True

    #while player.isplaying: continue
    # TODO

    #at this point the player finished playing
    #await voiceClient.disconnect()
