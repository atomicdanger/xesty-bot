import discord
from discord.ext import commands
import datetime
import requests
import os
import typing
from discord.ui import Button, View, TextInput, Modal
from discord import app_commands


class Moderation(commands.Cog):
    token = os.environ['TOKEN']
    application_id = "865841283343450122"
    api_url = f"https://discord.com/api/v9/applications/{application_id}/commands"
    header = {"Authorization": f"Bot {token}"}
    def __init__(self, client):
        self.client = client
        self.words=["nigga","nigger","fag","blackie","kys"]
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.bot:
            return
        if not message.content:
            return
        if message.channel.id ==965225348059000852:
            await message.delete()
            return
        for word in self.words:
            if word.lower() in message.content.lower():
                await message.delete()
                amount=datetime.timedelta(seconds=100)
                try:
                    await message.author.timeout(until=amount,reason="Automod")
                except:
                    pass
                await message.channel.send(f"Watch your language, {message.author.mention}!",delete_after=3)
                break
                break
    def royalty():
        def predicate(ctx):
            royalty = ctx.guild.get_role(910479865126457384)
            if royalty in ctx.author.roles:
                return True
        return commands.check(predicate)

    def admin():
        def predicate(ctx):
            admin = ctx.guild.get_role(924225886771871805)
            if admin in ctx.author.roles:
                return True
        return commands.check(predicate)

    def mod():
        def predicate(ctx):
            mod = ctx.guild.get_role(910536241345351681)
            if mod in ctx.author.roles:
                return True
        return commands.check(predicate)

    def staff():
        def predicate(ctx):
            staff=ctx.guild.get_role(910536793500315778)
            if staff in ctx.author.roles:
                return True
        return commands.check(predicate)

    def helper():
        def predicate(ctx):
            helper=ctx.guild.get_role(910536795404525579)
            if helper in ctx.author.roles:
                return True
        return commands.check(predicate)

    def ban_members():
        def predicate(ctx):
            role=ctx.guild.get_role(912974280088748112)
            if role in ctx.author.roles:
                return True
        return commands.check(predicate)

    def kick_members():
        def predicate(ctx):
            role=ctx.guild.get_role(912974226225508373)
            if role in ctx.author.roles:
                return True
        return commands.check(predicate)

    def timeout_members():
        def predicate(ctx):
            role=ctx.guild.get_role(924227421698424893)
            if role in ctx.author.roles:
                return True
        return commands.check(predicate)

    @commands.command()
    @commands.check_any(staff(),mod(),admin(),royalty(),kick_members())
    async def kick(self, ctx, member: discord.Member=None, *, reason:str="No reason provided"):
        author = ctx.message.author
        embed= discord.Embed(color=3092790)
        embed.set_image(url="https://i.imgur.com/8JT8UQG.png")
        embed.set_author(name=str(author),icon_url=str(author.display_avatar))
        if not member:
            embed.title="Failed"
            embed.description=f'Please provide an user to {ctx.command.qualified_name}.\nFormat: x!{ctx.command.qualified_name} [mention or user_id] [reason (optional)]'
            return await ctx.send(embed=embed)
        if member.top_role >= author.top_role:
            embed.title="Failed"
            embed.description=f"Couldn't {ctx.command.qualified_name} the user!\nReason: The user is same or higher ranked than you in the role hierarchy."
            return await ctx.send(embed=embed)
        reason = f"Kicked by {author}: " + reason
        embed.set_footer(text=reason)
        logs = ctx.guild.get_channel(977873814635560980)
        await member.kick(reason=reason)
        embed.title="Kicked"
        embed.description=f"Successfully kicked {member.mention} `({member.id})`"
        await ctx.channel.send(embed=embed)
        embed.description+=f"\n**Moderator: {author.mention}**"
        await logs.send(embed=embed)
        
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.CheckAnyFailure):
            await ctx.send("You don't have the perms to use the command!")


    @commands.command()
    @commands.check_any(mod(),admin(),royalty(),ban_members())
    async def ban(self, ctx, member: typing.Union[discord.Member,discord.User]=None, *, reason:str="No reason provided"):
        author = ctx.message.author
        guild=ctx.guild
        embed= discord.Embed(color=3092790)
        embed.set_image(url="https://i.imgur.com/8JT8UQG.png")
        embed.set_author(name=str(author),icon_url=str(author.display_avatar))
        if not member:
            embed.title="Failed"
            embed.description=f'Please provide an user to {ctx.command.qualified_name}.\nFormat: x!{ctx.command.qualified_name} [mention or user_id] [reason (optional)]'
            return await ctx.send(embed=embed)
        if member.top_role >= author.top_role:
            embed.title="Failed"
            embed.description=f"Couldn't {ctx.command.qualified_name} the user!\nReason: The user is same or higher ranked than you in the role hierarchy."
            return await ctx.send(embed=embed)
        reason = f"Banned by {author}: " + reason
        embed.set_footer(text=reason)
        logs = ctx.guild.get_channel(977873814635560980)
        
        await guild.ban(member,reason=reason,delete_message_days=0)
        embed.title="Banned"
        embed.description=f"Successfully banned {member.mention} `({member.id})`"
        await ctx.channel.send(embed=embed)
        embed.description+=f"\n**Moderator: {author.mention}**"
        await logs.send(embed=embed)
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.CheckAnyFailure):
            await ctx.send("You don't have the perms to use the command!")


    @commands.command()
    @commands.check_any(mod(),admin(),royalty(),ban_members())
    async def unban(self, ctx, member: discord.User=None,*,reason="No reason provided"):
        try:
            author = ctx.message.author
            guild=ctx.guild
            embed= discord.Embed(color=3092790)
            embed.set_image(url="https://i.imgur.com/8JT8UQG.png")
            embed.set_author(name=str(author),icon_url=str(author.display_avatar))
            if not member:
                embed.title="Failed"
                embed.description=f'Please provide an user to {ctx.command.qualified_name}.\nFormat: x!{ctx.command.qualified_name} [mention or user_id] [reason (optional)]'
                return await ctx.send(embed=embed)
            
            reason = f"Unbanned by {author}: " + reason
            embed.set_footer(text=reason)
            logs = ctx.guild.get_channel(977873814635560980)
            await guild.unban(member,reason=reason)
            embed.title="Unbanned"
            embed.description=f"Successfully unbanned {member.mention} `({member.id})`"
            await ctx.channel.send(embed=embed)
            embed.description+=f"\n**Moderator: {author.mention}**"
            await logs.send(embed=embed)
        except Exception as e:
            await ctx.send(e)
    @unban.error
    async def unban_error(self,ctx, error):
        if isinstance(error, commands.CheckAnyFailure):
            await ctx.send("You don't have the perms to use the command!")
    
    @commands.check_any(helper(),staff(),mod(),admin(),royalty(),timeout_members())
    @commands.command(aliases=["mute"])
    async def timeout(self,ctx,member:discord.Member=None,x:typing.Union[int,str]="5m",*,reason:str="No reason provided"):
        author = ctx.message.author
        embed= discord.Embed(color=3092790)
        embed.set_image(url="https://i.imgur.com/8JT8UQG.png")
        embed.set_author(name=str(author),icon_url=str(author.display_avatar))
        if not member:
            embed.title="Failed"
            embed.description=f'Please provide an user to {ctx.command.qualified_name}.\nFormat: x!{ctx.command.qualified_name} [mention or user_id] [time (`30m/30`)] [reason (optional)]'
            return await ctx.send(embed=embed)
        if member.top_role >= author.top_role:
            embed.title="Failed"
            embed.description=f"Couldn't {ctx.command.qualified_name} the user!\nReason: The user is same or higher ranked than you in the role hierarchy."
            return await ctx.send(embed=embed)
        if member.guild_permissions.administrator:
            embed.title="Failed"
            embed.description=f"Couldn't {ctx.command.qualified_name} the user!\nReason: The user has adminstrator"
            return await ctx.send(embed=embed)
        if isinstance(x,int):
            await ctx.send("entered")
            x= str(x)+"m"
        time_convert = {"s":1, "m":60, "h":3600,"d":86400}
        try:
            tempmute= int(x[:-1]) * time_convert[x[-1]]
        except:
            embed.title="Failed"
            embed.description=f'Please provide the amount of time in proper format.\nFormat: x!{ctx.command.qualified_name} [mention or user_id] [time (`30m/30`)] [reason (optional)]'
            return await ctx.send(embed=embed)
        if tempmute >=2419200:
            tempmute= 2419199
            x = "28d"
        amount = datetime.timedelta(seconds=int(tempmute))
        reason = f"Timed out by {author}: " + reason
        embed.set_footer(text=reason)
        logs = ctx.guild.get_channel(977873814635560980)
        try:
            await member.timeout(amount,reason=reason)
            embed.title="Timed out"
            embed.description=f"Successfully timed out {member.mention} `({member.id})` for {x}"
            await ctx.channel.send(embed=embed)
            embed.description+=f"\n**Moderator: {author.mention}**"
            await logs.send(embed=embed)
        except Exception as e:
            embed.title="Failed"
            embed.description=f"```py\n{e}```"
            return await ctx.send(embed=embed)
    @timeout.error
    async def timeout_error(self,ctx, error):
        if isinstance(error, commands.CheckAnyFailure):
            await ctx.send("You don't have the perms to use the command!")

    @commands.command(aliases=["unmute"])
    async def untimeout(self,ctx,member:discord.Member=None,*,reason="No reason provided"):
        author = ctx.message.author
        embed= discord.Embed(color=3092790)
        embed.set_image(url="https://i.imgur.com/8JT8UQG.png")
        embed.set_author(name=str(author),icon_url=str(author.display_avatar))
        if not member:
            embed.title="Failed"
            embed.description=f'Please provide an user to {ctx.command.qualified_name}.\nFormat: x!{ctx.command.qualified_name} [mention or user_id] [reason (optional)]'
            return await ctx.send(embed=embed)
        if member.top_role >= author.top_role:
            embed.title="Failed"
            embed.description=f"Couldn't {ctx.command.qualified_name} the user!\nReason: The user is same or higher ranked than you in the role hierarchy."
            return await ctx.send(embed=embed)
        reason = f"Untimed out by {author}: " + reason
        embed.set_footer(text=reason)
        logs = ctx.guild.get_channel(977873814635560980)
        try:
            await member.timeout(None,reason=reason)
            embed.title="Untimed out"
            embed.description=f"Successfully untimed out {member.mention} `({member.id})`"
            await ctx.channel.send(embed=embed)
            embed.description+=f"\n**Moderator: {author.mention}**"
            await logs.send(embed=embed)
        except Exception as e:
            embed.title="Failed"
            embed.description=f"```py\n{e}```"
            return await ctx.send(embed=embed)
    @untimeout.error
    async def untimeout_error(self,ctx, error):
        if isinstance(error, commands.CheckAnyFailure):
            await ctx.send("You don't have the perms to use the command!")

    @commands.command()
    async def test(self,ctx):
        for command in self.client.tree.walk_commands:
            await ctx.send(command)


async def setup(client):
    await client.add_cog(Moderation(client))