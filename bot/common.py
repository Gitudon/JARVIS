import os
import asyncio
import traceback
import discord
from discord.ext import commands
from googleapiclient.discovery import build
import aiomysql

SERVICE_NAME = "JARVIS"
TOKEN = os.getenv("TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
