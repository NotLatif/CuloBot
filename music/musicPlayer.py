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
from discord.ext import commands
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
from random import shuffle
import asyncio
import time

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

def searchYTurl(query): #gets the url of the first song in queue (the one to play)
    print(f'[MUSIC] - Searching for user requested song: ({query})')
    return VideosSearch(query, limit = 1).result()['result'][0]['link']

def conversion(sec):
    sec = int(sec)
    sec_value = sec % (24 * 3600)
    hour_value = sec_value // 3600
    sec_value %= 3600
    min = sec_value // 60
    sec_value %= 60
    return f'{int(hour_value):02}:{int(min):02}:{int(sec_value):02}'

class Player():
    def __init__(self, vc : discord.VoiceClient, queue) -> None:
        self.queue : list = queue
        self.voiceClient = vc
        self.isConnected = True
        
        self.loop = False
        self.loopQueue = False
        self.currentSong = None
        self.duration = 0
        self.stepProgress = 0 #keep track of seconds passed in 10 chuncks
        
        #flags needed to communicate with EmbedHandler
        self.skipped = False
        self.isPaused = False
        self.songStartTime = 0
        self.pauseStart = 0
        self.pauseEnd = 0

    def getVideoURL(self): #gets the url of the first song in queue (the one to play)
        print(f'[DEBUG] - searching for url (QUERY: {self.currentSong["search"]})')
        track = self.currentSong['search']
        url = VideosSearch(track, limit = 1).result()['result'][0]['link']
        print(f'[DEBUG] FOUND URL: {url}')
        return url
    
    #wrapper that handles embed and song
    async def starter(self):
        self.playNext(None)
        

    def playNext(self, error):
        print("---------------- PLAYNEXT ----------------")
        if error != None: print(f"[ERROR]: {error}")

        if len(self.queue) != 0 and self.loop == False:
            self.currentSong = self.queue.pop(0)
            print(f'POP: {self.currentSong}')
            if self.loopQueue:
                print("looping queue, append song to end")
                self.queue.append(self.currentSong)
            
        else:
            if self.loop == False: 
                print('[MUSIC] End of playlist.')
                ex, val, tb = sys.exc_info()
                traceback.print_exception(ex, val, tb)
                return

        self.playSong()

    def playSong(self):
        try:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(self.getVideoURL(), download=False)
                URL = info['formats'][0]['url']

                if self.voiceClient.is_playing(): 
                    print('[WARN]: musicbot was already playing, stopping song.')
                    self.voiceClient.stop()

                print(f'[MUSIC] - Now Playing: ({self.currentSong["trackName"]}) ')
                self.songStartTime = time.time()
                self.voiceClient.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after= self.playNext)

        except discord.ClientException:
            #bot got disconnected
            print('[WARN] Bot is not connected to vc')
            self.voiceClient.cleanup()
            self.isConnected = False
            return
    
    async def skip(self):
        if len(self.queue) > 0:
            print(f'[MUSIC] - skipped track ({self.currentSong["trackName"]})')
            print(f'[MUSIC] - next is {self.currentSong["trackName"] if self.loop else self.queue[0]["trackName"]}')
            self.voiceClient.stop()
            self.skipped = True
            # no need to call playNext since lambda will do it for us
        else:
            await self.stop()

    def restart(self):
        self.queue.insert(1, self.currentSong)
        print(f'[MUSIC] - restarted track ({self.currentSong["trackName"]})')
        self.voiceClient.stop()

    def shuffle(self):
        shuffle(self.queue)

    def pause(self):
        self.voiceClient.pause()
        self.isPaused = True
        self.pauseStart = time.time()

    def resume(self):
        self.voiceClient.resume()
        self.isPaused = False
        self.pauseEnd = time.time()

    def clear(self):
        self.queue = []
    

    async def stop(self):
        await self.voiceClient.disconnect()
        self.voiceClient.cleanup()

