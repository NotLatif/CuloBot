import asyncio
import discord
from discord.ext import commands


async def poll(ctx : commands.Context, message):
    title = message[0]
    questions = {}

    for i, x in enumerate(message[1:]):
        letter = chr(ord('`')+ (i+1))
        questions[f':regional_indicator_{letter}:'] = x
    
    desc = ''
    for x in questions:
        desc += f'{x} {questions[x]}\n'
    
    embed = discord.Embed(
        title=f'Loading poll please wait...',
    )
    embedMSG = await ctx.send(embed=embed)

    voters = {}

    for x in range(len(questions)):
        letter = chr(ord('`')+ (x+1))
        print(letter)
        
        await embedMSG.add_reaction(u"\u1F1F1")
    
    embed = discord.Embed(
        title=f'Poll from {ctx.author}: {title}',
        description=desc
    )

    embedMSG.edit(embed=embed)

    print(u"U+1F1E6")

    
