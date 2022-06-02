#speed pitch effects(filters nightcore, filters bassboost, filters list, filters reset)

#TODO add lyrics #https://docs.genius.com #musixmatch
#remove from queue < TEST
#loop queue: quando una canzone finisce viene aggiunta in coda < TEST
#restart: ripete la traccia < TEST
#mv x y: sposta la canzone x -> y < TEST
#autoplay
"""
"custom_playlist":{
      "Pippo": [
        "canzone 2",
        "canzone 1"
      ]
"""

import sys
import traceback
import discord
import asyncio
import time
from discord.ext import commands
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
from random import shuffle
from mPrint import mPrint as mp
import config


YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': '%(title)s.%(etx)s',
    'quiet': False
}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def mPrint(tag, text):
    mp(tag, 'musicPlayer', text)

def searchYTurl(query) -> str: #gets the url of the first song in queue (the one to play)
    mPrint('MUSIC', f'Searching for user requested song: ({query})')
    return VideosSearch(query, limit = 1).result()['result'][0]['link']

def conversion(sec):
    sec = int(sec)
    sec_value = sec % (24 * 3600)
    hour_value = sec_value // 3600
    sec_value %= 3600
    min = sec_value // 60
    sec_value %= 60
    h = f'{int(hour_value):02}:' if int(hour_value) != 0 else ''
    return f'{h}{int(min):02}:{int(sec_value):02}'

class Player():
    def __init__(self, vc : discord.VoiceClient, queue : dict[int:dict]) -> None:
        self.queue : dict[int:dict] = queue
        self.queueOrder = [x for x in range(len(queue))] #TEST 1 song in playlist

        self.isShuffled = config.player_shuffle
        if self.isShuffled: shuffle(self.queueOrder)

        self.voiceClient = vc
        self.isConnected = True

        self.loop = False
        self.loopQueue = False
        self.currentSong = None
        self.previousSongId = None
        self.duration = 0
        self.stepProgress = 0 #keep track of seconds passed in 10 chuncks

        self.stopped = False

        #flags needed to communicate with EmbedHandler
        self.skipped = False
        self.isPaused = False
        self.songStartTime = 0
        self.songStarted = False
        self.pauseStart = 0
        self.pauseEnd = 0
        self.endOfPlaylist = False

    def getVideoURL(self): #gets the url of the first song in queue (the one to play)
        mPrint('DEBUG', f'searching for url (QUERY: {self.currentSong["search"]})')
        track = self.currentSong['search']
        url = VideosSearch(track, limit = 1).result()['result'][0]['link']
        mPrint('DEBUG', f'FOUND URL: {url}')
        return url
    
    #wrapper that handles embed and song
    async def starter(self):
        self.playNext(None)
        

    def playNext(self, error):
        if self.stopped:
            mPrint('INFO', 'Player was stoppend. Returning.')
            return
        mPrint('INFO', "---------------- PLAYNEXT ----------------")
        if error != None: mPrint('ERROR', f"{error}")
        
        if len(self.queueOrder) != 0:
            if self.currentSong == None: # first song
                self.currentSong = self.queue[self.queueOrder[0]]
                self.previousSongId = self.queueOrder[0]

                if self.loopQueue:
                    mPrint('INFO', "looping queue, append song to end")
                    self.queueOrder.append(self.queueOrder[0])

                #mPrint('TEST', f'deleting {self.queueOrder[0]}, prev: {self.previousSongId}')
                # del self.queueOrder[0]

            else: #not first song
                #get last song
                self.previousSongId = self.queueOrder[0]

                #remove from order (or append to end if looping)
                if self.loopQueue:
                    mPrint('INFO', "looping queue, append song to end")
                    self.queueOrder.append(self.queueOrder[0])
                
                self.currentSong = self.queue[self.queueOrder[0]]
            del self.queueOrder[0]
                #mPrint('TEST', f'deleting {self.queueOrder[0]}, prev: {self.previousSongId}')  
        
        else:
            if self.loop == False: 
                self.endOfPlaylist = True
                mPrint('MUSIC', 'End of playlist.')
                return
        # mPrint('TEST', self.queueOrder)
        self.playSong()
        

    def playSong(self):
        try:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(self.getVideoURL(), download=False)
                URL = info['formats'][0]['url']

                if self.voiceClient.is_playing(): 
                    mPrint('WARN', 'musicbot was already playing, stopping song.')
                    self.voiceClient.stop()

                mPrint('MUSIC', f'Now Playing: ({self.currentSong["trackName"]}) ')
                self.songStartTime = time.time()
                self.songStarted = True
                source = discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)
                self.voiceClient.play(source, after= self.playNext)
               
        except discord.ClientException:
            #bot got disconnected
            mPrint('FATAL', 'Bot is not connected to vc')
            self.voiceClient.cleanup()
            self.isConnected = False
            return
    
    async def skip(self):
        if len(self.queueOrder) > 0:
            mPrint('MUSIC', f'skipped track ({self.currentSong["trackName"]})')
            mPrint('MUSIC', f'next is {self.currentSong["trackName"] if self.loop else self.queue[self.queueOrder[0]]["trackName"]}')
            self.voiceClient.stop()
            self.skipped = True
            # no need to call playNext since lambda will do it for us
        else:
            await self.stop()

    def restart(self):
        self.queueOrder.insert(0, self.previousSongId)
        mPrint('MUSIC', f'restarted track ({self.currentSong["trackName"]})')
        self.voiceClient.stop()

    def shuffle(self): #TODO make this a toggle
        if self.isShuffled:
            self.isShuffled = False
            self.queueOrder = [x for x in range(len(self.queue))]
        else:
            self.isShuffled = True
            shuffle(self.queueOrder)

    def pause(self):
        self.voiceClient.pause()
        self.isPaused = True
        self.pauseStart = time.time()

    def resume(self):
        self.voiceClient.resume()
        self.isPaused = False
        self.pauseEnd = time.time()

    def clear(self): #kind of does not make sense this just seems like stop() but spicy
        self.queueOrder = []
        self.queue = {}

    async def stop(self):
        self.clear()
        await self.voiceClient.disconnect()
        self.voiceClient.cleanup()

