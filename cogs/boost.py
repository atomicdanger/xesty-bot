import discord
from discord.ext import commands
import requests
import os
from PIL import Image
import io
import base64
class Boost(commands.Cog):
    token = os.environ['TOKEN']
    application_id = "865841283343450122"
    api_url = f"https://discord.com/api/v9/applications/{application_id}/commands"
    header = {"Authorization": f"Bot {token}"}
    def __init__(self, client):
        self.client = client
        self.db = client.db["boost"]
    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        boost = await self.db.find_one({"_id":"boosts"})
        boosters = boost["boosters"]
        if before.premium_since == after.premium_since:
            return
        if not before.premium_since and after.premium_since:
            if not before.id in boosters:
                boosters.append(after.id)
                await self.db.replace_one({"_id":"boosts"},boost,True)
                
            return
        if before.premium_since and not after.premium_since:
            if before.id in boosters:
                boosters.remove(after.id)
                a=await self.db.find_one({"_id":before.id})
                if a:
                    role = before.guild.get_role(a["role"])
                    if role:
                        await role.delete()
                    await self.db.delete_one({"_id":before.id})
                
                await self.db.replace_one({"_id":"boosts"},boost,True)
            return
    
        
        
    @commands.command(aliases=["customrole"])
    @commands.has_role(916140209832349737)
    async def cr(self,ctx,*,flags:str):
        if ctx.channel.id !=965225348059000852:
            return
        types =["image/png","image/jpeg","image/jpg"]
        info = await self.db.find_one({"_id":ctx.author.id})
        if not info:
            info ={}
            info["role"]=None
        if not "$" in flags:
            return
        ll = flags.split("$",3)
        ll.remove("")
        name=False
        color=False
        url=False
        image=False   
        for item in ll:
            l = item.split(" ",1)
            if l[0].lower()=="name":
                name=l[1].strip()
            elif l[0].lower()=="color":
                color=l[1].strip()
            elif l[0].lower()=="url":
                url=l[1].strip()
        if len(ctx.message.attachments)>0:
            attachment = ctx.message.attachments[0]
            imagetype = (attachment.content_type[6:]).upper()
            if attachment.content_type in types:
                image_data =await attachment.read()
                if attachment.size > 256000:
                    imgdata = io.BytesIO(image_data)
                    pilimage = Image.open(imgdata)
                    pilimage.thumbnail((128,128),Image.ANTIALIAS)
                    with io.BytesIO() as f:
                        pilimage.save(f, format=f'{imagetype}', optimize=True,quality=95)
                        f.seek(0)
                        imagebytes = f.read()
                else:
                    imagebytes= await attachment.read()
                encoded = base64.b64encode(imagebytes).decode()
                image = f"data:{attachment.content_type};base64,{encoded}"
        if url and not image:
            r = requests.get(url)
            if r.ok:
                _type = r.headers['Content-Type']
                size=r.headers['Content-length']
                imagetype = (_type[6:]).upper()
                if size:
                    size = int(size)
                if _type in types:
                    image_data = r.content
                    if size > 256000:
                        imgdata = io.BytesIO(image_data)
                        pilimage = Image.open(imgdata)
                        pilimage.thumbnail((128,128),Image.ANTIALIAS)
                        with io.BytesIO() as f:
                            pilimage.save(f, format=f'{imagetype}', optimize=True,quality=95)
                            f.seek(0)
                            imagebytes = f.read()
                    else:
                        imagebytes= image_data
                    encoded = base64.b64encode(imagebytes).decode()
                    image = f"data:{_type};base64,{encoded}"
        
        m = {}
        if name:
            m["name"]=name
        if color:
            m["color"]=int(color[1:],16)
        if image:
            m["icon"]=image
        
        if info["role"]:
            role=ctx.guild.get_role(info["role"])
            if role:
                url=f"https://discord.com/api/v9/guilds/{ctx.guild.id}/roles/{role.id}"
                r=requests.patch(url,json=m,headers=self.header)
            else:
                # cr = ctx.guild.get_role(964684181277929562)
                # print(cr.position)
                url=f"https://discord.com/api/v9/guilds/{ctx.guild.id}/roles"
                r=requests.post(url,json=m,headers=self.header)
                if r.ok:
                    id = int(r.json()["id"])
                    info["role"]=id
                    guild = await self.client.fetch_guild(ctx.guild.id) 
                    role = guild.get_role(id)
                    await ctx.author.add_roles(role)
                    await role.edit(position=102)
                    
        else:
            url=f"https://discord.com/api/v9/guilds/{ctx.guild.id}/roles"
            r=requests.post(url,json=m,headers=self.header)
            if r.ok:
                id = int(r.json()["id"])
                info["role"]=id
                guild = await self.client.fetch_guild(ctx.guild.id) 
                role = guild.get_role(id)
                await ctx.author.add_roles(role)
                await role.edit(position=102)
        if r.ok:
            await ctx.send("Enjoy your Custom role!!",delete_after=3)
            await self.db.replace_one({"_id":ctx.author.id},info,True)
        else:
            await ctx.send("Failed to create role! Contact staff for more info.",delete_after=3)
        
    @commands.command()
    @commands.is_owner()
    async def cr_delete(self,ctx,member:discord.Member=None):
        await self.db.delete_one({"_id":ctx.author.id})
        await ctx.send("done",delete_after=3)
    @commands.command()
    @commands.is_owner()
    async def reset(self,ctx):
        info=await self.db.find_one({"_id":"boosts"})
        if not info:
            info={}
            info["boosters"]=[]
        boosters = ctx.guild.premium_subscribers
        for id in info["boosters"]:
            member = ctx.guild.get_member(id)
            if member.id in info["boosters"] and not member.premium_since:
                info["boosters"].remove(id)
        for booster in boosters:
            if not booster.id in info["boosters"]:
                info["boosters"].append(booster.id)
        await self.db.replace_one({"_id":"boosts"},info,True)
        await ctx.send(info["boosters"])
    @commands.command()
    async def boost(self,ctx):
        embed = discord.Embed(
            title="Thanks for Boosting",
            description="**Command:**\n`x!cr` or `x!customrole`",
color= 3092790
            
        )
        embed.add_field(name="Options",value=f"```・$name: The role name\n・$color: The color hex for the role\n・$url: Image url for the role icon\n・[Attachment]: Image attachment for the role icon\n\nNote: The image or image url needs to be either png or jpeg```")
        embed.add_field(name="Example",value=f"```x!cr $name Dangie $color #000001 $url https://i.imgur.com/n0Q1D1k.png```",inline=False)
        embed.set_image(url="https://i.imgur.com/8JT8UQG.png")
        # embed.set_thumbnail(url=str(ctx.guild.icon_url))
        await ctx.send(embed=embed)
async def setup(client):
    await client.add_cog(Boost(client))