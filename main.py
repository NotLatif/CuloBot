import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import random
from datetime import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')[1:-1]
GUILD = os.getenv('DISCORD_GUILD')[1:-1]

client = discord.Client()

bot = commands.Bot(command_prefix='!')

#VAR LOAD
with open("vars.cfg", "r"):
    pass #response_perc = 

@client.event   ## EXCEPTION LOGGER
async def on_error(event, *args, **kwargs):
    now = datetime.now()
    current_time = now.strftime("[%d/%m/%y %H:%M:%S]")
    
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'{current_time} Unhandled message: {args[0]}\n')
        else:
            raise

@client.event   ## BOT ONLINE
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event   ## MEMBER JOIN XXX
async def on_member_join(member):
    
    await member.create_dm()
    await member.dm_channel.send(
        f'A {member.name} piace il culo.'
    )

@client.event   ## DETECT AND RESPOND TO MSG
async def on_message(message):
    if message.author == client.user: #don't respond to self
        return
    
    if len(message.content.split()) < 2:
        return

    if random.randrange(0, 100) > 100: #45% chance of answering
        return

    msg = message.content
    msg = msg.split() #["ciao", "prova", "rovb"]
    msg[random.randrange(0, len(msg))] = "culo"
    msg = " ".join(msg)

    await message.channel.send(msg)
 
@bot.command(name='response%', help="Indica la percentuale (intera) di volte a cui il bot risponde ad un messaggio")
async def perc(ctx):  ## BOT COMMANDS
    
    await ctx.send("ok")


client.run(TOKEN)


