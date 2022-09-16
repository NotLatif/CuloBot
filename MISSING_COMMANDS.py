#Things yet to implement in the new version

import discord
from discord.ext import commands

@bot.command(name='getimage')
async def test(ctx : commands.Context):
    if ctx.author.id != 348199387543109654:
        return
    user = ctx.message.content.split()[1][2:-1]
    member = await ctx.guild.fetch_member(int(user))
    await ctx.channel.typing()
    await joinImageSend(member, ctx.guild, ctx.channel)

@bot.command(name='bot_restart')
async def test(ctx : commands.Context):
    #ONLY FOR TESTING PURPOSES. DO NOT ABUSE THIS COMMAND
    if ctx.message.author.id == 348199387543109654 or ctx.guild.id == 694106741436186665:
        mPrint("WARN", "RESTARTING BOT")
        await ctx.send("WARNING, DO NOT ABUSE THIS COMMAND...\nplease wait...")
        os.system(f"bot.py RESTART {ctx.guild.id} {ctx.channel.id} {ctx.message.id}")
        #sys.exit()

@bot.command(name='rawdump')
async def rawDump(ctx : commands.Context):
    await ctx.send(f'```JSON dump for {ctx.guild.name}:\n{json.dumps(settings[int(ctx.guild.id)], indent=3)}```')

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

@bot.command(name = 'help')
async def embedpages(ctx : commands.Context):
    e = discord.Embed (
        title = 'CuloBot',
        description = strings["bot.help.description"],
        colour = col.orange
    ).set_footer(text=strings["bot.help.footer"])
    
    e.set_thumbnail(url='https://i.pinimg.com/originals/b5/46/3c/b5463c3591ec63cf076ac48179e3b0db.png')

    page0 = e.copy().set_author(name='Help 0/4, Info', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page1 = e.copy().set_author(name='Help 1/4, Culo!', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page2 = e.copy().set_author(name='Help 2/4, Music!', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page3 = e.copy().set_author(name='Help 3/4, CHECKMATE', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    page4 = e.copy().set_author(name='Help 4/4, Misc', icon_url='https://cdn.discordapp.com/avatars/696013896254750792/ac773a080a7a0663d7ce7ee8cc2f0afb.webp?size=256')
    
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
    page2.add_field(name='!music', value=strings["bot.help.music.info"], inline=False)#ok
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

    page3.add_field(name='!chess boards', value=strings["bot.help.chess.boards"], inline=False)#ok
    page3.add_field(name='!chess design [see|add|del|edit]', value=strings["bot.help.chess.design"], inline=False)#ok
    page3.add_field(name='!chess see <name | FEN>', value=strings["bot.help.chess.see"], inline=False)#ok
    page3.add_field(name='!chess add <name> <FEN>', value=strings["bot.help.chess.add"], inline=False)#ok
    page3.add_field(name='!chess remove <name>', value=strings["bot.help.chess.remove"], inline=False)#ok
    page3.add_field(name='!chess rename <name> <newName>', value=strings["bot.help.chess.rename"], inline=False)#ok
    page3.add_field(name='!chess edit <name> <FEN>', value=strings["bot.help.chess.edit"], inline=False)#ok

    #Page 4 misc
    page4.add_field(name='!ping', value='Pong!', inline=False)#ok
    page4.add_field(name='!rawdump', value=strings["bot.help.misc.rawdump"], inline=False)#ok
    page4.add_field(name='joinmsg [msg]', value=strings["bot.help.misc.joinmsg"], inline=False)
    page4.add_field(name='leavemsg [msg]', value=strings["bot.help.misc.leavemsg"], inline=False)
    page4.add_field(name='joinimage [True|False]', value=strings["bot.help.misc.joinimage"], inline=False)

    #fotter for page 1
    page0.add_field(name='Source code', value=strings['bot.source_code'], inline=False)
    page0.add_field(name=strings['bot.help.issues'], value=strings['bot.issues'], inline=False)
    
    page1.add_field(name='Source code', value=strings['bot.source_code'], inline=False)
    page1.add_field(name=strings['bot.help.issues'], value=strings['bot.issues'], inline=False)
    
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
            else:
                i = len(pages)-1
            await msg.edit(embed = pages[i])
        elif str(emoji) == '▶':
            if i < len(pages) - 1:
                i += 1
            else:
                i = 0
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



# you coud use discord ui for chess interactions before games!!!!
@tree.command(name="ephemeral", description="test")
async def ephe(interaction : discord.Interaction):
    select = discord.ui.Select(options=[
        discord.SelectOption(label="White", emoji="🤍"),
        discord.SelectOption(label="Black", emoji="🖤")
    ])
    view = discord.ui.View()
    view.add_item(select)
    embed = discord.Embed(
        title="squadre",
        description="teaotA",
        color=0x242424
    )
    async def mycallback(interaction : discord.Interaction):
        await interaction.response.send_message(f"Okay, {select.values[0]}") #0 because it only has 1 select
    select.callback = mycallback

    await interaction.response.send_message("Scegli una squadra", embed=embed,view=view)
    # await interaction.response.send_message("Hello", ephemeral=True)





@bot.command(name='suggest', pass_context=True) #Player
async def suggest(ctx : commands.Context):
    await ctx.channel.typing()
    await asyncio.sleep(2) #ensure that file exists
    if os.path.isfile(f'botFiles/suggestions/{str(ctx.guild.id)}.json'):
        with open(f'botFiles/{str(ctx.guild.id)}.json') as f:
            newOverwrites = json.load(f)
            if settings[ctx.guild.id]['youtube_search_overwrite'] == newOverwrites:
                await ctx.send('Non è cambiato niente...')
            else:
                settings[ctx.guild.id]['youtube_search_overwrite'] = newOverwrites
                dumpSettings()
                await ctx.send('Done')
    else:
        await ctx.send('C\'è stato un errore...')