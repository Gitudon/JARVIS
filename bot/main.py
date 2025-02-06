import discord
from discord.ext import commands
import asyncio
import os
import requests
from bs4 import BeautifulSoup

TOKEN =  os.getenv("TOKEN")
DISCORD_CHANNEL_ID= int(os.environ.get("DISCORD_CHANNEL_ID"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
intent = discord.Intents.default()
intent.message_content= True

client = commands.Bot(
    command_prefix='-',
    intents=intent
)

# youtubeのapiは一日あたり10000回まで。1分1回で1440回なので余裕
search_url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={YOUTUBE_CHANNEL_ID}&part=id&order=date"
latest_video="9r13OIuDcTY"

async def get_new_video():
    response = requests.get(search_url)
    data = response.json()
    video_id = data["items"][0]["id"]["videoId"]
    return video_id

async def check_new_video():
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    global latest_video
    new_video = await get_new_video()
    if new_video != latest_video:
        latest_video = [new_video]
        await channel.send("Sir, I have found a new video!")
        await channel.send(f"https://www.youtube.com/watch?v={new_video}")

@client.command()
async def test(ctx):
    if ctx.channel.id == DISCORD_CHANNEL_ID:
        await ctx.send("J.A.R.V.I.S. is working!")

@client.event
async def on_ready():
    print("J.A.R.V.I.S. is ready!")
    print(latest_video)
    while True:
        await check_new_video()
        await asyncio.sleep(60)

client.run(TOKEN)