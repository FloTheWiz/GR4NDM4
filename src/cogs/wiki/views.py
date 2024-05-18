import discord
# Search Embed. 
class DeleteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Delete", style=discord.ButtonStyle.red, emoji="🗑️")
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=':)',delete_after=0.5)


class LinkButton(discord.ui.Button):
    def __init__(self, link):
        super().__init__(label='Link', style=discord.ButtonStyle.green, emoji="✔️")
        self.link = link
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=self.link) 
        
class SearchSelect(discord.ui.Select):
    def __init__(self, values):
        numbers = ['0️⃣','1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']
        options = [] 
        for i, v in enumerate(values):
            print(i, v)
            options.append(discord.SelectOption(label=v['name'], description=v['description'],emoji=numbers[i]))
        super().__init__(placeholder='Search 🔎', min_values=0, max_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        # User selects a search option
        await interaction.response.send_message(f'You Selected: {self.values[0]}', ephemeral=True) # 

        return

class TagView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, url, search_results):
        super().__init__()
        self.add_item(LinkButton(url))
        self.add_item(DeleteButton())
        self.add_item(SearchSelect(search_results))
        print('Setup Tagview')
