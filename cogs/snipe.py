import discord
from discord.ext import commands
import os
import requests
import io
from discord.ui import Button, View, TextInput, Modal
import datetime

class Snipe(commands.Cog):
    token = os.environ['TOKEN']
    application_id = "865841283343450122"
    api_url = f"https://discord.com/api/v9/applications/{application_id}/commands"
    header = {"Authorization": f"Bot {token}"}
    def __init__(self, client):
        self.client = client
        
    @commands.command(aliases=['s', 'fetch'])
    async def snipe(self,ctx):
        async with ctx.channel.typing():
            try:
                data = await self.client.snipe.find_one({"_id":ctx.channel.id})
                if not data:
                    embed = discord.Embed(color=3092790, description=f"**Noting to snipe**")
                    return await ctx.send(embed=embed)
                # try:
                #     channel = data["channels"][str(ctx.channel.id)]
                # except:
                #     embed = discord.Embed(color=3092790, description=f"**{ctx.author.mention}: nothing 2 snipe**")
                #     return await ctx.send(embed=embed)
                # else:
                channel = data["messages"]
                if len(channel)==0:
                    embed = discord.Embed(color=3092790, description=f"**Noting to snipe**")
                    return await ctx.send(embed=embed)
                async def get(index):
                    message = channel[index]
                    timestamp = datetime.datetime.fromisoformat(message["timestamp"])
                    embeds=[]
                    files=[]
                    embed= discord.Embed(color=3092790)
                    embed.set_footer(text=f"1/{len(channel)}")
                    embed.set_author(name=str(ctx.author),icon_url=str(ctx.author.display_avatar))
                    embed.timestamp=timestamp
                    user = await self.client.fetch_user(message["author"])
                    embed.set_author(name=str(user),icon_url=str(user.display_avatar))
                    embed.set_footer(text=f"{index+1}/{len(channel)}")
                    embed.description=""    
                    if message["content"]:
                        embed.description+=message["content"]+"\n"
                    if message["embed"]:
                        embed.description+="**Embed:** True"+"\n"
                        e=discord.Embed.from_dict(message["embed"])
                        embeds.append(e)
                    if message["attachment"]:
                        if message["attachment"]["bytes"]:
                            f=io.BytesIO(message["attachment"]["bytes"])
                            embed.description+="**Attachment:** True"+"\n"
                            
                            file = discord.File(f,message["attachment"]["name"])
                            files.append(file)
                        elif message["attachment"]["image"]:
                            embed.set_image(url=message["attachment"]["url"])
                            embed.description+="**Attachment:** True"+"\n"
                        else:
                            embed.description+= f'**Attachment:**\n[{message["attachment"]["name"]}]({message["attachment"]["url"]})'+"\n"
                    embeds.append(embed)
                    return (embeds,files)
                embeds,files = await get(0)
                cooldown ={}
                for i in range(1,len(channel)+1):
                    cooldown[str(i)]=False
                wb_icon = self.client.get_emoji(978603039474733077)
                wb = Button(emoji=wb_icon, custom_id=f"snipe_webhook",style=discord.ButtonStyle.grey)
                
                async def webhook_callback(i:discord.Interaction):
                    if i.user != ctx.author:
                        return await i.response.send_message(f"Invoker only",ephemeral=True)
                    if len(i.message.embeds)==1:
                        embed_index = 0
                    else:
                        embed_index=1
                    content=None
                    wb_embeds=[]
                    wb_files=[]
                    page = int(i.message.embeds[embed_index].footer.text.split("/")[0])
                    message = channel[page-1]
                    author= await self.client.fetch_user(message["author"])
                    cooldown[str(page)]=True
                    c_i=0
                    if len(view.children)>1:
                        c_i=2
                    view.children[c_i].disabled=True
                    webhook = await ctx.channel.create_webhook(name=author.display_name,avatar=await author.display_avatar.read())
                    if message["content"]:
                        content=message["content"]
                    if message["embed"]:
                        e=discord.Embed.from_dict(message["embed"])
                        wb_embeds.append(e)
                    if message["attachment"]:
                        if message["attachment"]["bytes"]:
                            f=io.BytesIO(message["attachment"]["bytes"])
                            
                            
                            file = discord.File(f,message["attachment"]["name"])
                            wb_files.append(file)
                        else:
                            if content:
                                content+=message["attachment"]["url"] 
                            else:
                                content = message["attachment"]["url"]
                    await webhook.send(content=content,embeds=wb_embeds,files=wb_files)
                    await webhook.delete(prefer_auth=False)
                    await i.response.edit_message(view=view)
                wb.callback= webhook_callback
                if len(channel)==1:
                    view = View(timeout=120)
                    view.add_item(wb)
                    
                    message = await ctx.send(embeds=embeds,files=files,view=view)
                    async def on_timeout():
                        view.clear_items()
                        await message.edit(view=view)
                    view.on_timeout=on_timeout
                    return
                
                left_arrow = self.client.get_emoji(978571039342747648)
                right_arrow = self.client.get_emoji(978571041712533524)
                
                previous = Button(emoji=left_arrow, custom_id=f"snipe_prev",style=discord.ButtonStyle.grey,disabled=True)
                next = Button(emoji=right_arrow, custom_id=f"snipe_next",style=discord.ButtonStyle.grey)
                
                view = View(timeout=120)
                view.add_item(previous)
                view.add_item(next)
                view.add_item(wb)

                async def previous_callback(i:discord.Interaction):
                    if i.user != ctx.author:
                        return await i.response.send_message(f"Invoker only",ephemeral=True)
                    if len(i.message.embeds)==1:
                        embed_index = 0
                    else:
                        embed_index=1
                    page = int(i.message.embeds[embed_index].footer.text.split("/")[0])
                    view.children[1].disabled=False
                    if page==2:
                        view.children[0].disabled=True
                    view.children[2].disabled=False
                    if cooldown[str(page-1)]:
                        view.children[2].disabled=True
                        
                    embeds,file= await get(page-2)
                    await i.response.edit_message(embeds=embeds,attachments=file,view=view)
                async def next_callback(i:discord.Interaction):
                    if i.user != ctx.author:
                        return await i.response.send_message(f"Invoker only",ephemeral=True)
                    if len(i.message.embeds)==1:
                        embed_index = 0
                    else:
                        embed_index=1
                    page = int(i.message.embeds[embed_index].footer.text.split("/")[0])
                    
                    view.children[0].disabled=False
                    if len(channel)-1 ==page:
                        view.children[1].disabled=True
                    view.children[2].disabled=False
                    if cooldown[str(page+1)]:
                        view.children[2].disabled=True
                    embeds,file= await get(page)
                    await i.response.edit_message(embeds=embeds,attachments=file,view=view)
                previous.callback= previous_callback
                next.callback= next_callback
                
                message = await ctx.send(embeds=embeds,files=files,view=view)
                async def on_timeout():
                    view.clear_items()
                    await message.edit(view=view)
                view.on_timeout=on_timeout
            except Exception as e:
                await ctx.send(e)
        
                

    
    @commands.Cog.listener()
    async def on_message_delete(self,message):
        if message.is_system():
            return
        if message.webhook_id:
            return
        
        data = await self.client.snipe.find_one({"_id":message.channel.id})
        if not data:
            data = {}
            data["messages"]=[]
        # try:
        #     channel= data["channels"][str(message.channel.id)]
        # except:
        #     data["channels"][str(message.channel.id)]=[]
        #     channel = data["channels"][str(message.channel.id)]
        channel = data["messages"]
        m = {"content":None,"embed":None,"attachment":None,"timestamp":None,"author":message.author.id}
        if message.content:
            m["content"]=message.content
        if len(message.embeds)>0:
            embed = message.embeds[0].to_dict()
            m["embed"]=embed
        if len(message.attachments)>0:
            url = message.attachments[0].proxy_url
            image=False
            bytes=None
            filename= str(message.attachments[0].filename)
            if "image" in message.attachments[0].content_type:
                image = True
            if message.attachments[0].size < 8 * 1024000:
                bytes=await message.attachments[0].read(use_cached=True)
            m["attachment"]={"name":filename,"url":url,"bytes":bytes,"image":image}
        m["timestamp"]=str(message.created_at.isoformat())
        if len(channel)==10:
            channel.pop()
        channel.insert(0,m)
        await self.client.snipe.replace_one({"_id":message.channel.id},data,True)
            
   
        
        
async def setup(client):
    await client.add_cog(Snipe(client))