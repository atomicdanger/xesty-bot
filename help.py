import discord
from discord.ext import commands
import asyncio
import typing
from SlashCommands import SlashCore
from Context import SlashContext, ComponentContext
from Messages import ActionRow, Button, SelectMenu, MenuOption
import os
import requests
import spotipy


class Help(commands.Cog):
    token = os.environ['TOKEN']
    application_id = "865841283343450122"
    api_url = f"https://discord.com/api/v9/applications/{application_id}/commands"
    header = {"Authorization": f"Bot {token}"}
    def __init__(self, client):
        self.client = client
        self.request = requests.Session()
        
    # async def interaction_created(self,x):
    #     if x["t"] != "INTERACTION_CREATE":
    #         return
    #     data = x["d"]
    #     if data["type"] ==3:
    #         ctx = ComponentContext(self.client,self.request,data)
    #         if ctx.custom_id =="Avatar":
    #             await self.avatar(ctx)
    #     else:
    #         try:
    #             ctx = SlashContext(self.client,self.request,data)
    #             await SlashCore.run_func(ctx)
    #         except Exception as e:
    #             print(e)
    # async def avatar(self,ctx):
    #     member = await ctx.member()
    #     show_avatar = discord.Embed(
    #         title=f"{member}",
    #         description=
    #         f"[JPEG]({member.avatar_url_as(static_format='jpeg')}) | [PNG]({member.avatar_url_as(static_format='png')})",
    #         color=3092790)
    #     show_avatar.set_author(
    #         name="Avatar")
    #     show_avatar.set_image(
    #         url=f"{member.avatar_url_as(static_format='png', size=2048)}")
    #     await ctx.callback(embed=show_avatar)
    # @commands.command(aliases=["h"])
    # async def help(self, ctx):
    #     button = Button(label="Avatar", custom_id="Avatar",style=3)
    #     button1 = Button(label="Server Invite", url="https://discord.gg/roast",style=5)
    #     ar = ActionRow([button,button1])
    #     h = discord.Embed(
    #         title=f"Help",
    #         color=3092790)
    #     h.set_author(
    #         name=f"{ctx.guild.name}",
    #         icon_url=f"{ctx.guild.icon_url}")
        
    #     h.set_thumbnail(
    #         url=ctx.guild.icon_url)
    #     h.add_field(name="Avatar", value="Shows the avatar of the mentioned user\n`c!av [user]`",inline=False)
    #     # h.add_field(name="Blacklist", value="Blacklists the user or the name\n`ob!blacklist [user/name] [reason](optional)`",inline=False)
    #     # h.add_field(name="Verified Blacklist", value="Blacklists the verified user or the name\n`ob!blacklist-verified [user/name] [reason](optional)`",inline=False)
    #     # h.add_field(name="Verified Troll Blacklist", value="Blacklists the verified user or the name as a troll\n`ob!blacklist-troll [user/name] [reason](optional)`",inline=False)
    #     message = {
    #             "embeds": [h.to_dict()],
    #                 "components": [ar.to_dict()]}
    #     url = f"https://discord.com/api/v9/channels/{ctx.channel.id}/messages"
    #     requests.post(url, headers=self.header,json=message)
    # @commands.command()
    # async def test(self, ctx):
    #     guild = self.client.get_guild(944557938914263060)
    #     red = await guild.fetch_emoji(957928671140794428)
    #     pink = await guild.fetch_emoji(957928823045898250)
    #     violet = await guild.fetch_emoji(957929187426050120)
    #     blurple = await guild.fetch_emoji(957929420239278100)
    #     purple = await guild.fetch_emoji(957929578284875816)
    #     aqua = await guild.fetch_emoji(957930021140434954)
    #     blue = await guild.fetch_emoji(957929698103558144)
    #     yellow = await guild.fetch_emoji(957929850088337449)
    #     green = await guild.fetch_emoji(957930149502910474)
    #     black = await guild.fetch_emoji(957930259498557471)

    #     redr = ctx.guild.get_role(910536796369207346)
    #     pinkr = ctx.guild.get_role(910535886050054184)
    #     violetr = ctx.guild.get_role(910539541629272065)
    #     blurpler = ctx.guild.get_role(910539546675007520)
    #     purpler = ctx.guild.get_role(923911609477369867)
    #     aquar = ctx.guild.get_role(910536794469203989)
    #     bluer = ctx.guild.get_role(915238244487135303)
    #     yellowr = ctx.guild.get_role(915237934976892959)
    #     greenr = ctx.guild.get_role(910536797296148540)
    #     blackr = ctx.guild.get_role(915237937241792582)
        
    #     button = Button(emoji=red, custom_id="cred")
    #     button2 = Button(emoji=pink, custom_id="cpink")
    #     button3 = Button(emoji=violet, custom_id="cviolet")
    #     button4 = Button(emoji=blurple, custom_id="cblurple")
    #     button5 = Button(emoji=purple, custom_id="cpurple")
        
    #     button6 = Button(emoji=aqua, custom_id="caqua")
    #     button7 = Button(emoji=blue, custom_id="cblue")
    #     button8 = Button(emoji=yellow, custom_id="cyellow")
    #     button9 = Button(emoji=green, custom_id="cgreen")
    #     button10 = Button(emoji=black, custom_id="cblack")
        
    #     # button1 = Button(label="Server Invite", url="https://discord.gg/roast",style=5)
    #     ar = ActionRow([button,button2,button3,button4,button5])
    #     ar1 = ActionRow([button6,button7,button8,button9,button10])
        
    #     h = discord.Embed(
    #         title=f"Color Roles",
    #         description=f"{red} {redr.name}\n{pink} {pinkr.name}\n{violet} {violetr.name}\n{blurple} {blurpler.name}\n{purple} {purpler.name}\n{aqua} {aquar.name}\n{blue} {bluer.name}\n{yellow} {yellowr.name}\n{green} {greenr.name}\n{black} {blackr.name}",
    #         color=3092790)
        
    #     h.set_image(url="https://i.imgur.com/8JT8UQG.png")
    #     # h.add_field(name="Avatar", value="Shows the avatar of the mentioned user\n`c!av [user]`",inline=False)
    #     # h.add_field(name="Blacklist", value="Blacklists the user or the name\n`ob!blacklist [user/name] [reason](optional)`",inline=False)
    #     # h.add_field(name="Verified Blacklist", value="Blacklists the verified user or the name\n`ob!blacklist-verified [user/name] [reason](optional)`",inline=False)
    #     # h.add_field(name="Verified Troll Blacklist", value="Blacklists the verified user or the name as a troll\n`ob!blacklist-troll [user/name] [reason](optional)`",inline=False)
    #     message = {
    #             "embeds": [h.to_dict()],
    #                 "components": [ar.to_dict(),ar1.to_dict()]}
    #     url = f"https://discord.com/api/v9/channels/{ctx.channel.id}/messages"
    #     embed=discord.Embed(color=3092790)
    #     embed.set_image(
    #         url="https://i.imgur.com/ps49YeA.gif")
    #     await ctx.send(embed=embed)
    #     requests.post(url, headers=self.header,json=message)

    # @commands.command()
    # async def dmall(self,ctx):
    #     members = ctx.guild.members
    #     embed = discord.Embed(
    #         title="Shop",
    #         color=3092790
    #     )
    #     embed.add_field(name="<a:diamond:959758570956673024> $100",value=f"・**Type:** Nitro/Paypal/Giftcard\n```Credits Required: 100,000```",inline=False)
    #     embed.add_field(name="<a:diamond:959758570956673024> $50",value=f"・**Type:** Nitro/Paypal/Giftcard\n```Credits Required: 50,000```",inline=False)
    #     embed.add_field(name="<a:diamond:959758570956673024> $10",value=f"・**Type:** Nitro/Paypal/Giftcard\n```Credits Required: 10,000```",inline=False)
    #     embed.add_field(name="<a:diamond:959758570956673024> Custom Role",value=f"・**Type:** Discord Role\n・**Validity:** Permanent```Credits Required: 10,000```",inline=False)
    #     embed.add_field(name="<a:diamond:959758570956673024> $5",value=f"・**Type:** Nitro/Paypal/Giftcard\n```Credits Required: 5,000```",inline=False)
    #     embed.add_field(name="<a:diamond:959758570956673024> Custom Role",value=f"・**Type:** Discord Role\n・**Validity:** One month```Credits Required: 1,000```",inline=False)
    #     # embed.set_author(name="Shop")
    #     embed.set_image(url="https://media.giphy.com/media/cx2ff3RehGgXQ06H41/giphy.gif")
    #     c = "<:copper:924932585048641556> Starting soon, we implemented a new system where you can earn rewards just by being active in chat and channels or inviting people. These rewards can range from nitro, gift cards, Xbox game pass, Itunes, steam, etc.\ndiscord.gg/xesty"
        
    #     for member in members:
    #         if member.bot:
    #             continue
            
    #         try:
    #             await member.send(embed=embed)
    #             print(member.name)
    #         except Exception as e:
    #             print(e)
    #             continue
    #     await ctx.send("Done")
    # @commands.command()
    # async def removeall(self,ctx):
    #     uv = ctx.guild.get_role(923205585451749377)
    #     loved = ctx.guild.get_role(910541065071779922)
    #     sr = ctx.guild.get_role(912964821169872916)
    #     tl= ctx.guild.get_role(912963843146285066)
    #     dr= ctx.guild.get_role(913720141014007828)
    #     for member in uv.members:
    #         roles = member.roles
    #         if not loved in roles:
    #             await member.add_roles(loved)
    #         if not sr in roles:
    #             await member.add_roles(sr)
    #         if not tl in roles:
    #             await member.add_roles(tl)
    #         if not dr in roles:
    #             await member.add_roles(dr)
                
    #         await member.remove_roles(uv)
    #     await ctx.send("done")

    # @commands.command()
    # async def emojis(self,ctx):
    #     guild = self.client.get_guild(910395389172121600)
    #     for emoji in guild.emojis:
    #         await ctx.send(emoji)
    

def setup(client):
    client.add_cog(Help(client))