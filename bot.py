# bot.py
import os
import discord
import json
from dotenv import load_dotenv
import random
from discord.ext import commands
import giphy_client
from discord.ext.commands import Bot
import asyncio
from giphy_client.rest import ApiException
from cogs.Admin import Admin
import time

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GIF_TOKEN = os.getenv('GIFY_TOKEN') 
BOT_OWNER_ID = os.getenv('OWNER')

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix=['punkBot ', 'punkbot '], intents=intents, help_command=None)

bot.add_cog(Admin(bot, BOT_OWNER_ID))

api_instance = giphy_client.DefaultApi()

messages = joined = 0

owner_id = BOT_OWNER_ID

async def updateStats():
    await bot.wait_until_ready()
    global messages, joined

    while not bot.is_closed():
        try:
            with open('logs.txt', 'a') as f:
                f.write(f"Time: {int(time.time())}, messages: {messages}, members joined: {joined}\n")
            messages = 0
            joined = 0

            await asyncio.sleep(6.0)
        except Exception as e:
            print(e, flush=True)

@bot.event
async def onMessage(message):
    banned_terms = []
    if any(banned_word in message.content for banned_word in banned_terms):
        await message.channel.send("No swearing" + message.author.name)
        await message.delete()
    if message.content.lower() == "punkBot help":
        em = discord.Embed(title = 'Command list', color=discord.Color.green())
        em.add_field(name="Gifs", value="Commands:\n \a - gif\n Usage:\n \a - punkBot gif <word>", inline = False)
        em.add_field(
            name="Admin/Owner only",
            value="Commands:\n \a - ban\n \a - unban\n \a - addRole\n \a - removeRole\n Usage:\n \a - punkBot ban <@user>\n \a - punkBot unban <user id>\n \a - punkBot add_role/remove_role <@user> <role>"
        )
        await message.channel.send(content=None, embed=em)
    await bot.process_commands(message)


async def get_msg(channel, msgID: int):
    msg = await channel.fetch_message(msgID)
    return(msg)

@bot.command()
async def deleteMsg(ctx, arg):
    print(arg, flush=True)
    if ctx.message.author.guild_permissions.administrator or ctx.message.author.id == int(owner_id):
        msg = await get_msg(ctx.message.channel, arg)
        print(ctx.message.channel, flush=True)
        await msg.delete()
    else:
        return 1

@bot.event
async def onMemberJoin(member):
    global joined
    joined += 1
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Enjoy your stay {member.mention}!')

@bot.command()
async def getUserList(ctx):
    mb_list = []
    with open('users.txt','w') as f:
        async for member in ctx.guild.fetch_members(limit=None):
            print("{},{}".format(member,member.id), file=f,)
            mb_list.append(member)
    print("done")
    return mb_list

@bot.command()
async def gif(ctx, arg):
    if not arg:
        await ctx.send('You must specify an argument!')
    gify = await searchGifs(arg)
    await ctx.send(gify)

async def searchGifs(query):
    try:
        response = api_instance.gifs_search_get(GIF_TOKEN, query, limit=15, rating='r')
        lst = list(response.data)
        gif = random.choices(lst)

        return gif[0].url

    except ApiException as e:
        return "Exception when calling DefaultApi->gifs_search_get: %s\n" % e

bot.loop.create_task(updateStats())
bot.run(TOKEN)
