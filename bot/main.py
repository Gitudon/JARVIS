import discord
from discord.ext import commands
from googleapiclient.discovery import build
import asyncio
import os
import json
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

async def get_new_video():
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        response = youtube.search().list(
            part = "snippet",
            channelId = YOUTUBE_CHANNEL_ID,
            maxResults = 5, 
            order = "date", 
            type="video"
        ).execute()
        video_ids = []
        for item in response["items"]:
            video_ids.append(item["id"]["videoId"])
        return video_ids
    except Exception as e:
        print(e)
        return "ERROR"

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
    latest_video=await get_new_video()
    while True:
        buf_videos = await get_new_video()
        if buf_videos != "ERROR":
            for buf_video in buf_videos:
                if buf_video not in latest_video:
                    await send_new_video(buf_video)
                    latest_video.append(buf_video)
            print(latest_video)
        #15分おきで様子を見る
        await asyncio.sleep(900)

client.run(TOKEN)