class MessageHandler():
    #Handles the embed of the player in parallel with the player
    def __init__(self, player : Player, embedMSG : discord.Message, vchannel : discord.VoiceChannel) -> None:
        self.player = player
        self.embedMSG = embedMSG

        precision = config.timeline_precision
        precision = 16 if precision > 16 else 1 if precision < 1 else precision
        self.timelinePrecision = precision
        self.timelineChars = ('▂', '▅')
        self.timeBar = []
        self.timeStart = 0
        self.timeDone = 0

        self.stepProgress = 0
        self.duration = 0
        self.pauseDiff = 0

        self.vchannel = vchannel
        self.isAloneInVC = False
        self.aloneTimeStart = 0
        self.maxAloneTime = config.max_alone_time if config.max_alone_time <= 300 else 300

    async def start(self):
        await self.embedLoop()
        mPrint('DEBUG', 'Embed handler finished')

    async def embedLoop(self):
        while True: #foreach song
            self.timeDone = time.time()
            if self.player.endOfPlaylist:
                mPrint("DEBUG","EOPlaylist, stopping embedloop")
                await self.updateEmbed(True)
                await self.player.stop()
                return

            if not self.player.songStarted:
                # mPrint("TEST", f"Song has not started yet, waiting... (duration: {self.player.currentSong['duration_sec']}, done after {self.timeDone - self.timeStart})")
                await asyncio.sleep(0.3)
                if not self.player.voiceClient.is_connected():
                    mPrint("WARN", "Bot was disconnected from vc, stopping embedloop")
                    return
                continue #don't do anything if player did not change song

            self.player.songStarted = False

            currentSong = self.player.currentSong

            self.timeBar = [self.timelineChars[0] for x in range(self.timelinePrecision)]
            
            mPrint('MUSIC', f'Song name: {currentSong["trackName"]}')
            mPrint('MUSIC', f'Song duration: {currentSong["duration_sec"]}')

            stepSeconds = float(currentSong["duration_sec"]) / self.timelinePrecision
            self.duration = currentSong["duration_sec"]
            self.stepProgress = 0

            await self.updateEmbed()

            initialTime = self.player.songStartTime
            #update timestamp every "step" seconds
            currentStep = 1
            mPrint('DEBUG', f"Step sec: {stepSeconds}")
            timeDeltaError = 0
            self.timeStart = time.time()
            while True:
                await asyncio.sleep(0.5)

                if self.player.pauseEnd - self.player.pauseStart != 0: #pause started
                    if self.player.pauseEnd == 0:
                        continue
                    self.pauseDiff = self.player.pauseStart - self.player.pauseEnd
                    self.player.pauseStart = 0
                    self.player.pauseEnd = 0
                    mPrint('DEBUG', f'timePassed = {time.time() - initialTime}')
                    mPrint('DEBUG', f'pauseTime = {self.pauseDiff}')
                    mPrint('DEBUG', f'paused = {self.player.isPaused}')

                timePassed = time.time() - initialTime + self.pauseDiff
                if self.player.isPaused == False and timePassed >= stepSeconds:
                    timeDeltaError = timePassed - stepSeconds
                    initialTime = time.time() - timeDeltaError #idk, I think it's good now?

                    self.pauseDiff = 0
                    
                    self.stepProgress = stepSeconds * (currentStep)
                    #update timebar
                    for i in range(currentStep):
                        self.timeBar[i] = self.timelineChars[1]
                                    
                    #update message
                    currentStep += 1
                    await self.updateEmbed()
        
                    #reset time to current step
                    # mPrint('TEST', f"updating after: {timePassed}s; error: {timeDeltaError}")
                    # mPrint('TEST', f'step: {currentStep-1} of {self.timelinePrecision}')
                    
                if currentStep-1 == self.timelinePrecision: # BUG this gets triggered too soon
                    mPrint('DEBUG', "[EMBEDLOOP] Steps finished")
                    break
                
                if self.player.skipped:
                    mPrint('DEBUG', "[EMBEDLOOP] Skip detected")
                    self.player.skipped = False
                    await asyncio.sleep(0.5) #wait for player to set it's vars
                    break

                if self.player.endOfPlaylist:
                    await self.updateEmbed(True)
                    await self.player.stop()
                    mPrint("DEBUG","EOPlaylist, stopping embedloop")
                    return

                elif not self.player.voiceClient.is_connected():
                    mPrint("WARN", "Bot was disconnected from vc, stopping embedloop")
                    return
                
                if len(self.vchannel.members) == 1:
                    self.isAloneInVC == True
                    if self.aloneTimeStart == 0:
                        mPrint('WARN', 'I\'m alone in the vc...')
                        self.aloneTimeStart = time.time()
                    else:
                        if time.time() - self.aloneTimeStart > self.maxAloneTime:
                            mPrint('DEBUG', f'Waited for {time.time() - self.aloneTimeStart}s for people to join, now quitting')
                            mPrint('WARN', 'Fuck this, I\'m going where people actually want me')
                            await self.player.stop()
                            await self.updateEmbed(leftAlone = True)
                            return
                else:
                    self.isAloneInVC == False
                    self.aloneTimeStart = 0


    def getEmbed(self, stop = False, move = False, pnext = False, leftAlone = False) -> discord.Embed: #TODO, there are too many variables that do one thing, just fix this
        last5 = f'__**0-** {self.player.currentSong["trackName"]} [{self.player.currentSong["artist"]}]__\n'

        queue = []
        for x in self.player.queueOrder[0:5]:
            queue.append(self.player.queue[x])

        for i, x in enumerate(queue):
            if pnext and i == 0:
                last5 += '➡ '
            last5 += f'**{i+1}-** {x["trackName"]} [by: {x["artist"]}]\n'

        last5 = last5[:-1]

        embed = discord.Embed(
            title = f'Queue: {len(self.player.queueOrder)} songs. {"⏸" * self.player.isPaused} {"🔂" * self.player.loop} {"🔁" * self.player.loopQueue} {"🔀" * self.player.isShuffled}',
            description= f'Now Playing: **{self.player.currentSong["trackName"]}**\n{"".join(self.timeBar)} {conversion(self.stepProgress)} / {conversion(self.duration)}\n',
            color=0xff866f
        )
        artist = "N/A" if self.player.currentSong["artist"] == "" else self.player.currentSong["artist"]
        
        embed.add_field(name='Author:', value=f'{artist}')
        latency = "N/A" if self.player.voiceClient.latency == float('inf') else ("%.3fms" % self.player.voiceClient.latency)
        embed.add_field(name='Latency:', value=f'{latency}')
        if not move:
            embed.add_field(name='Last 5 in queue', value=last5, inline=False)
        else:
            last5 = ''
            for i in range(6):
                last5 += f"**{i}**- `                                      `\n"
            embed.add_field(name="This message was moved, you may find the new one below", value=last5, inline=False)
            embed.color = 0x1e1e1e


        if stop:
            embed.add_field(name=f'{"Queue finita" if self.player.endOfPlaylist else "Queue annullata"}', value=f'Grazie per aver ascoltato con CuloBot!', inline=False)
            embed.color = 0x1e1e1e
        elif leftAlone:
            embed.add_field(name="Queue annullata", value="Mi avete lasciato da solo nel canale vocale 😭")

        embed.set_footer(text='🍑 Comandi del player: https://notlatif.github.io/CuloBot/#MusicBot')

        return embed

    async def updateEmbed(self, stop = False, pnext = False, leftAlone = False):
        await asyncio.sleep(0.5)
        try:
            if stop or leftAlone:
                await self.embedMSG.edit(embed=self.getEmbed(stop=stop, leftAlone=leftAlone))
                await self.embedMSG.clear_reactions()
            else:
                await self.embedMSG.edit(embed=self.getEmbed(pnext=pnext))
        except discord.errors.HTTPException:
            mPrint('ERROR', f"DISCORD ERROR (probably embed had blank value)\n{traceback.format_exc()}")
    
        