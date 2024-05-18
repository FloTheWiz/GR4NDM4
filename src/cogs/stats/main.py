import datetime 
import time
import platform
import logging

import discord 
from discord.ext import commands
from discord import app_commands
from cogs.stats.views import (generate_info_embed, get_client_uptime)

log = logging.getLogger(__name__)

async def setup(client):
    await client.add_cog(Stats(client))
   


class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.hybrid_command(
        name="about", usage=";about", aliases=["info","grandma","GR4NDM4","author"]
        )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def _about(self, ctx: commands.Context):
        e = generate_info_embed(self.client, ctx)
        await ctx.send(embed=e)
        
        
    @commands.hybrid_command(name="ping", description="Ping the bot.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def ping(self, ctx: commands.Context):
        """Show latency in seconds & milliseconds"""
        before = time.monotonic()
        message = await ctx.send(":ping_pong: Pong !")
        ping = (time.monotonic() - before) * 1000
        await message.edit(
            content=f":ping_pong: Pong ! in `{float(round(ping/1000.0,3))}s` ||{int(ping)}ms||"
        )

    @commands.hybrid_command(name="uptime", usage="!uptime")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def _uptime(self, ctx: commands.Context):
        """
        Gets the time since the bot first connected to Discord
        """
        em = discord.Embed(
            title="Local time",
            description=str(datetime.datetime.now())[:-7],
            colour=0x14E818,
        )
        em.set_author(
            name=self.client.user.name, icon_url="https://i.imgur.com/3VPTx2K.gif"
        )
        em.add_field(
            name="Current uptime",
            value=get_client_uptime(self.client.uptime, brief=True),
            inline=True,
        )
        em.add_field(name="Start time", value=str(self.client.uptime)[:-7], inline=True)
        em.set_footer(
            text="Made with 💖 by Xorhash",
            icon_url="https://media.giphy.com/media/qjPD3Me0OCvFC/giphy.gif",
        )
        await ctx.send(embed=em)
        
        