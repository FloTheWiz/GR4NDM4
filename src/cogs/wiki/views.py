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

class SearchEmbed(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, search_results: list, search_term: str):
        self.search_term = self.search_term
        self.interaction = interaction
        self.search_results = search_results
        self.index = 1
        self.max_pages = self.compute_total_pages(len(search_results), 5)
        super().__init__(timeout=100)
    
    async def make_embed(self, content):
        e = discord.Embed(
            title=f"Search for: {self.search_term}",
            description="",
            color=0xC55050,  # Nice light red
    )
        e.set_author(name=f'GR4NDM4 - {self.interaction.user}',icon_url="https://i.imgur.com/U3Nyus7.gif")
        # Now we need to make the page itself.
        # Oh boy.
        # Name, Description, Link, Data
        for entry in content:
            e.add_field(name=f'**')


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            emb = discord.Embed(
                description=f"Only the author of the command can perform this action.",
                color=16711680
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return False

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1
