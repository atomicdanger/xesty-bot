import discord
from discord.ext import commands
import os
from discord.ui import Button, View, TextInput, Modal, Select
from random import choice
import string

class Welcome(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.Cog.listener()
    async def on_interaction(self,i:discord.Interaction):
        data = i.data
        method = data["custom_id"]
        data=await self.client.config.find_one({"_id":"config"})
        if method == data["verification"]["key"]:
            await self.verify(i)
    async def Gen(self,length=15, chars=string.ascii_letters + string.digits):
        return ''.join([choice(chars) for i in range(length)])
    @commands.command()
    async def verify1(self,ctx):
        s=await self.Gen()
        view = View(timeout=None)
        button = Button(label="verify ♡", custom_id=s)
        view.add_item(button)
        data=await self.client.config.find_one({"_id":"config"})
        deleted=True
        if not data:
            data = {}
            data["verification"]={}
            data["verification"]["key"]=None
            data["verification"]["message"]=None
        if data["verification"]["message"]:
            try:
                try:
                    if ctx.channel:
                        channel=ctx.channel
                    else:
                        channel = ctx
                except:
                    channel=ctx
                m=await channel.fetch_message(data["verification"]["message"])
                await m.delete()
            except:
                deleted=None
        if deleted:
            embed=discord.Embed(
                title="𝑉𝐸𝑅𝐼𝐹𝐼𝐶𝐴𝑇𝐼𝑂𝑁",
                description="Click on the button down below to get verified\nand gain access to the rest of the server",
    color= 3092790      
            )
            embed.set_image(url="https://i.pinimg.com/originals/4a/70/5e/4a705e028bb9f5d50995e68c791fb10a.gif")
            message = await ctx.send(embed=embed,view=view)
            data["verification"]["key"]=s
            data["verification"]["message"]=message.id
            await self.client.config.replace_one({"_id":"config"},data,True)
    async def verify(self,i):
        member = i.user
        channel = self.client.get_channel(955108971914620979)	
        ctx = self.client.get_channel(983795336407576646)
        r = i.guild.get_role(910541065071779922)
        if r in member.roles:
            await i.response.send_message(f"You already are verified! Visit {channel.mention} to start chatting.",ephemeral=True)
            return
        uv= i.guild.get_role(991537153010053120)
        await member.remove_roles(uv)
        await i.response.send_message(f"You have been verified! Visit {channel.mention} to start chatting.",ephemeral=True)
        embed=discord.Embed(
            title= "Welcome to Xesty!",
            description = f'''𝙀𝙣𝙟𝙤𝙮 𝙮𝙤𝙪𝙧 𝙨𝙩𝙖𝙮 {member.mention}
<:copper:924932585048641556> Talk and earn credits!
<:copper:924932585048641556> Check for giveaways!
<:copper:924932585048641556> Boost for special perks!''',
color= 3092790
        ) 
        embed.set_author(name="Xesty", icon_url=str(member.guild.icon))
        embed.set_thumbnail(url=str(member.display_avatar))
        embed.set_image(url="https://i.imgur.com/8JT8UQG.png")
        
        await channel.send(embed=embed)
        await channel.send(f"Welcome {member.mention}!")
        roles =[910541065071779922,912963843146285066,912964821169872916,913720141014007828]
        for role in roles:
            v= i.guild.get_role(role)
            await member.add_roles(v)
        await self.verify1(ctx)
    @commands.command()
    async def uv(self,ctx):
        uv= ctx.guild.get_role(991537153010053120)
        channels=ctx.guild.channels
        channels.extend(ctx.guild.categories) 
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel= False
        for channel in channels: 
            await channel.set_permissions(uv,overwrite=overwrite)
        await ctx.send("done")
async def setup(client):
    await client.add_cog(Welcome(client))