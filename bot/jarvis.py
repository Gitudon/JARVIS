import discord
from discord.ext import commands
from googleapiclient.discovery import build
import mysql.connector
import asyncio
import os
import json
import requests

TOKEN = os.getenv("TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
if DISCORD_CHANNEL_ID[-1] not in "0123456789":
    DISCORD_CHANNEL_ID = int(DISCORD_CHANNEL_ID[:-1])
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
intent = discord.Intents.default()
intent.message_content = True
client = commands.Bot(command_prefix="-", intents=intent)
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    username=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
)
cursor = conn.cursor(buffered=True)


async def get_new_videos():
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        response = (
            youtube.search()
            .list(
                part="snippet",
                channelId=YOUTUBE_CHANNEL_ID,
                maxResults=5,
                order="date",
                type="video",
            )
            .execute()
        )
        video_urls = []
        cursor.execute("SELECT url FROM sent_urls WHERE service = 'JARVIS'")
        sent_urls = cursor.fetchall()
        for i in range(len(sent_urls)):
            if type(sent_urls[i]) is tuple:
                sent_urls[i] = sent_urls[i][0]
        for item in response["items"]:
            video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            if video_url not in sent_urls:
                title = item["snippet"]["title"]
                query = """
                INSERT INTO sent_urls (url, title, category, service) VALUES (%s,  %s, %s, %s)
                """
                cursor.execute(
                    query,
                    (video_url, title, "new_video", "JARVIS"),
                )
                conn.commit()
                video_urls.append(video_url)
        return video_urls
    except Exception as e:
        print(e)
        return "ERROR"


async def send_new_video(new_video):
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    await channel.send(f"Sir, I have found a new video!\n\n{new_video}")


@client.command()
async def test(ctx):
    if ctx.channel.id == DISCORD_CHANNEL_ID:
        await ctx.send("J.A.R.V.I.S. is working!")


@client.event
async def on_ready():
    print("J.A.R.V.I.S. is ready!")
    while True:
        buf_videos = await get_new_videos()
        if buf_videos != "ERROR":
            for buf_video in buf_videos:
                await send_new_video(buf_video)
        await asyncio.sleep(900)


client.run(TOKEN)
