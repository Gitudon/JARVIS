import discord
from discord.ext import commands
from googleapiclient.discovery import build
import mysql.connector
import asyncio
import os

TOKEN = os.getenv("TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
intent = discord.Intents.default()
intent.message_content = True
client = commands.Bot(command_prefix="-", intents=intent)


# MySQLの接続設定
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


async def run_sql(sql: str, params: tuple):
    conn = get_connection()
    cursor = conn.cursor(buffered=True)
    if params != ():
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    if sql.strip().upper().startswith("SELECT"):
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    else:
        conn.commit()
        cursor.close()
        conn.close()
        return


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
        sent_urls = await run_sql(
            "SELECT url FROM sent_urls WHERE service = 'JARVIS'",
            (),
        )
        for i in range(len(sent_urls)):
            if type(sent_urls[i]) is tuple:
                sent_urls[i] = sent_urls[i][0]
        for item in response["items"]:
            video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            if video_url not in sent_urls:
                title = item["snippet"]["title"]
                await run_sql(
                    "INSERT INTO sent_urls (url, title, category, service) VALUES (%s,  %s, %s, %s)",
                    (video_url, title, "new_video", "JARVIS"),
                )
                video_urls.append(video_url)
        return video_urls
    except Exception as e:
        print(e)
        return "ERROR"


async def send_new_video(new_video):
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if new_video is None:
        return
    await channel.send(f"Sir, I have found a new video!\n\n{new_video}")


@client.command()
async def test(ctx):
    if ctx.channel.id == DISCORD_CHANNEL_ID:
        await ctx.send("J.A.R.V.I.S. is working!")


@client.event
async def on_ready():
    print("J.A.R.V.I.S. is ready!")
    while True:
        try:
            buf_videos = await get_new_videos()
            if buf_videos != "ERROR":
                for buf_video in buf_videos:
                    await send_new_video(buf_video)
        except Exception as e:
            print(f"Error in on_ready loop: {e}")
        await asyncio.sleep(900)


client.run(TOKEN)
