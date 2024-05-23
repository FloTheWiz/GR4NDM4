import datetime 
import requests 
import json  

from Levenshtein import distance
from bs4 import BeautifulSoup
import discord
from discord.ext import commands, tasks

from core.wikihelper import get_search_results, link_to_url, check_site_validity, check_for_tags, strip_tags, find_search_exists, find_did_you_mean, link_to_search
from cogs.wiki.views import TagView, DeleteButton, LinkButton
# freshly baked
# I could fetch this as a Role and check it against the user.roles
# but id is the lazy way
#LazyDevs
MIN_ROLE = 1169378393096196237

def save_wiki_json(data):
    with open('Core/data_file.json','w') as write_file:
        json.dump(data, write_file, indent=4)

def load_wiki_json():
    with open('Core/data_file.json','r') as read_file:
        data = json.load(read_file)
    return data


async def setup(client):
	await client.add_cog(Wiki(client))

class Wiki(commands.Cog):
    def __init__(self, client):
        self.client = client 
        self.wiki_json = load_wiki_json()

        self.cd_dict = {"global":0,"msgs":[]}

        self.reduce_cooldown.start()

    @tasks.loop(seconds=1.0)
    async def reduce_cooldown(self):
        if self.cd_dict['global'] > 0:
            print("reducing CD")
            self.cd_dict['global'] -= 1 
        if self.cd_dict['global'] == 0 and len(self.cd_dict['msgs']) > 0:
            for msg in self.cd_dict['msgs']:
                mem= await msg.guild.fetch_member(self.client.user.id)
                await msg.remove_reaction("❌",mem)
                await msg.remove_reaction("⌛",mem)
            self.cd_dict['msgs'] = []

    def cog_unload(self):
        self.reduce_cooldown.cancel()

    @reduce_cooldown.before_loop
    async def before_reduce_cd(self):
        print('waiting for wiki')
        await self.client.wait_until_ready()

    async def can_use_wiki(self, message: discord.Message) -> bool:
        """Checks if the user is in the correct channel + has the correct role
        
        msg- discord message

        Return: bool
        """
        
        # first we check we SHOULD check this message should be "seen"
        if message.channel.id not in self.wiki_json['allowed_channels']:
            return False
            
        # Fuck it, we hardcode role IDs. 
        if not any(role.id == MIN_ROLE for role in message.author.roles):
            return False
        # We can check the timer
        if self.cd_dict['global'] > 0:
             remaining = self.cd_dict["global"]
             # Add them. 
             await message.add_reaction("❌")
             await message.add_reaction("⌛")
             await message.channel.send(f"Sorry, I'm still on cooldown for **{remaining} Seconds**", delete_after=1)
             self.cd_dict['msgs'].append(message)
             return False
        return True 
            

    @commands.hybrid_group(name='customcommand')
    # Empty command for custom command
    # i think, unusable. 
    async def custom_command_parent(self, ctx: commands.Context):
         return
   
   # View Custom Commands
    @custom_command_parent.command(name='view')
    async def view(self, ctx: commands.Context):
        if not ctx.channel.id in self.wiki_json["allowed_channels"]:
              await ctx.send(f'Sorry, Please use this in the correct channel, ie <#{self.wiki_json["allowed_channels"][0]}>')
              return
        msg = ''
        for cmd in self.wiki_json['custom_commands'].keys():
             msg += f'**{cmd}** (_Aliases: {",".join(self.wiki_json["custom_commands"][cmd]["aliases"])}_) \|\| CONTENT: {self.wiki_json["custom_commands"][cmd]["content"]}\n'
        await ctx.send(msg)
    
    @custom_command_parent.command(name="add")
    async def add_custom_command(self, ctx: commands.Context, cmd_name: str, content: str):
        try:
              self.wiki_json['custom_commands'][cmd_name] = {'aliases':[],"content":content}
              save_wiki_json(self.wiki_json)
              await ctx.message.add_reaction('👍')
        except Exception as e:
             await ctx.send(f'Error: {e}', ephemeral=True)


    @custom_command_parent.command(name="addalias")
    async def add_custom_command_alias(self, ctx: commands.Context, cmd_name: str, alias: str):
        try:
              self.wiki_json['custom_commands'][cmd_name]['aliases'].append(alias.lower())
              save_wiki_json(self.wiki_json)
              await ctx.message.add_reaction('👍')
        except Exception as e:
             await ctx.send(f'Error: {e}', ephemeral=True)



    @commands.Cog.listener()
    async def on_message(self, message):

        

        tag = check_for_tags(str(message.content)) # spooky regex

        if not(tag):
            return   ## Alas, just a normal message 
        if '@' in tag: # someone tryin' to ping someone. We don't stand for it at all. There's no pages with @. 
             return 
        if '[[' in tag:
             # We haven't stripped it properly apparently
             tag = str(message.content).split('[[')[1]
             if ']]' in tag:
                  tag = tag.split(']]')[0]

        if not await self.can_use_wiki(message):
             return 
        # We got a tag ladies and gentlemen.
        view = discord.ui.View(timeout=None)
        view.add_item(DeleteButton())  
            
 
        # Custom Commands: 
        for cmd in self.wiki_json['custom_commands'].keys():
                if cmd.lower() == tag.lower() or tag.lower() in self.wiki_json['custom_commands'][cmd]['aliases']: 
                    # Not worth making a whole ass view in view.py for this
                    await message.channel.send(self.wiki_json['custom_commands'][cmd]['content'], view=view)
                    self.cd_dict['global'] = 5
                    return 
                
        if not(any(letter.isalpha() for letter in tag)):
             return
        link = link_to_url(tag)
        c = check_site_validity(link)
        if c == 'Cloudflare':
             # We need to account for this 
             view.add_item(LinkButton(link))
             await message.channel.send('Sorry, The Wiki appears to be down, if you want, I can link directly to that page?', view=view)
        elif c == True: 
            # If it works, then it works. 
            # I know this is reusing code from above, but it's preferable to making a new one every time someone tags 
            # Fixing this PEP-8 'bug' would require a move around. 
            # Welcome to fix. 


            await message.channel.send(link,view=view)
            await message.add_reaction('👍')
            self.cd_dict['global'] = 5
            return 
        
        else: 
            # Uh oh, someone borked a tag. 
            # Search it, and parse the html
            search_link = link_to_search(tag)
            search_data = requests.get(search_link)
            search_soup = BeautifulSoup(search_data.text, 'html.parser')
            search_results = get_search_results(search_soup)
            if search_results:
                first_result = search_results[0]
                url = first_result['url']
                url_title = first_result['name']
                if distance(url_title, tag) < len(tag) // 2 -1: # It's probably that.
                        await message.channel.send(url,view=view)
                        return
            else: 
                # We got NO results
                # We could probably make this smarter by caching the wiki or some shit?
                await message.add_reaction('❓')
                return
            # Magic. 
            
            ask = await message.channel.send(str(message.author.mention) + ' Did you mean: **' + url_title + '**?', view=TagView(url=url,search_results=search_results)) 
            self.cd_dict['global'] = 5
            
