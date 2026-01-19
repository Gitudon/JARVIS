import os
import asyncio
import traceback
import discord
from discord.ext import commands
from googleapiclient.discovery import build
import aiomysql

TOKEN = os.getenv("TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
intent = discord.Intents.default()
intent.message_content = True
client = commands.Bot(command_prefix="-", intents=intent)
task = None


# MySQLの接続設定
class UseMySQL:
    pool: aiomysql.Pool | None = None

    @classmethod
    async def init_pool(cls):
        if cls.pool is None:
            cls.pool = await aiomysql.create_pool(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                db=os.getenv("DB_NAME"),
                autocommit=True,
                minsize=1,
                maxsize=5,
            )

    @classmethod
    async def close_pool(cls):
        if cls.pool:
            cls.pool.close()
            await cls.pool.wait_closed()
            cls.pool = None

    @classmethod
    async def run_sql(cls, sql: str, params: tuple = ()) -> list | None:
        async with cls.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
                if sql.strip().upper().startswith("SELECT"):
                    rows = await cur.fetchall()
                    return [r[0] if isinstance(r, tuple) else r for r in rows]


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
        for item in response["items"]:
            video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            sent = (
                await UseMySQL.run_sql(
                    "SELECT url FROM sent_urls WHERE service = 'JARVIS' AND url = %s",
                    (video_url,),
                )
                != []
            )
            if not sent:
                title = item["snippet"]["title"]
                await UseMySQL.run_sql(
                    "INSERT INTO sent_urls (url, title, category, service) VALUES (%s,  %s, %s, %s)",
                    (video_url, title, "new_video", "JARVIS"),
                )
                video_urls.append(video_url)
        return video_urls
    except Exception as e:
        print(e)
        return "ERROR"


async def send_new_video(new_video: str):
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if not new_video:
        return
    await channel.send(f"Sir, I have found a new video!\n\n{new_video}")


async def main():
    while True:
        try:
            buf_videos = await get_new_videos()
            if buf_videos != "ERROR":
                for buf_video in buf_videos:
                    await send_new_video(buf_video)
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
        await asyncio.sleep(900)


@client.command()
async def test(ctx: commands.Context):
    if ctx.channel.id == DISCORD_CHANNEL_ID:
        await ctx.send("J.A.R.V.I.S. is working!")


@client.event
async def on_ready():
    global task
    await UseMySQL.init_pool()
    print("J.A.R.V.I.S. is ready!")
    if task is None or task.done():
        task = asyncio.create_task(main())


client.run(TOKEN)
