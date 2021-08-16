# bot.py
import os
import discord
from discord.ext.commands.core import has_role
from dotenv import load_dotenv
import random
from discord.ext import commands
import giphy_client
from discord.ext.commands import Bot
import asyncio
from giphy_client.rest import ApiException
import time
import aiocron
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GIF_TOKEN = os.getenv('GIFY_TOKEN') 

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix=['punkBot ', 'punkbot ', 'pb ', 'PunkBot', 'PB'], intents=intents, help_command=None)

api_instance = giphy_client.DefaultApi()

messages = joined = 0

async def update_stats():
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
async def on_member_join(member):
    global joined
    joined += 1
    channel = discord.utils.get(member.guild.channels, name='off-topic-general')
    await channel.send(f'Welcome {member.mention}! Thanks for joining our discord.')

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

@aiocron.crontab('* * * * *')
async def announce_tournments():
    channel = bot.get_channel(849735687724335124)
    tourneys = getTournments()
    for t in tourneys:
        diff = datetime.fromisoformat(t["time"]) - datetime.utcnow()
        if diff > timedelta(minutes=30, seconds=0) and diff <= timedelta(minutes=30, seconds=59, milliseconds=999.999):
            await channel.send(f"{t['name']} is starting in {int(diff.total_seconds() / 60)} minutes! {t['link']}")

def getTournments():
    events = []
    URL = "https://lichess.org/team/chesspunks"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("tr", class_="enterable")
    index = 1
    for result in results:
        events += [{
            "name": result.find("span", class_="name").text,
            "info": result.find("span", class_="setup").text,
            "time": datetime.fromisoformat(result.find("time", class_="timeago abs")['datetime'][:-1]).strftime('%Y-%m-%d %H:%M'),
            "link": 'https://lichess.org' + result.find('td', class_="header").find('a')['href'],
        }]
        index += 1
    return events

bot.loop.create_task(update_stats())
bot.run(TOKEN)
