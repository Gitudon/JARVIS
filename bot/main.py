import discord
from discord.ext import commands
import asyncio
import os
import requests

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

async def get_new_video():
    response = requests.get(search_url)
    data = response.json()
    video_id = data["items"][0]["id"]["videoId"]
    return video_id

async def send_new_video(new_video):
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    await channel.send("Sir, I have found a new video!")
    await channel.send(f"https://www.youtube.com/watch?v={new_video}")

@client.command()
async def test(ctx):
    if ctx.channel.id == DISCORD_CHANNEL_ID:
        await ctx.send("J.A.R.V.I.S. is working!")

@client.event
async def on_ready():
    print("J.A.R.V.I.S. is ready!")
    latest_video=[]
    latest_video.append(await get_new_video())
    while True:
        buf_video = await get_new_video()
        if buf_video not in latest_video:
            await send_new_video(buf_video)
            latest_video.append(buf_video)
            print(latest_video)
        if len(latest_video)>=50:
            latest_video = latest_video[:10]
        await asyncio.sleep(60)

client.run(TOKEN)