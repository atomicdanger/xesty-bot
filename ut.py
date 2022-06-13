import discord
from discord.ext import commands
import asyncio
import typing
from Messages import ActionRow, Button
import requests
import os
import json
class Utility(commands.Cog):
    token = os.environ['TOKEN']
    application_id = "865841283343450122"
    api_url = f"https://discord.com/api/v9/applications/{application_id}/commands"
    header = {"Authorization": f"Bot {token}"}
    def __init__(self, client):
        self.client = client
        self.snipes = {}
    
    # @commands.command(aliases=["inv"])
    # async def invite(self,ctx):
    #     await ctx.send("discord.gg/roast")
    # @commands.Cog.listener()
    # async def on_voice_state_update(self,member, before, after):
    # 	if not before.channel.category_id == 819744518530007060:
    # 		return
    # 	if before.channel.id == 896210278235111504:
    # 		return
    # 	if len(before.channel.members) == 0:
    # 		await before.channel.delete(reason="All users left (Evented Ended)")
    # @commands.Cog.listener()
    # async def on_raw_message_delete(self,payload):
    # 	message = payload.cached_message
    # 	if message:
    # 		self.snipes[message.channel.id] = message
    # @commands.Cog.listener()	
    # async def on_message(self,message):
    # 	if "pic perm" in message.content and not message.author == message.guild.me:
    # 		await message.channel.send("`gg/haunt` in yo status for pic perms bozo")
    # @commands.Cog.listener()
    # async def on_member_update(self,b,a):
    # 	if b.id==924264692350873610:
    # 		c = await self.client.fetch_channel(910481152513540146)
    # 		url = f"https://discord.com/api/v9/guilds/{a.guild.id}/members/{a.id}"
    # 		# json = {"communication_disabled_until":iso}
    # 		r= requests.get(url, headers=self.header)
    # 		t = r.json()["communication_disabled_until"]
    # 		if not t:
    # 			t = "Timeout removed"		
    # 		await c.send(t)
        # h = b.guild.get_role(902239703678451812)
        # regex = "gg/wraith"
        # if b.activity == a.activity:
        # 	return 
        # if h in b.roles:
        # 	# print(a.status)
        # 	if str(a.status) == "offline":
        # 		await a.remove_roles(h)
        # 	elif a.activity:
        # 		if not regex in a.activity.name:
        # 			await a.remove_roles(h)
        # 	else:
        # 		await a.remove_roles(h)

        # if type(a.activity) == discord.CustomActivity:
        # 	if regex in str(a.activity):
        # 		await a.add_roles(h)
    @commands.command()
    @commands.has_role(896199809457860628)
    async def host(self,ctx,name=None,limit= 99):
        try:
            host = ctx.author
            if not name:
                name = f"{host.name}'s Event"
            category = discord.utils.get(ctx.guild.categories, id=819744518530007060)
            overwrite = {host:discord.PermissionOverwrite(view_channel=True,manage_channels=True,manage_permissions=True,create_instant_invite=True, connect=True,mute_members=True,move_members=True,priority_speaker=True,speak=True,stream=True,use_voice_activation=True,deafen_members=True)}			
            channel = await ctx.guild.create_voice_channel(name=name,overwrites=overwrite,category=category,bitrate=64000,user_limit=limit)
            invite = await channel.create_invite()
            embed = discord.Embed(
                title= "Event Channel created",
                description=f"Channel name: {name}\nHost: {host.mention}\nUser Limit: {limit}\n Click the button below to join the channel!",
            color=3092790)
            button = Button(label="Click me!",style=5,url=invite.url)
            ar = ActionRow([button])
            message = {
                "embeds":[embed.to_dict()],
                "components": [ar.to_dict()]}
            url = f"https://discord.com/api/v8/channels/{ctx.channel.id}/messages"
            requests.post(url, headers=self.header,json=message)
        except Exception as e:
            await ctx.send(e)
    @host.error
    async def host_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.channel.send("Sorry, You are not allowed to use this command. You need `Host` Role to use the command.")
    @commands.command(aliases=["avatar","pfp"])
    async def av(self, ctx, *, member: discord.Member = None):
        if not member:
            member = ctx.author
        show_avatar = discord.Embed(
            title=f"{member}",
            description=
            f"[JPEG]({member.avatar_url_as(static_format='jpeg')}) | [PNG]({member.avatar_url_as(static_format='png')})",
            color=3092790)
        show_avatar.set_author(
            name="Avatar")
        show_avatar.set_image(
            url=f"{member.avatar_url_as(static_format='png', size=2048)}")
        await ctx.send(embed=show_avatar)
    @commands.command(aliases=["give-role","grole"])
    @commands.has_permissions(administrator=True)
    async def giverole(self, ctx, member: discord.Member,roles:commands.Greedy[discord.Role]):
        # await ctx.send(type(roles))
        add_roles = []
        # unable_role = []
        try:
            for role in roles:
                if member.top_role > role:
                    await member.add_roles(role)
                    add_roles.append(role)
                else:
                    embed = discord.Embed(
                title = "Unable to add the role",
                description = f"**Target:** {member.mention}\n**Role:** {role.mention}\n**Reason:** The role is above the highest role of the member",
                color=3092790
            )
                    await ctx.send(embed = embed)
            if len(add_roles) > 0:
                rolez = list(map(lambda x: x.mention,add_roles))
                roless = "\n".join(rolez)
                embed = discord.Embed(
                    title = "Roles Added",
                    description = f"**Target:** {member.mention}\n**Roles Added:**\n{roless}",
                    color=3092790
                )
                embed.set_footer(text=f"Requested by {ctx.author}")
                await ctx.send(embed = embed)
        except Exception as e:
            embed = discord.Embed(
                title = "Unable to add the roles",
                description = f"Error:\n```py{e}```",
                color=3092790
            )
            await ctx.send(embed = embed)
    @giverole.error
    async def give_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.channel.send("Sorry, You are not allowed to use this command. You need `Administrator` permission to use the command.")
    @commands.command(aliases=["remove-role","rrole","trole","take-role"])
    @commands.has_permissions(administrator=True)
    async def removerole(self, ctx, member: discord.Member,roles:commands.Greedy[discord.Role]):
        r_roles = []
        try:
            for role in roles:
                if ctx.author.top_role > role:
                    await member.remove_roles(role)
                    r_roles.append(role)
                else:
                    embed = discord.Embed(
                title = "Unable to add the role",
                description = f"**Target:** {member.mention}\n**Role:** {role.mention}\n**Reason:** The role is above your highest role",
                color=3092790
            )
                    await ctx.send(embed = embed)
            if len(r_roles) > 0:			
                rolez = list(map(lambda x: x.mention,r_roles))
                roless = "\n".join(rolez)
                embed = discord.Embed(
                    title = "Roles Removed",
                    description = f"**Target:** {member.mention}\n**Roles Removed:**\n{roless}",
                    color=3092790
                )
                embed.set_footer(text=f"Requested by {ctx.author}")
                await ctx.send(embed = embed)
        except Exception as e:
            embed = discord.Embed(
                title = "Unable to remove the role",
                description = f"Error:\n```py{e}```",
                color=3092790
            )
            await ctx.send(embed = embed)
    @removerole.error
    async def removerole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.channel.send("Sorry, You are not allowed to use this command. You need `Administrator` permission to use the command.")

    @commands.command()
    async def snipe(self,ctx):
        try:
            message = self.snipes[ctx.channel.id]
        except:
            await ctx.send("Nothing to snipe!")
            return
        embed = discord.Embed(
            description = f"**Content:**\n{message.content}\n**Sent by:**\n{message.author.mention}\n**Sent in:**\n{message.channel.mention}",
            color=3092790
        )

        if len(message.attachments) >0:
            attachment = message.attachments[0]
            embed.description = embed.description + "\n\n**Attachment**:"
            if attachment.proxy_url:
                try:
                    embed.set_image(url = attachment.proxy_url)
                except:
                    embed.description = embed.description + "\nAttachment Url has expired"
            else:
                embed.description = embed.description + "\nAttachment Url has expired"
        embed.set_footer(text="Created at")
        embed.set_author(name="Snipe")
        embed.timestamp = message.created_at
        await ctx.send(embed=embed)
    @commands.command(aliases=["ps","pm"])
    @commands.has_role(939261534557851668)
    async def partnership(self,ctx,member: discord.Member):
        try:
            pm = ctx.guild.get_role(939261289392402432)
            
            await member.add_roles(pm)
            embed = discord.Embed(
                title= "Partnership Manager",
                description= f"Added {member.mention} as a partnership manager",
                color=3092790

            )
            embed.set_footer(text=f"Added by {ctx.author}")
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
    @partnership.error
    async def partnership_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.channel.send("Sorry, You are not allowed to use this command. You need `Head PM` Role to use the command.")
    @commands.command()
    async def moveroles(self,ctx, bots: discord.Role):
        # bots = ctx.guild.get_role(8844360226361835530)
        # print(bots.name)
        lenght = len(ctx.guild.roles)
        for m in bots.members:
            try:
                for r in m.roles:
                    if r != bots:
                        await r.edit(position=lenght)
            except Exception as e:
                print(e)
                continue
            print("e")
        
        await ctx.send("done")
    @commands.command()
    async def gallrole(self,ctx):
        members = ctx.guild.members
        role = ctx.guild.get_role(905033635122511892)
        print("okay")
        for m in members:
            try:
                if not role in m.roles: 
                    await m.add_roles(role)
                    print("done")
            except Exception as e:
                print(e)
                continue
        await ctx.send("Done")

    @commands.command()
    async def makeroles(self,ctx):
        s = 0
        guild = ctx.guild
        roles ={5:"ᴢᴏᴍʙɪᴇ",10:"ʟᴇᴘʀᴇᴄʜᴀᴜɴ",15:"ʙʀᴀʜᴍs",20:"ᴛʜᴇ ᴇɴᴛɪᴛʏ",25:"ʟᴇᴀᴛʜᴇʀғᴀᴄᴇ",30:"ɢʜᴏsᴛғᴀᴄᴇ",
        35:"ᴍɪᴄʜᴀᴇʟ ᴍʏᴇʀs",40:"ᴛʜᴇ ɴᴜɴ",45:"ᴀɴɴᴀʙᴇʟʟᴇ",50:"sɪɴɪsᴛᴇʀ", 60:"ғʀᴇᴅᴅʏ",70:"ᴊᴀsᴏɴ", 80:"ᴄʜᴜᴄᴋʏ",90:"ᴘᴇɴɴʏᴡɪsᴇ",
        100:"ᴛʜᴇ ᴅᴇᴠɪʟ"}
        keys = list(roles.keys())
        keys.reverse()
        for key in keys:
            color = discord.Colour.from_rgb(255,s,s)
            perm = discord.Permissions.none()
            # await ctx.send(color.value)
            role = await guild.create_role(name=f"⁶⁶⁶{roles.get(key)} | {key}⸸",permissions=perm,color= color.value)
            await ctx.send(role.mention)
            s +=15
            
            
        await ctx.send("done")
    # @commands.command()
    # async def g(self,ctx):

    # 	role = ctx.guild.get_role(813783777675051030)
    # 	await ctx.author.add_roles(role)
    @commands.command()
    async def info(self,ctx):
        with open('cogs/info.json', 'r') as f:
            info = json.load(f)
        for key in info.keys():
            embed = discord.Embed(
                title= f"{info[key][0]}",
                description=f"{info[key][1]}",
                color=3092790
            )
            perm = info[key][3]
            if perm != "None":
                embed.add_field(name="Permission Unlocked",value=f"• {perm}")
            embed.set_author(name= f"・Level {key}・")
            embed.set_thumbnail(url=info[key][2])
            await ctx.send(embed=embed)
    @commands.command()
    async def change(self,ctx):
        channels = ctx.guild.channels
        role = ctx.guild.get_role(923205585451749377)
        for channel in channels:
            await channel.edit(name=f"𝐗︱{channel.name[4:]}")
            await channel.set_permissions(role, read_messages=False)
        await ctx.send("Done")
    @commands.command()
    # @commands.check(owners2)
    async def gen(self, ctx):
        # nonBinary = discord.utils.get(ctx.guild.roles,name="Non Binary")
        others = discord.utils.get(ctx.guild.roles,name="They/Them")
        male = discord.utils.get(ctx.guild.roles,name="He/Him")
        female = discord.utils.get(ctx.guild.roles,name="She/Her")
        embed_gen = discord.Embed(
            title = "GENDER",
            description = f"<:he:924636387683233802> {male.mention}\n\n<:she:924636463507841034> {female.mention}\n\n<:they:924636504620412938> {others.mention}",
            color = 3092790
    )
        embed_gen.set_thumbnail(url="https://thumbs.gfycat.com/ShorttermSneakyBrontosaurus-small.gif")
        await ctx.send("https://tenor.com/view/visionserver-self-roles-gif-22210808")
        await ctx.send("https://i.imgur.com/mEsztqs.png")
        await ctx.send(embed=embed_gen)
        await ctx.send("https://i.imgur.com/ILSiRce.png")
    @commands.command()
    # @commands.check(owners2)
    async def age(self, ctx):
        # nonBinary = discord.utils.get(ctx.guild.roles,name="Non Binary")
        others = discord.utils.get(ctx.guild.roles,name="18+")
        male = discord.utils.get(ctx.guild.roles,name="13-15")
        female = discord.utils.get(ctx.guild.roles,name="16-18")
        embed_gen = discord.Embed(
            title = "AGE",
            description = f":person_doing_cartwheel: {male.mention}\n\n:person_bouncing_ball: {female.mention}\n\n:person_lifting_weights: {others.mention}",
            color = 3092790 
    )
        embed_gen.set_thumbnail(url="https://media3.giphy.com/media/CO2qotWn78ZrO/giphy.gif")
        await ctx.send(embed=embed_gen)
        await ctx.send("https://i.imgur.com/VE7Xy6c.png")
    # @commands.command()
    # async def rules(self,ctx):
    #     embed = discord.Embed(
    #         color = 3092790 
    #     )
    #     embed.set_image(url="https://i.imgur.com/k3remKC.png")
    #     await ctx.send(embed=embed)
    #     embed = discord.Embed(
    #         description="",
    #         color = 3092790
    #     )
    @commands.command()
    async def wtest(self,ctx,member:discord.Member):
        embed = discord.Embed(
            title= "Welcome to Xesty!",
            description = f'''Enjoy your stay {member.mention}
Boost for special perm access!
**[Xesty](https://discord.gg/wx6RkBupfh) W**''',
color= 3092790
        )
        embed.set_author(name="Xesty", icon_url=str(member.guild.icon_url))
        embed.set_thumbnail(url=str(member.avatar_url))
        # embed.set_image(url="https://i.pinimg.com/originals/81/6e/f5/816ef501d1adc014474cd018df784065.gif")
        embed.set_image(url="https://i.imgur.com/mb0r6dD.jpg")
        await ctx.channel.send(f"Welcome {member.mention}!")
        await ctx.channel.send(embed=embed)
    @commands.command()
    async def rules(self,ctx):
        # embed = discord.Embed(
        #     color= 3092790
        # )
        # # embed.set_image(url="https://i.imgur.com/o7kcSKo.png")
        # await ctx.channel.send(embed=embed)
        a = "<:rules:960071937235750942> **𝗖𝗵𝗮𝘁 𝗩𝗶𝗼𝗹𝗮𝘁𝗶𝗼𝗻𝘀**\n> Be polite. Respect other people! There is a border between jokes and harming someone's feelings and it should not be crossed. Don't joke about disabilities. Hard and non-hard n-word could get you banned!"
        b= "<:rules:960071937235750942> **𝐔𝐬𝐞𝐫 𝐕𝐢𝐨𝐥𝐚𝐭𝐢𝐨𝐧𝐬**\n> No Doxxing: If spotted, you'll immediately be banned and your account will be reported to Discord TOS.\n> No Information Leaking: If you leak somebody's private information, you will be banned and reported."
        c= "<:rules:960071937235750942> **𝐀𝐠𝐞 𝐕𝐢𝐨𝐥𝐚𝐭𝐢𝐨𝐧𝐬**\n> Being underage is against discord T.O.S. if you're lying or are underage (-13), you will be banned from the server and reported to discord."
        d="<:rules:960071937235750942> **𝐀𝐝𝐯𝐞𝐫𝐭𝐢𝐬𝐞𝐦𝐞𝐧𝐭 𝐕𝐢𝐨𝐥𝐚𝐭𝐢𝐨𝐧𝐬**\n> Do not self advertise you'll be banned right away. If you're caught DM promoting your server or socials in people's DMs, you'll be banned from the server."
        e = "<:rules:960071937235750942> **𝐃𝐢𝐬𝐜𝐨𝐫𝐝 𝐕𝐢𝐨𝐥𝐚𝐭𝐢𝐨𝐧𝐬**\n> The moment you join the server, you fully agree to follow the Discord Terms & Service. If you fail to follow the Discord TOS, you'll be banned from the server immediately.\n> ・[Discord TOS](https://discord.com/terms)\n> ・[Discord Guidelines](https://discord.com/guidelines)"              
        
        embed = discord.Embed(
            description=f"> ・1.5x Boost while gaining credits\n> ・Instant Access Image Perms\n> ・Instant Access to private threads\n> ・Instant Access to Color Roles\n> ・Special role with an icon\n",
            color=3092790
        )
        embed.set_author(name="Booster Perms",icon_url="https://cdn.discordapp.com/emojis/964132175945564201.gif?size=44&quality=lossless")
        embed.set_image(url="https://i.imgur.com/8JT8UQG.png")
        embed.set_thumbnail(url=str(ctx.guild.icon_url))
        
        await ctx.send(embed=embed)
def setup(client):
    client.add_cog(Utility(client))
