import asyncio
import logging
import os
import traceback
import aiomysql
import discord
from discord.ext import commands
from googleapiclient.discovery import build

SERVICE_NAME = "JARVIS"
TOKEN = os.getenv("TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

# ログの設定
format = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
)
handler = logging.StreamHandler()
handler.setFormatter(format)
logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
bot_logger = logging.getLogger(SERVICE_NAME)


async def write_log_message(message: str, category: str):
    if category == "INFO":
        bot_logger.info(message)
    elif category == "ERROR":
        bot_logger.error(message)
    else:
        bot_logger.warning(message)
