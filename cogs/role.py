import discord
from discord.ext import commands
import os
import requests
from discord.utils import get
from discord.ui import Button, View, TextInput, Modal, Select
import json

class Role(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.roles=[924928169717411870,910852917131632641,958966114229051412]
        self.colors=[913720141014007828,976299429768359976, 976299434419814431, 976299433706790953, 976299432561754132, 976299431102140459, 976299428765925446, 976299425116860416, 976299424286400512, 976299423258771527, 976299427021078598, 976299426073182238, 976299427868327936, 976299416711495701, 976299415759372388, 976299414677233716, 976299413121155152, 976299412269719583, 976299413892898886, 976299410038349824, 976299408062820392, 976299411162431529, 976299407257514044, 976299406276063263, 976299408842973194, 976299405336543322, 976299404468289596, 976299403616858112, 976299401851043860, 976299401028968498, 923911609477369867, 976299399141552138, 976299399862968341, 976299397262499850, 976299395047915570, 976299396067115078, 910536797296148540, 976299421560090654, 976299418573746236, 976299419127386215, 976299417592279040, 964199099840753665, 964198610684227624, 976299394267742249, 976299391314976808, 976299388563505183, 976299390174121984, 976299389352046602, 910536796369207346, 976299383312252990, 976299386944487444, 976299382347558942, 976299387762401300, 976299384708947999, 915238244487135303]
        self.orders=["・White・","・Blue・","・Purple・","・Pink・","・Green・","・Yellow・","・Orange・","・Red・","・Black・","・Default・"]
        self.order=["White","Blue","Purple","Pink","Green","Yellow","Orange","Red","Black"]
        
    @commands.Cog.listener()
    async def on_interaction(self,i:discord.Interaction):
        if i.channel_id==923924855747936257:
            await self.give_color(i)
    async def give_color(self,i:discord.Interaction):
        data=i.data
        role_id = int(data["values"][0])
        eligible=None
        r = i.guild.get_role(role_id)
        for role in i.user.roles:
            if r==role:
                await i.user.remove_roles(role)
                default = i.guild.get_role(913720141014007828)
                await i.user.add_roles(default)
                await i.response.send_message(f"Changed your color role to {default.mention}!",ephemeral=True)
                return
            if role.id in self.colors:
                await i.user.remove_roles(role)
            if role.id in self.roles:
                eligible = True
        if eligible:
            await i.user.add_roles(r)#its not flags this is the old code
            await i.response.send_message(f"Changed your color role to {r.mention}!",ephemeral=True)
            return
        await i.response.send_message(f"You gotta be level +5 to access color roles!",ephemeral=True)
    @commands.command()
    async def embeds(self,ctx):
        guild = self.client.get_guild(961171937927766056)
        g2 = self.client.get_guild(944557938914263060)
        emojis = guild.emojis
        emojis2 = g2.emojis
        await self.main(ctx)

        filename = 'roles.json'
        with open(filename, 'r') as f:
            data = json.load(f)
        for order in self.order[::-1]:
            embed= discord.Embed(color= 3092790)
            emoji = get(emojis2,name=order)
            embed.set_author(name=f"5.0 Shades of {order}")
            embed.set_thumbnail(url=emoji.url)
            embed.set_image(url=str(data[order]["url"]))
            embed.description=""
            view = View()
            selectmenu = Select(custom_id="color_roles",placeholder="Pick a color from the menu")
            for id in data[order]["shades"][::-1]:
                role = ctx.guild.get_role(id)#lemme see how to make selectmenus wait
                emoji = get(emojis,name=role.name.replace(" ","_"))
                embed.description+=f"{emoji} {role.mention}\n"#yeah we can
                selectmenu.add_option(label=role.name,value=str(role.id),emoji=emoji)
            view.add_item(selectmenu)
            
            await ctx.send(embed=embed,view=view)
    @commands.command()
    async def main(self,ctx):
        guild = self.client.get_guild(944557938914263060)
        emojis = guild.emojis
        main = self.orders
        embed= discord.Embed(color= 3092790)
        
        embed.set_author(name=f"Shades of Xesty")
        embed.set_thumbnail(url="https://i.imgur.com/kJu2vK1.png")
        #add the xesty server icon in the image wouldnt that be too big? and also I was gonna change it[, check discord
        embed.set_image(url="https://cdn.discordapp.com/attachments/928234533092995072/978979613529227334/unknown.png")
        embed.description=""
        view = View()
        selectmenu = Select(custom_id="color_roles",placeholder="Pick a color from the menu")
        for id in main:
            role = get(ctx.guild.roles,name=id)
            emoji = get(emojis,name=role.name[1:-1].replace(" ", "_"))
            embed.description+=f"{emoji} {role.mention}\n"
            selectmenu.add_option(label=role.name,value=str(role.id),emoji=emoji)
        view.add_item(selectmenu)
        await ctx.send(embed=embed,view=view)
        
async def setup(client):
    await client.add_cog(Role(client))