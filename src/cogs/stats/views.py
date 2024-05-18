from datetime import datetime
from random import choice
import platform
from distutils.util import strtobool  # I fucking love this command
from typing import Optional
import discord
from discord.ext import commands

import traceback

# Ew american spelling
from core.utils import humanize_timedelta


def get_client_uptime(uptime, brief=False):
    # Works well enough for what it does
    now = datetime.now()
    delta = now - uptime
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    if brief:
        fmt = "{h}h {m}m {s}s"
        if days:
            fmt = "{d}d " + fmt
        return fmt.format(d=days, h=hours, m=minutes, s=seconds)
    return humanize_timedelta(delta)
    
def generate_info_embed(client: discord.Client, ctx) -> discord.Embed:
    embed = discord.Embed(
        title="About Me!",
        description="Hi, I'm a nice Grandma",
        color=0xC55050,  # Nice light red
    )
    embed.set_image(url="https://i.imgur.com/U3Nyus7.gif")
    voice_channels = []
    text_channels = []
    for guild in client.guilds:
        voice_channels.extend(guild.voice_channels)
        text_channels.extend(guild.text_channels)

    embed.add_field(name="Guilds", value=len(client.guilds), inline=True)
    embed.add_field(name="Version", value=client._version, inline=True)
    embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
    embed.add_field(name="Uptime", value=get_client_uptime(client.uptime, brief=True))
    embed.set_footer(
        text="Made with 💖 by The Wizard!",
        icon_url="https://c.tenor.com/Gxa1JfN3334AAAAC/dm4uz3-sakamoto.gif",  # Spin gif
    )
    return embed
    