class MessageHandler():
    #Handles the embed of the player in parallel with the player
    def __init__(self, player : Player, embedMSG = discord.Message) -> None:
        self.player = player
        self.embedMSG = embedMSG

        self.timelinePrecision = 14
        self.timelineChars = ('▂', '▄')
        self.timeBar = []

        self.stepProgress = 0
        self.duration = 0
        self.pauseDiff = 0

    async def start(self):
        await self.embedLoop()
        print('INFO started handler')

    async def embedLoop(self):
        while True: #foreach song
            currentSong = self.player.currentSong 
            self.timeBar = [self.timelineChars[0] for x in range(self.timelinePrecision)]
            
            print(f'Song duration: {currentSong["duration_sec"]}')

            stepSeconds = float(currentSong["duration_sec"]) / self.timelinePrecision
            self.duration = currentSong["duration_sec"]
            self.stepProgress = 0

            await self.updateEmbed()

            initialTime = self.player.songStartTime
            #update timestamp every "step" seconds
            currentStep = 1
            print(f"Step sec: {stepSeconds}")
            while True:
                await asyncio.sleep(1)
            
                if self.player.pauseEnd - self.player.pauseStart != 0: #pause started
                    if self.player.pauseEnd == 0:
                        continue
                    self.pauseDiff = self.player.pauseStart - self.player.pauseEnd
                    self.player.pauseStart = 0
                    self.player.pauseEnd = 0
                    print(f'[DEBUG] timePassed = {time.time() - initialTime}')
                    print(f'[DEBUG] pauseTime = {self.pauseDiff}')
                    print(f'[DEBUG] paused = {self.player.isPaused}')

                timePassed = time.time() - initialTime + self.pauseDiff
                if self.player.isPaused == False and timePassed >= stepSeconds:
                    self.pauseDiff = 0
                    initialTime = time.time()
                    print(f"updating after: {timePassed}s")
                    #reset time to current step
                    
                    self.stepProgress = stepSeconds * (currentStep)
                    #update timebar
                    for i, y in enumerate(self.timeBar):
                        if y == self.timelineChars[0]:
                            self.timeBar[i] = self.timelineChars[1]
                            break
                    
                    #update message
                    currentStep += 1
                    await self.updateEmbed()
                
                if currentSong != self.player.currentSong:
                    print("song was skipped")
                    break

                if currentStep == self.timelinePrecision:
                    print("Steps finished")
                    break
                
                if self.player.skipped:
                    print("Skip detected")
                    self.player.skipped = False
                    await asyncio.sleep(0.5) #wait for player to set it's vars
                    break

    def getEmbed(self):
        last5 = f'__**0.** {self.player.currentSong["trackName"]} [{self.player.currentSong["artist"]}]__\n'
        for i, x in enumerate(self.player.queue[:5]):
            last5 += f'**{i+1}**- {x["trackName"]} [by: {x["artist"]}]\n'

        last5 = last5[:-1]

        embed = discord.Embed(
            title = f'Queue: {len(self.player.queue)} songs. {"⏸" * self.player.isPaused} {"🔂" * self.player.loop} {"🔁" * self.player.loopQueue}',
            description= f'Now Playing: **{self.player.currentSong["trackName"]}**\n{"".join(self.timeBar)} ({conversion(self.stepProgress)} - {conversion(self.duration)})\n',
            color=0xff866f
        )
        artist = "N/A" if self.player.currentSong["artist"] == "" else self.player.currentSong["artist"]
        
        embed.add_field(name='Author:', value=f'{artist}')
        embed.add_field(name='Loop:', value=str(self.player.loop))
        embed.add_field(name='Last 5 in queue', value=f'{last5}', inline=False)
        
        #print(f'DEBUG EMBED VALUES:\nAuthor: {self.player.currentSong["artist"]}\nLoop: {str(self.player.loop)}\nLast5: {last5}')
        
        return embed

    async def updateEmbed(self):
        await asyncio.sleep(0.5)
        try:
            await self.embedMSG.edit(embed=self.getEmbed())
        except discord.errors.HTTPException:
            print("DISCORD ERROR (probably embed had blank value)")
    
        

# except (IndexError, AttributeError, KeyError) as e:
#     print('[MUSIC] End of playlist.')
#     ex, val, tb = sys.exc_info()
#     traceback.print_exception(ex, val, tb)
#     await self.stop()
#     return