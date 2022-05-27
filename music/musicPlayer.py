import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
from random import shuffle

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

class Player():
    def __init__(self, bot : commands.bot, vc : discord.VoiceClient, queue, embed : discord.Embed) -> None:
        self.bot = bot
        self.queue : list = queue
        self.voiceClient = vc
        self.isConnected = True
        self.done = False
        self.embed = embed
        self.loop = False
        self.currentSong = None

    def getVideoURL(self): #gets the url of the first song in queue (the one to play)
        print(f'[MUSIC] - searching for url ({self.queue[0]["trackName"]})')
        track = self.queue[0]['search']
        return VideosSearch(track, limit = 1).result()['result'][0]['link']
    
    def playNext(self):
        try:
            print(f'POP: {self.currentSong}')
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(self.getVideoURL(), download=False)
                URL = info['formats'][0]['url']
                print(f'[MUSIC] - playing song ({self.queue[0]["trackName"]})')
                if not self.loop: self.currentSong = self.queue.pop(0)
                self.voiceClient.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: self.playNext())

        except (IndexError, AttributeError, KeyError):
            print('[MUSIC] End of playlist.')
            self.done = True
            return

        except discord.ClientException:
            #bot got disconnected
            print('[MUSIC ERROR] Bot disconnected')
            self.isConnected = False
            return

    def skip(self):
        print(f'[MUSIC] - skipped track ({self.queue[0]["trackName"]})')
        print(f'[MUSIC] - next is {self.queue[0]["trackName"]}')
        self.voiceClient.stop()
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

