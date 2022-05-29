import sys
import discord
from discord.ext import commands
import traceback
import asyncio
from random import shuffle

sys.path.insert(0, 'music/')
import spotifyParser
import youtubeParser
import musicPlayer

def parseUrl(url):
    if 'open.spotify.com' in url:
        tracks = spotifyParser.getSongs(url)

    else: #TODO implement
        tracks = youtubeParser.getSongs(url)

    return tracks

async def play(url, ctx : commands.Context, bot : discord.Client):

    tracks = parseUrl(url)
    shuffle(tracks)

    last5 = ''
    for i, x in enumerate(tracks[:6]):
        last5 += f'**{i}**- {x["trackName"]} [by: {x["artist"]}]\n'
     
    embed = discord.Embed(
        title=f'Queue: {len(tracks)} songs.',
        description=f'Now Playing: **{tracks[0]["trackName"]}**\n▂▂▂▂▂▂▂▂▂▂ (00:00 - 00:00)\n',
        color=0xff866f
    )
    if( tracks[0]["artist"] != ''):
        embed.add_field(name='Author:', value=f'{tracks[0]["artist"]}', inline=True)
    embed.add_field(name='Loop:', value=f'False', inline=True)
    if ( last5 != "" ):
        embed.add_field(name='Last 5 in queue', value=f'{last5}', inline=False)
    embed.set_footer(text='🍑 the best bot 🎶')
     
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

    player = musicPlayer.Player(bot, voice, tracks, embed, embedMSG)

    
    try:
        task = asyncio.create_task(player.playNext())

    except Exception as e:
        print('exception')
        await voice.disconnect()
        voice.cleanup()
        ex, val, tb = sys.exc_info()
        traceback.print_exception(ex, val, tb)

    def check(m : discord.Message, u=None):	#check if message was sent in thread using ID
        return m.author != bot.user and m.channel.id == ctx.channel.id

    async def userInput(task):
        while True:
            try:
                userMessage : discord.Message = await bot.wait_for('message', check=check)	
            except Exception:
                print('WAITFOR EXCEPTION')
                await voice.disconnect()
                voice.cleanup()
                ex, val, tb = sys.exc_info()
                traceback.print_exception(ex, val, tb)


            if player.done == True:
                return

            if userMessage.content.split()[0] == 'skip':
                skip = userMessage.content.split()
                task.cancel()
                if len(skip) == 2 and skip[1].isnumeric():
                    for x in range(int(skip[1])-1):
                        player.queue.pop(0)
                    task = asyncio.create_task(player.skip())
                    continue
                task = asyncio.create_task(player.skip())

            elif userMessage.content == 'pause' and userMessage.author.id == 348199387543109654:
                await player.pause()

            elif userMessage.content == 'shuffle':
                player.shuffle()
                await userMessage.add_reaction('🔀')
                await userMessage.add_reaction('✅')
                
            elif userMessage.content == 'resume' and userMessage.author.id == 348199387543109654:
                await player.resume()

            elif userMessage.content == 'stop':
                await player.stop()
                task.cancel()
                return 0
            
            elif userMessage.content == 'clear':
                player.clear()

            elif userMessage.content == 'loop' and userMessage.author.id == 348199387543109654:
                player.loop = True
                await userMessage.add_reaction('🔂')

            elif userMessage.content == 'queue':
                embedMSG = await ctx.send(embed=player.embed)

            elif userMessage.content.split()[0] in ['!play', '!p', 'play', 'p']:
                request = userMessage.content.split()
                if len(request) == 1:
                    userMessage.reply("Devi darmi un link bro")
                else:
                    request = ' '.join(request[1:])
                    print(f'Queueedit: {request}')
                    tracks = parseUrl(request)
                    for t in tracks:
                        player.queue.append(t)
                    await player.updateEmbed()
            
            elif userMessage.content.split()[0] in ['!playnext', '!pnext', 'playnext', 'pnext']:
                request = userMessage.content.split()
                if len(request) == 1:
                    userMessage.reply("Devi darmi un link bro")
                else:
                    request = ' '.join(request[1:])
                    print(f'Queueedit: {request}')
                    tracks = parseUrl(request)
                    player.queue = tracks + player.queue
                    await player.updateEmbed()

            if userMessage.content in ['shuffle', 'clear', 'loop']:
                await player.updateEmbed()
            

    asyncio.create_task(userInput(task))

cmds = ['skip', 'pause', 'shuffle', 'resume', 'stop', 'clear', 'loop', 'queue', '!playnext', '!pnext']

# vc.source = discord.PCMVolumeTransformer(vc.source, 1)

