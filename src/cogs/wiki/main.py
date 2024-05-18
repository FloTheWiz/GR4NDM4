import re
import requests 

from Levenshtein import distance
from bs4 import BeautifulSoup
import discord
from discord.ext import commands

from core.wikihelper import get_search_results, link_to_url, check_site_validity, check_for_tags, strip_tags, find_search_exists, find_did_you_mean, fetch_first_result, link_to_search
from cogs.wiki.views import TagView, DeleteButton, LinkButton
# freshly baked
# I could fetch this as a Role and check it against the user.roles
# but id is the lazy way
#LazyDevs
MIN_ROLE = 1169378393096196237

async def setup(client):
	await client.add_cog(Wiki(client))

class Wiki(commands.Cog):
    def __init__(self, client):
        self.client = client 
        self.wiki_json = {'allowed_channels':[1176899203084075131],'custom_commands':{'365':'https://pastebin.com/8W6i6PFr'}}
        
        
    @commands.Cog.listener()
    async def on_message(self, message):
        
        # first we check we SHOULD check this message should be "seen"
        if message.channel.id not in self.wiki_json['allowed_channels']:
            return ## Message is not in CC channels, discard. 
            
        # Fuck it, we hardcode role IDs. 
        if not any(role.id == MIN_ROLE for role in message.author.roles):
            return ## user can't use the bot until freshly baked 
            
        tag = check_for_tags(str(message.content)) # spooky regex

        if not(tag):
            return   ## Alas, just a normal message 
        
        # We got a tag ladies and gentlemen.
        view = discord.ui.View(timeout=None)
        view.add_item(DeleteButton())  
        # first we strip the fluff
        tag = strip_tags(tag)
        # Check the tag for gross shit
        if '@' in tag:
             return 
        
        # I'm sorry
        for cmd in self.wiki_json['custom_commands'].keys():
                if cmd.lower() == tag.lower(): 
                    # Not worth making a whole ass view in view.py for this
                    await message.channel.send(self.wiki_json['custom_commands'][cmd], view=view)
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
            return 
        
        else: 
            # Uh oh, someone borked a tag. 
            # Search it, and parse the html
            search_link = link_to_search(tag)
            search_data = requests.get(search_link)
            search_soup = BeautifulSoup(search_data.text, 'html.parser')
            first_result = fetch_first_result(search_soup)
            if first_result:
                url = 'https://cookieclicker.wiki.gg/' + first_result['href']
                url_title = first_result['title']
                if distance(url_title, tag) < 4: # It's probably that.
                     await message.channel.send(url,view=view)
                     return
            else: 
                print(search_data.history)
                # We got NO results
                # We could probably make this smarter by caching the wiki or some shit?
                await message.add_reaction('❓')
                return
            # Magic. 
            search_results = get_search_results(search_soup)
            print(search_results)
            ask = await message.channel.send(str(message.author.mention) + ' Did you mean: **' + url_title + '**?', view=TagView(url=url,search_results=search_results)) 
            
            
