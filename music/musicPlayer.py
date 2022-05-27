import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
from random import shuffle
import asyncio

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

timeline = ('▂', '▄')

def conversion(sec):
   sec_value = sec % (24 * 3600)
   hour_value = sec_value // 3600
   sec_value %= 3600
   min = sec_value // 60
   sec_value %= 60
   return f'{int(hour_value):02}:{int(min):02}:{int(sec_value):02}'

class Player():
    def __init__(self, bot : commands.bot, vc : discord.VoiceClient, queue, embed : discord.Embed, embedMSG = discord.Message) -> None:
        self.bot = bot
        self.queue : list = queue
        self.voiceClient = vc
        self.isConnected = True
        self.done = False
        self.embed = embed
        self.loop = False
        self.currentSong = None
        self.embedMSG = embedMSG
        self.duration = 0
        self.progress = 0
        self.timeBar = [timeline[0] for x in range(10)]

    def getVideoURL(self): #gets the url of the first song in queue (the one to play)
        print(f'[MUSIC] - searching for url ({self.currentSong["trackName"]})')
        track = self.currentSong['search']
        url = VideosSearch(track, limit = 1).result()['result'][0]['link']
        print(f'[DEBUG] FOUND URL: {url}')
        return url
    
    #wrapper that handles embed and song
    async def playNext(self):
        try:
            self.currentSong = self.queue.pop(0)
            flag = self.queue[0]['trackName']
            print(f'POP: {self.currentSong}')
            print(f'Song duration: {self.currentSong["duration_sec"]}')
            self.duration = self.currentSong['duration_sec']
            self.progress = 0
            self.timeBar = [timeline[0] for x in range(10)]
            await self.updateEmbed()
            self.playSong()

            steps = float(self.currentSong["duration_sec"]) / 10

            for x in range(10):
                await asyncio.sleep(steps)
                if flag != self.queue[0]['trackName']:
                    return #song was changed

                self.progress = steps * (x+1)
                for i, x in enumerate(self.timeBar):
                    if x == timeline[0]:
                        self.timeBar[i] = timeline[1]
                        break
                await self.updateEmbed()

            print("Wait elapsed")
            await self.playNext()

        except (IndexError, AttributeError, KeyError):
            print('[MUSIC] End of playlist.')
            self.done = True
            await self.stop()
            return

    def playSong(self):
        try:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(self.getVideoURL(), download=False)
                URL = info['formats'][0]['url']
                print(f'[MUSIC] - playing song ({self.currentSong["trackName"]}) ')
                self.voiceClient.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

        except discord.ClientException:
            #bot got disconnected
            print('[MUSIC WARN] Bot disconnected')
            self.voiceClient.cleanup()
            self.isConnected = False
            return

    async def updateEmbed(self):
        last5 = '' 
        last5 += f'__**0.** {self.currentSong["trackName"]}__\n'
        for i, x in enumerate(self.queue[:5]):
            last5 += f'**{i+1}**- {x["trackName"]} [by: {self.currentSong["artist"]}]\n'
        self.embed.title = f'Queue: {len(self.queue)} songs.'
        self.embed.description=f'Now Playing: **{self.currentSong["trackName"]}**\n{"".join(self.timeBar)} ({conversion(self.progress)} - {conversion(self.duration)})\n'
        self.embed.set_field_at(0, name='Author:', value=f'{self.currentSong["artist"]}')
        self.embed.set_field_at(1, name='Loop:', value=self.loop)
        self.embed.set_field_at(2, name='Last 5 in queue', value=f'{last5}', inline=False)
        await self.embedMSG.edit(embed=self.embed)

    async def skip(self):
        print(f'[MUSIC] - skipped track ({self.currentSong["trackName"]})')
        print(f'[MUSIC] - next is {self.queue[0]["trackName"]}')
        self.voiceClient.stop()
        await self.playNext()
        # no need to call playNext since lambda will do it for us

    def shuffle(self):
        shuffle(self.queue)

    def pause(self):
        self.voiceClient.pause()

    def resume(self):
        self.voiceClient.resume()

    def clear(self):
        self.queue = []

    async def stop(self):
        await self.voiceClient.disconnect()
        self.voiceClient.cleanup()


def searchYTurl(query): #gets the url of the first song in queue (the one to play)
    print(f'[MUSIC] - Searching for user requested song: ({query})')
    return VideosSearch(query, limit = 1).result()['result'][0]['link']