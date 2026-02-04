from common import *
from use_mysql import UseMySQL
from crawler import *

intent = discord.Intents.default()
intent.message_content = True
client = commands.Bot(command_prefix="-", intents=intent)
task = None


class JARVIS:
    @staticmethod
    async def send_new_video(new_video: str):
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        if not new_video:
            return
        await channel.send(f"Sir, I have found a new video!\n\n{new_video}")


async def main():
    while True:
        try:
            buf_videos = await Crawler.get_new_videos()
            if buf_videos != "ERROR":
                for buf_video in buf_videos:
                    await JARVIS.send_new_video(buf_video)
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
