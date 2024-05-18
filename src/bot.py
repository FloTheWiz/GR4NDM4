from datetime import datetime
import logging
import discord
from discord.ext import commands
from core.cogmanager import cogs_manager

description = "Hello, I am a nice Grandma here to show you the Wiki!"
log = logging.getLogger(__name__)


def _prefix_callable(bot, msg: discord.Message):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append(";")
    return base
        
class grandma(commands.Bot):
    def __init__(self, cogs: list, secrets):
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
            message_content=True,
        )
            
        super().__init__(
            command_prefix = _prefix_callable,
            description = description,
            pm_help = None, 
            help_attr=dict(hidden=True),
            allowed_mentions = allowed_mentions,
            intents=intents
            )
        # Reminder to make a help function. 
        
        self._cogs = cogs
        self._secrets = secrets
        self._version = '0.1'
        self.uptime = datetime.now() 
        # we use uptime instead of _uptime because of the function _uptime. Avoiding naming collisions. 
        
        
    async def on_ready(self):
        print(
            f"Username: {self.user} | {discord.__version__=}\nGuilds: {len(self.guilds)} | Users: {len(self.users)}|Prefix: {self.command_prefix}"
        )
        print(
            f"Invite Link: https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=52288&scope=bot%20applications.commands"
        )
        log.info('Ready: %s (ID: %s)', self.user, self.user.id)
        

    async def startup(self):
        """Sync application commands"""
        await self.wait_until_ready()
        await self.tree.sync()
        print("Ready and Tree Synced")

    async def setup_hook(self):
        """Initialize cogs"""

        # Cogs loader
        await cogs_manager(self, "load", self._cogs)
        log.info('Cog List Loaded')
        # Sync application commands & show logging informations
        self.loop.create_task(self.startup())

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner
    
    async def on_command_error(self, ctx, error: commands.CommandError) -> None:
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                log.exception('In %s:', ctx.command.qualified_name, exc_info=original)
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(str(error))