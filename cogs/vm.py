import discord, datetime, time, math, requests
from discord.ext import commands
from discord.utils import get
from discord.ui import Button, View, TextInput, Modal, Select
import asyncio
# from Messages import ActionRow, Button, MenuOption,SelectMenu
import os

class VM(commands.Cog):
    
    def __init__(self, bot):
        self.client = bot
        self.methods = {"vmrename":self.rename,"vmlock":self.lock,"vmunlock":self.unlock,"vmghost":self.ghost,"vmunghost":self.unghost,
                  "vmban":self.vmban,
                  "vmunban":self.vmunban,"vmwhitelist":self.whitelist,"vmactivity":self.activity,"vmdelete":self.delete}
    @commands.Cog.listener()
    async def on_interaction(self,i:discord.Interaction):
        # if i.channel_id==979681423160147968:
        data = i.data
        method = data["custom_id"]
        if method in list(self.methods.keys()):
            await self.methods[method](i)
    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        whitelist=[535490443681595392]
        jvc_id= 979681300220903425
        b=None
        a=None
        if before.channel and before.channel.id == jvc_id:
            return
        if before.channel:
            b_channel = before.channel.id
            b = await self.client.vm.find_one({"channel":b_channel})    
        else:
            a_channel = after.channel.id
            a = await self.client.vm.find_one({"channel":a_channel})     
        if b and before.channel.id == b["channel"]:
            if not b["boost"]:
                if len(before.channel.members) == 0:
                    await before.channel.delete(reason="Empty Vc")
                    b["channel"]=None
                    await self.client.vm.replace_one({"_id":b["_id"]},b)
            else:
                cooldown = b["cooldown"]["last"]+30
                if cooldown >time.time():
                    t=cooldown-time.time()
                    await asyncio.sleep(t)
                    before.channel = await member.guild.fetch_channel(before.channel.id)
                if len(before.channel.members) == 0:
                    await before.channel.delete(reason="Empty Vc")
                    b["channel"]=None
                    b["boost"]=False
                    await self.client.vm.replace_one({"_id":b["_id"]},b)
                
        if a and after.channel.id ==a["channel"]:
            if member.id != a["_id"]:
                if member.id in whitelist:
                    return
                if member.id in a["ban"]:
                    await member.move_to(before.channel)
                    return
                if a["lock"] or a["ghost"] and not member.id in a["whitelist"]:
                    await member.move_to(before.channel)
                    return
        if after.channel and after.channel.id == jvc_id:
            booster=None
            booster_c=None
            data = await self.client.vm.find_one({"_id":member.id})
            if data:
                if data["channel"]:
                    return
                cooldown = data["cooldown"]["last"]+30
                if cooldown >time.time():
                    if data["cooldown"]["warns"]==3:
                        return
                    data["cooldown"]["warns"]+=1
                    if not member.premium_since:
                        embed= discord.Embed(color=3092790,title="Cooldown",description=f"Wait <t:{cooldown}:R> before being able to make a new VC.\nBoost the server to avoid the cooldowns!")
                        embed.set_author(name="Voice Master")
                        try:
                            await member.send(embed=embed)
                        except:
                            interface_c = member.guild.get_channel(979681423160147968)
                            await interface_c.send(member.mention,delete_after=3)
                            await interface_c.send(embed=embed,delete_after=3)
                        await self.client.vm.replace_one({"_id":member.id},data,True)
                    else:
                        booster=True
                    if data["cooldown"]["warns"]==3:
                        ban_role= member.guild.get_role(2)
                        await member.add_roles(ban_role)
                        if not member.premium_since:
                            await asyncio.sleep(300)
                            await member.remove_roles(ban_role)
                            return
                        else:
                            booster_c=True
            jtc = await self.client.fetch_channel(jvc_id)
            overwrites = {}
            overwrite = discord.PermissionOverwrite()
            overwrite.view_channel= True
            overwrite.connect= True
            overwrite.create_instant_invite= True
            overwrite.speak= True
            overwrite.stream= True
            overwrite.priority_speaker= True
            overwrite.mute_members= True
            overwrite.deafen_members= True
            overwrite.move_members= True
            overwrites[member]=overwrite
            name = f"{member.display_name}'s vc"
            if data:
                if data["name"]:
                    name = data["name"]
                if data["lock"]:
                    overwrite = discord.PermissionOverwrite()
                    overwrite.connect= False
                    overwrites[member.guild.default_role]=overwrite
                if data["ghost"]:
                    overwrite = discord.PermissionOverwrite()
                    overwrite.view_channel= False
                    overwrites[member.guild.default_role]=overwrite
                for id in data["ban"]:
                    m = await member.guild.fetch_member(id) 
                    overwrite = discord.PermissionOverwrite()
                    overwrite.connect= False
                    overwrites[m]=overwrite
                for id in data["whitelist"]:
                    m = await member.guild.fetch_member(id) 
                    overwrite = discord.PermissionOverwrite()
                    overwrite.connect= True
                    overwrite.view_channel= True
                    overwrites[m]=overwrite
            else:
                data={}
                data["name"]=None
                data["ghost"]=None
                data["lock"]=None
                data["ban"]=[]
                data["whitelist"]=[]
            data["boost"]=False
            if not booster:
                data["cooldown"]={"last":time.time(),"warns":0}
            if booster_c:
                data["boost"]=True
            new_vc = await member.guild.create_voice_channel(name=name,category=jtc.category,overwrites=overwrites)
            data["channel"]=new_vc.id
            await member.move_to(new_vc)
            await self.client.vm.replace_one({"_id":member.id},data,True)
            if booster_c:
                await asyncio.sleep(300)
                await member.remove_roles(ban_role)

    async def rename(self,i):
        user= i.user
        if not user.voice or not user.voice.channel:
            embed = discord.Embed(color=3092790,description=f"**You aren't connected to a voice channel**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.voice.channel.category_id !=979681214787121192:
            embed = discord.Embed(color=3092790,description=f"**The interface only works for join to create channels**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        data = await self.client.vm.find_one({"channel":user.voice.channel.id})
        if not data:
            embed = discord.Embed(color=3092790,description=f"**The channel wasn't registered in the database. Contact the staff for more info!**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.id !=data["_id"]:
            owner = user.guild.get_member(data["_id"])
            embed = discord.Embed(color=3092790,description=f"**Only owner of the voice channel ({owner.mention}) can access the feature**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        modal = Modal(title="Rename")
        text = TextInput(label="Name",placeholder="Submit empty to reset the name",required=False)
        async def rename_callback(ir:discord.Interaction):
            name = text.value
            n = text.value
            if not name:
                name = f"{user.display_name}'s vc"
                n=None
            await user.voice.channel.edit(name=name)
            data["name"]=n
            await self.client.vm.replace_one({"_id":user.id},data)
            embed = discord.Embed(color=3092790,description=f"Renamed the channel to **{name}**")
            await ir.response.send_message(embed=embed,ephemeral=True)
        modal.on_submit=rename_callback
        modal.add_item(text)
        await i.response.send_modal(modal)#lets test it
    @commands.command()
    async def testem(self,ctx):
        embed= discord.Embed(title="Hey")
        view=View(timeout=None)
        button = Button(label="Activity",custom_id="vmactivity")
        # button1 = Button(label="Unlock",custom_id="vmunlock")
        # button3 = Button(label="Ghost",custom_id="vmghost")
        # button4 = Button(label="Unghost",custom_id="vmunghost")
        
        view.add_item(button)
        # view.add_item(button1)
        # view.add_item(button3)
        # view.add_item(button4)
        
        # async def response(i:discord.Interaction):
        #     print("b")
        #     await self.rename(i)
        await ctx.send(embed=embed,view=view)#lets test it
    async def lock(self,i:discord.Interaction):
        user= i.user
        if not user.voice or not user.voice.channel:
            embed = discord.Embed(color=3092790,description=f"**You aren't connected to a voice channel**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.voice.channel.category_id !=979681214787121192:
            embed = discord.Embed(color=3092790,description=f"**The interface only works for join to create channels**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        data = await self.client.vm.find_one({"channel":user.voice.channel.id})
        if not data:
            embed = discord.Embed(color=3092790,description=f"**The channel wasn't registered in the database. Contact the staff for more info!**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.id !=data["_id"]:
            owner = user.guild.get_member(data["_id"])
            embed = discord.Embed(color=3092790,description=f"**Only owner of the voice channel ({owner.mention}) can access the feature**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        overwrite = user.voice.channel.overwrites_for(user.guild.default_role)
        overwrite.connect=False
        await user.voice.channel.set_permissions(user.guild.default_role,overwrite=overwrite)
        view = View(timeout=10) 
        unlock = Button(label="Unlock",custom_id="vmunlock")
        view.add_item(unlock) 
        embed = discord.Embed(color=3092790,title="Lock",description=f"[`Locks`](https://discord.gg/xesty) the channel for everyone.\n**Locked** the voice channel!\n\n**Usage:**\n・[`Unlock`](https://discord.gg/xesty): Click the button to unlock the channel")
        await i.response.send_message(embed=embed,view=view,ephemeral=True)
        data["lock"]=True
        await self.client.vm.replace_one({"_id":user.id},data)
        async def on_timeout():
            view.clear_items()
            await i.edit_original_message(view=view)
        view.on_timeout=on_timeout
        
    async def unlock(self,i):
        user= i.user
        if not user.voice or not user.voice.channel:
            embed = discord.Embed(color=3092790,description=f"**You aren't connected to a voice channel**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.voice.channel.category_id !=979681214787121192:
            embed = discord.Embed(color=3092790,description=f"**The interface only works for join to create channels**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        data = await self.client.vm.find_one({"channel":user.voice.channel.id})
        if not data:
            embed = discord.Embed(color=3092790,description=f"**The channel wasn't registered in the database. Contact the staff for more info!**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.id !=data["_id"]:
            owner = user.guild.get_member(data["_id"])
            embed = discord.Embed(color=3092790,description=f"**Only owner of the voice channel ({owner.mention}) can access the feature**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        overwrite = user.voice.channel.overwrites_for(user.guild.default_role)
        overwrite.connect=None
        await user.voice.channel.set_permissions(user.guild.default_role,overwrite=overwrite)
        view = View(timeout=10) 
        lock = Button(label="Lock",custom_id="vmlock")
        view.add_item(lock) 
        embed = discord.Embed(color=3092790,title="Unlock",description=f"[`Unlocks`](https://discord.gg/xesty) the channel and lets everyone join.\n**Unlocked** the voice channel!\n\n**Usage:**\n・[`Lock`](https://discord.gg/xesty): Click the button to lock the channel")
        await i.response.send_message(embed=embed,view=view,ephemeral=True)
        data["lock"]=None
        await self.client.vm.replace_one({"_id":user.id},data)
        async def on_timeout():
            view.clear_items()
            await i.edit_original_message(view=view)
        view.on_timeout=on_timeout
        

    async def ghost(self,i):
        user= i.user
        if not user.voice or not user.voice.channel:
            embed = discord.Embed(color=3092790,description=f"**You aren't connected to a voice channel**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.voice.channel.category_id !=979681214787121192:
            embed = discord.Embed(color=3092790,description=f"**The interface only works for join to create channels**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        data = await self.client.vm.find_one({"channel":user.voice.channel.id})
        if not data:
            embed = discord.Embed(color=3092790,description=f"**The channel wasn't registered in the database. Contact the staff for more info!**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.id !=data["_id"]:
            owner = user.guild.get_member(data["_id"])
            embed = discord.Embed(color=3092790,description=f"**Only owner of the voice channel ({owner.mention}) can access the feature**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        overwrite = user.voice.channel.overwrites_for(user.guild.default_role)
        overwrite.view_channel=False
        await user.voice.channel.set_permissions(user.guild.default_role,overwrite=overwrite)
        view = View(timeout=10) 
        lock = Button(label="Unhide",custom_id="vmunghost")
        view.add_item(lock) 
        embed = discord.Embed(color=3092790,title="Hide",description=f"[`Hides`](https://discord.gg/xesty) the channel from everyone.\n**Hid** the voice channel!\n\n**Usage:**\n・[`Unhide`](https://discord.gg/xesty): Click the button to unhide the channel")
        
        await i.response.send_message(embed=embed,view=view,ephemeral=True)
        data["ghost"]=True
        await self.client.vm.replace_one({"_id":user.id},data)
        async def on_timeout():
            view.clear_items()
            await i.edit_original_message(view=view)
        view.on_timeout=on_timeout
    async def unghost(self,i):
        user= i.user
        if not user.voice or not user.voice.channel:
            embed = discord.Embed(color=3092790,description=f"**You aren't connected to a voice channel**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.voice.channel.category_id !=979681214787121192:
            embed = discord.Embed(color=3092790,description=f"**The interface only works for join to create channels**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        data = await self.client.vm.find_one({"channel":user.voice.channel.id})
        if not data:
            embed = discord.Embed(color=3092790,description=f"**The channel wasn't registered in the database. Contact the staff for more info!**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.id !=data["_id"]:
            owner = user.guild.get_member(data["_id"])
            embed = discord.Embed(color=3092790,description=f"**Only owner of the voice channel ({owner.mention}) can access the feature**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        overwrite = user.voice.channel.overwrites_for(user.guild.default_role)
        overwrite.view_channel=None
        await user.voice.channel.set_permissions(user.guild.default_role,overwrite=overwrite)
        view = View(timeout=10) 
        lock = Button(label="Hide",custom_id="vmghost")
        view.add_item(lock) 
        embed = discord.Embed(color=3092790,title="Unhide",description=f"[`Unhides`](https://discord.gg/xesty) the channel from everyone.\n**Unhid** the voice channel!\n\n**Usage:**\n・[`Hide`](https://discord.gg/xesty): Click the button to hide the channel")
        
        await i.response.send_message(embed=embed,view=view,ephemeral=True)
        data["ghost"]=None #test now?
        await self.client.vm.replace_one({"_id":user.id},data)
        async def on_timeout():
            view.clear_items()
            await i.edit_original_message(view=view)
        view.on_timeout=on_timeout
    
    async def vmban(self,i):
        user= i.user
        if not user.voice or not user.voice.channel:
            embed = discord.Embed(color=3092790,description=f"**You aren't connected to a voice channel**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.voice.channel.category_id !=979681214787121192:
            embed = discord.Embed(color=3092790,description=f"**The interface only works for join to create channels**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        data = await self.client.vm.find_one({"channel":user.voice.channel.id})
        if not data:
            embed = discord.Embed(color=3092790,description=f"**The channel wasn't registered in the database. Contact the staff for more info!**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.id !=data["_id"]:
            owner = user.guild.get_member(data["_id"])
            embed = discord.Embed(color=3092790,description=f"**Only owner of the voice channel ({owner.mention}) can access the feature**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        embed = discord.Embed(
            title="Ban",
            description="[`Bans`](https://discord.gg/xesty) users from joining your channel even if its unlocked.\n\n**Usage:**\n・[`Ban User`](https://discord.gg/xesty): Click the button to enter the member you wish to ban from the VC",
            color=3092790
        )
        view=View()
        button = Button(label="Ban User",custom_id="select_button_vmban",style=discord.ButtonStyle.red)
        b_bans = Button(label="Bans",custom_id="vmbans")
        view.add_item(button)
        view.add_item(b_bans) 
        async def ban_member(id):
            member = i.guild.get_member(int(id))
            if not member:
                return
            overwrite = user.voice.channel.overwrites_for(member)
            overwrite.connect=False
            await user.voice.channel.set_permissions(member,overwrite=overwrite)
            return member
        async def select_callback(ir):
            values = ir.data["values"]
            bans=[]
            reason=""
            for id in values:
                member =await ban_member(id)
                if not member:
                    reason="・Member not found\n"
                    continue
                if id in data["ban"]:
                    reason="・Member already is banned\n"
                    continue
                bans.append(member.id)
            view.clear_items()
            view.clear_items()
            view.add_items(b_bans)
            if len(bans)>0:
                embed.description = f"**Banned** `0` members\n**Reason:\n**{reason}\n\n**Usage:**\n・[`Bans`](https://discord.gg/xesty): Click the button to see all the bans."
                await ir.response.edit_message(embed=embed,view=view)
            else:
                data["ban"].extend(bans)
                await self.client.vm.replace_one({"_id":user.id},data)
                embed.description = f"**Banned** `{len(bans)}` members\n\n**Usage:**\n・[`Bans`](https://discord.gg/xesty): Click the button to see all the bans."
                await ir.response.edit_message(embed=embed,view=view)
        async def button_callback(ir): 
            modal = Modal(title="Ban")
            text = TextInput(label="Ban Member",placeholder="Enter the ID or the username",required=True)
            async def text_callback(irr:discord.Interaction):
                x = text.value
                member = user.guild.get_member_named(x) or user.guild.get_member(int(x))
                view.clear_items()
                view.add_item(b_bans)
                if not member:
                    embed.description = f"**Banned** `0` members\n**Reason:\n**・Member not found\n\n**Usage:**\n・[`Bans`](https://discord.gg/xesty): Click the button to see all the bans."
                    await irr.response.edit_message(embed=embed,view=view)
                    return
                overwrite = user.voice.channel.overwrites_for(member)
                overwrite.connect=False
                await user.voice.channel.set_permissions(member,overwrite=overwrite)
                if member.id in data["ban"]:
                    embed.description = f"**Banned** `0` members\n**Reason:\n**・Member already is banned\n\n**Usage:**\n・[`Bans`](https://discord.gg/xesty): Click the button to see all the bans."
                    await irr.response.edit_message(embed=embed,view=view)
                    return
                data["ban"].append(member.id)
                await self.client.vm.replace_one({"_id":user.id},data)
                
                embed.description = f"**Banned** {member.mention}\n\n**Usage:**\n・[`Bans`](https://discord.gg/xesty): Click the button to see all the bans."
                await irr.response.edit_message(embed=embed,view=view)
            modal.on_submit=text_callback
            modal.add_item(text)
            await ir.response.send_modal(modal)
        async def list_callback(ir):
            d = data["ban"]
            if len(d)==0:
                view.clear_items()
                await ir.response.edit_message(content="No members are ban.",embed=None,view=view)
                return
            embed,pages = await self.page(ir,1,d)
            embed.title ="Bans"
            if pages >1:
                embed.set_footer(text=f"1/{pages}")
                previous = Button(label="Previous", custom_id=f"vmban_prev",style=discord.ButtonStyle.grey,disabled=True)
                next = Button(label="Next", custom_id=f"vmban_next",style=discord.ButtonStyle.grey)
                view = View(timeout=120)
                view.add_item(previous)
                view.add_item(next)
        
                async def previous_callback(irr:discord.Interaction):
                    page = int(irr.message.embeds[0].footer.text.split("/")[0])
                    view.children[1].disabled=False
                    if page==2:
                        view.children[0].disabled=True
                    embedp,pagesp = await self.page(page-1,d)
                    embedp.set_footer(text=f"{page-1}/{pagesp}")
                    embedp.title ="Bans"
                    await irr.response.edit_message(embed=embedp,view=view)
                async def next_callback(irr:discord.Interaction):
                    page = int(irr.message.embeds[0].footer.text.split("/")[0])
                    
                    view.children[0].disabled=False
                    if pages-1 ==page:
                        view.children[1].disabled=True
                    embedn,pagesp = await self.page(page+1,d)
                    embedn.set_footer(text=f"{page+1}/{pagesp}")
                    embedn.title ="Bans"
                    await irr.response.edit_message(embed=embedn,view=view)
                previous.callback= previous_callback
                next.callback= next_callback
                
                await ir.response.edit_message(embed=embed,view=view)                
            else:
                view.clear_items()
                await ir.response.edit_message(embed=embed,view=view)
        if len(user.voice.channel.members)>1 and len(user.voice.channel.members)<=25:
            select = Select(custom_id="select_vmban",placeholder="Select a member to ban from the VC",max_value=len(user.voice.channel.members))
            view.add_item(select)
            for member in user.voice.channel.members[:25]:
                if not member.id == data["_id"]:
                    select.add_option(label=f"{member.display_name}",value=member.id,description=str(member)) 
            embed.description+="\n・[`DropDown Menu`](https://discord.gg/xesty): Select an existing VC participant to ban."
            select.callback=select_callback
        button.callback=button_callback
        b_bans.callback=list_callback
        embed.description+="\n・[`Bans`](https://discord.gg/xesty): Click the button to see all the bans."
        await i.response.send_message(embed=embed,view=view,ephemeral=True)
        async def on_timeout():
            view.clear_items()
            await i.edit_original_message(view=view)
        view.on_timeout=on_timeout
        
    async def vmunban(self,i):
        user= i.user
        if not user.voice or not user.voice.channel:
            embed = discord.Embed(color=3092790,description=f"**You aren't connected to a voice channel**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.voice.channel.category_id !=979681214787121192:
            embed = discord.Embed(color=3092790,description=f"**The interface only works for join to create channels**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        data = await self.client.vm.find_one({"channel":user.voice.channel.id})
        if not data:
            embed = discord.Embed(color=3092790,description=f"**The channel wasn't registered in the database. Contact the staff for more info!**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.id !=data["_id"]:
            owner = user.guild.get_member(data["_id"])
            embed = discord.Embed(color=3092790,description=f"**Only owner of the voice channel ({owner.mention}) can access the feature**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        embed = discord.Embed(
            title="Ban",
            description="[`Unbans`](https://discord.gg/xesty) users and lets em join your channel if its unlocked.\n\n**Usage:**\n",
            color=3092790
        )
        if len(data["ban"])==0:
            await i.response.send_message(content="No users are banned",ephemeral=True)
            return
        view=View()
        async def select_callback(ir):
            values = ir.data["values"]
            for id in values:
                member = ir.guild.get_member(int(id))
                if member:
                    overwrite = user.voice.channel.overwrites_for(member)
                    overwrite.connect=None
                    await user.voice.channel.set_permissions(member,overwrite=overwrite)
                data["ban"].remove(id)
            view.clear_items()
            view.add_items(b_bans)
            await self.client.vm.replace_one({"_id":user.id},data)
            embed.description = f"**Unbanned** `{len(data['values'])}` members\n\n**Usage:**\n・[`Bans`](https://discord.gg/xesty): Click the button to see all the bans."
            await ir.response.edit_message(embed=embed,view=view)
        async def button_callback(ir): 
            modal = Modal(title="Unban")
            text = TextInput(label="Unban Member",placeholder="Enter the ID or the username",required=True)
            async def text_callback(irr:discord.Interaction):
                x = text.value
                view.clear_items()
                view.add_item(b_bans)
                member = user.guild.get_member_named(x) or user.guild.get_member(int(x))
                if not member:
                    try:
                        member = await self.client.fetch_user(int(x))
                    except:
                        embed.description = f"**Unbanned** `0` members\n**Reason:\n**・Member not found\n\n**Usage:**\n・[`Bans`](https://discord.gg/xesty): Click the button to see all the bans."
                        await irr.response.edit_message(embed=embed,view=view)
                        return
                if not member.id in data["ban"]:
                    embed.description = f"**Unbanned** `0` members\n**Reason:\n**・Member was never banned\n\n**Usage:**\n・[`Bans`](https://discord.gg/xesty): Click the button to see all the bans."
                    await irr.response.edit_message(embed=embed,view=view)
                    return
                if type(member)== discord.Member:
                    overwrite = user.voice.channel.overwrites_for(member)
                    overwrite.connect=None
                    await user.voice.channel.set_permissions(member,overwrite=overwrite)
                data["ban"].remove(member.id)
                embed.description = f"**Unbanned** {member.mention}\n\n**Usage:**\n・[`Bans`](https://discord.gg/xesty): Click the button to see all the bans."
                await irr.response.edit_message(embed=embed,view=view)
                await self.client.vm.replace_one({"_id":user.id},data)
                
            modal.on_submit=text_callback
            modal.add_item(text)
            await ir.response.send_modal(modal)
        async def list_callback(ir):
            d = data["ban"]
            if len(d)==0:
                view.clear_items()
                await ir.response.edit_message(content="No members are ban.",embed=None,view=view)
                return
            embed,pages = await self.page(ir,1,d)
            embed.title ="Bans"
            if pages >1:
                embed.set_footer(text=f"1/{pages}")
                previous = Button(label="Previous", custom_id=f"vmban_prev",style=discord.ButtonStyle.grey,disabled=True)
                next = Button(label="Next", custom_id=f"vmban_next",style=discord.ButtonStyle.grey)
                view = View(timeout=120)
                view.add_item(previous)
                view.add_item(next)
        
                async def previous_callback(irr:discord.Interaction):
                    page = int(irr.message.embeds[0].footer.text.split("/")[0])
                    view.children[1].disabled=False
                    if page==2:
                        view.children[0].disabled=True
                    embedp,pagesp = await self.page(page-1,d)
                    embedp.set_footer(text=f"{page-1}/{pagesp}")
                    embedp.title ="Bans"
                    await irr.response.edit_message(embed=embedp,view=view)
                async def next_callback(irr:discord.Interaction):
                    page = int(irr.message.embeds[0].footer.text.split("/")[0])
                    
                    view.children[0].disabled=False
                    if pages-1 ==page:
                        view.children[1].disabled=True
                    embedn,pagesp = await self.page(page+1,d)
                    embedn.set_footer(text=f"{page+1}/{pagesp}")
                    embedn.title ="Bans"
                    await irr.response.edit_message(embed=embedn,view=view)
                previous.callback= previous_callback
                next.callback= next_callback
                
                await ir.response.edit_message(embed=embed,view=view)                
            else:
                view.clear_items()
                await ir.response.edit_message(embed=embed,view=view)   
        if len(data["ban"])<=25:
            select = Select(custom_id="select_vmunban",placeholder="Select a member to unban from the VC",max_value=len(data["ban"]))
            view.add_item(select)
            for id in data["ban"]:
                try:
                    member = await self.client.fetch_user(id)
                    select.add_option(label=f"{member.display_name}",value=member.id,description=str(member))
                except:
                    pass
            embed.description+="・[`DropDown Menu`](https://discord.gg/xesty): Select a member to unban from the dropdown menu.\n"
            select.callback=select_callback
        else:
            button = Button(label="Unban User",custom_id="select_button_vmunban",style=discord.ButtonStyle.primary)
            view.add_item(button)
            embed.description ="・[`Unban User`](https://discord.gg/xesty): Click the button to enter the member you wish to ban from the VC\n"
            button.callback=button_callback
        b_bans = Button(label="Bans",custom_id="vmbans")
        view.add_item(b_bans)
        b_bans.callback=list_callback
        embed.description+="・[`Bans`](https://discord.gg/xesty): Click the button to see all the bans."
        await i.response.send_message(embed=embed,view=view,ephemeral=True)
        async def on_timeout():
            view.clear_items()
            await i.edit_original_message(view=view)
        view.on_timeout=on_timeout
    async def activity(self,i):
        guild = self.client.get_guild(944557938914263060)
        emojis = guild.emojis
        user= i.user
        if not user.voice or not user.voice.channel:
            embed = discord.Embed(color=3092790,description=f"**You aren't connected to a voice channel**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.voice.channel.category_id !=979681214787121192:
            embed = discord.Embed(color=3092790,description=f"**The interface only works for join to create channels**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        data = await self.client.vm.find_one({"channel":user.voice.channel.id})
        if not data:
            embed = discord.Embed(color=3092790,description=f"**The channel wasn't registered in the database. Contact the staff for more info!**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.id !=data["_id"]:
            owner = user.guild.get_member(data["_id"])
            embed = discord.Embed(color=3092790,description=f"**Only owner of the voice channel ({owner.mention}) can access the feature**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
                
        activities={#goodenough?
    "880218394199220334":["Watch Together","Watch Youtube together with your friends."],
    "945737671223947305": ["Putt Party","Putt Party our putting golf game that you can play with your friends."],
    "832025144389533716": ["Blazing 8s","Blazing 8s(Uno) is our Crazy Eights-inspired card game that you can play with your friends!"], 
    "832012774040141894": ["Chess in the Park","Unleash your Grandmaster by playing multiple games of Chess at once vs anybody on the server."],
    "832013003968348200": ["Checkers in the Park","Checkers is a multiplayer checkers strategy game"],
    "755827207812677713": ["Poker Night","Poker Night is a Texas hold 'em style game mode with up to 7 other players."],
    "902271654783242291": ["Sketch Heads","A game where you discover that you're either bad at drawing or your friends are bad at guessing!"],
    "852509694341283871": ["SpellCast","A word game where everyone takes turns attempting to find words in sequences of adjacent letters."],
    "903769130790969345": ["Land-io","Land-io is an IO-style, snake-inspired arcade game that can be played with 1-16 players at a time."],
    "879863686565621790": ["Letter League","A game where everyone places letters on a shared game board to create words in a crossword-style."],
    "879863976006127627": ["Word Snacks","Word Snacks is a multiplayer word search game, find and make as many words as possible."],
}
        view = View()
        select = Select(custom_id="select_vmactivity",placeholder="Select an activity to start") 
        async def select_callback(ir:discord.Interaction): 
            channel = ir.user.voice.channel
            value = ir.data["values"][0]
            name = activities[value][0]
            invite = await channel.create_invite(target_type=discord.InviteTarget.embedded_application,target_application_id=int(value))
            view.clear_items()
            await ir.response.edit_message(content=f"[Click to open {name} in {channel}]({invite.url})",embed=None,view=view)
            
        select.callback=select_callback
        for key,value in activities.items():
            id = key
            emoji = get(emojis,name=id)
            select.add_option(label=value[0],value=key,description=value[1],emoji=emoji) 
        view.add_item(select)
        
        embed = discord.Embed(
            title="Activity",
            description="[`Starts`](https://discord.gg/xesty) an activity to play with your friends in the VC (Desktop Only).\n\n**Usage:**\n・[`Dropdown Menu`](https://discord.gg/xesty): Select an activity to start from the menu",color=3092790)
        await i.response.send_message(embed=embed,view=view,ephemeral=True)
        async def on_timeout():
            view.clear_items()
            await i.edit_original_message(view=view)
        view.on_timeout=on_timeout
    async def whitelist(self,i):
        user= i.user
        if not user.voice or not user.voice.channel:
            embed = discord.Embed(color=3092790,description=f"**You aren't connected to a voice channel**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.voice.channel.category_id !=979681214787121192:
            embed = discord.Embed(color=3092790,description=f"**The interface only works for join to create channels**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        data = await self.client.vm.find_one({"channel":user.voice.channel.id})
        if not data:
            embed = discord.Embed(color=3092790,description=f"**The channel wasn't registered in the database. Contact the staff for more info!**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.id !=data["_id"]:
            owner = user.guild.get_member(data["_id"])
            embed = discord.Embed(color=3092790,description=f"**Only owner of the voice channel ({owner.mention}) can access the feature**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        embed=discord.Embed(color=3092790,title="Whitelist",description="[`Whitelists`](https://discord.gg/xesty) an user and lets em join even if the channels locked or ghosted.\n\n**Usage:**\n・[`Add`](https://discord.gg/xesty): Click the button to whitelist a member\n・[`Remove`](https://discord.gg/xesty): Click the button to unwhitelist a member\n・[`List`](https://discord.gg/xesty): Click the button to see all the whitelisted members")
        view=View()
        add=Button(label="Add",custom_="vm_whitelist_add")
        remove=Button(label="Remove",custom_="vm_whitelist_remove")
        wlist=Button(label="List",custom_="vmwhitelists")
        view.add_item(add)
        view.add_item(remove)
        view.add_item(wlist)
        async def add_callback(ir):
            modal = Modal(title="Whitelist")
            text = TextInput(label="Add Member",placeholder="Enter the ID or the username",required=True)
            async def text_callback(irr:discord.Interaction):
                x = text.value
                view.clear_items()
                view.add_item(list)
                member = user.guild.get_member_named(x) or user.guild.get_member(int(x))
                if not member:
                    embed.description = f"**Whitelisted** `0` member\n**Reason:\n**・Member not found\n\n**Usage:**\n・[`List`](https://discord.gg/xesty): Click the button to see all the whitelisted members."
                    await ir.response.edit_message(embed=embed,view=view)
                    return
                overwrite = user.voice.channel.overwrites_for(member)
                overwrite.connect=True
                overwrite.view_channel=True
                await user.voice.channel.set_permissions(member,overwrite=overwrite)
                if member.id in data["whitelist"]:
                    embed.description = f"**Whitelisted** `0` members\n**Reason:\n**・The member already is whitelisted\n\n**Usage:**\n・[`List`](https://discord.gg/xesty): Click the button to see all the whitelisted members."
                    await ir.response.edit_message(embed=embed,view=view)
                    return
                
                data["whitelist"].append(member.id)
                await self.client.vm.replace_one({"_id":user.id},data)
                
                embed.description = f"**Whitelisted** {member.mention}\n\n**Usage:**\n・[`List`](https://discord.gg/xesty): Click the button to see all the whitelisted members."
                await irr.response.edit_message(embed=embed,view=view)
            modal.on_submit=text_callback
            modal.add_item(text)
            await ir.response.send_modal(modal)
        async def remove_callback(ir):
            modal = Modal(title="Whitelist")
            text = TextInput(label="Remove Member",placeholder="Enter the ID or the username",required=True)
            async def text_callback(irr:discord.Interaction):
                x = text.value
                view.clear_items()
                view.add_item(list)
                member = user.guild.get_member_named(x) or user.guild.get_member(int(x))
                if not member:
                    embed.description = f"**Unwhitelisted** `0` members\n**Reason:\n**・Member not found\n\n**Usage:**\n・[`List`](https://discord.gg/xesty): Click the button to see all the whitelisted members."
                    await ir.response.edit_message(embed=embed,view=view)
                    return
                if not member.id in data["whitelist"]:
                    embed.description = f"**Unwhitelisted** `0` members\n**Reason:\n**・The member is not whitelisted\n\n**Usage:**\n・[`List`](https://discord.gg/xesty): Click the button to see all the whitelisted members."
                    await ir.response.edit_message(embed=embed,view=view)
                    return
                
                overwrite = user.voice.channel.overwrites_for(member)
                overwrite.connect=None
                overwrite.view_channel=None
                await user.voice.channel.set_permissions(member,overwrite=overwrite)
                data["whitelist"].remove(member.id)
                await self.client.vm.replace_one({"_id":user.id},data)
                
                embed.description = f"**Unwhitelisted** {member.mention}\n\n**Usage:**\n・[`List`](https://discord.gg/xesty): Click the button to see all the whitelisted members."
                await irr.response.edit_message(embed=embed,view=view)
            modal.on_submit=text_callback
            modal.add_item(text)
            await ir.response.send_modal(modal)
        async def list_callback(ir):
            d = data["whitelist"]
            if len(d)==0:
                view.clear_items()
                await ir.response.edit_message(content="No members are whitelisted.",embed=None,view=view)
                return
            embed,pages = await self.page(ir,1,d)
            embed.title ="Whitelists"
            if pages >1:
                embed.set_footer(text=f"1/{pages}")
                previous = Button(label="Previous", custom_id=f"whitelist_prev",style=discord.ButtonStyle.grey,disabled=True)
                next = Button(label="Next", custom_id=f"whitelist_next",style=discord.ButtonStyle.grey)
                view = View(timeout=120)
                view.add_item(previous)
                view.add_item(next)
        
                async def previous_callback(irr:discord.Interaction):
                    page = int(irr.message.embeds[0].footer.text.split("/")[0])
                    view.children[1].disabled=False
                    if page==2:
                        view.children[0].disabled=True
                    embedp,pagesp = await self.page(page-1,d)
                    embedp.set_footer(text=f"{page-1}/{pagesp}")
                    embedp.title ="Whitelists"
                    await irr.response.edit_message(embed=embedp,view=view)
                async def next_callback(irr:discord.Interaction):
                    page = int(irr.message.embeds[0].footer.text.split("/")[0])
                    
                    view.children[0].disabled=False
                    if pages-1 ==page:
                        view.children[1].disabled=True
                    embedn,pagesp = await self.page(page+1,d)
                    embedn.set_footer(text=f"{page+1}/{pagesp}")
                    embedn.title ="Whitelists"
                    await irr.response.edit_message(embed=embedn,view=view)
                previous.callback= previous_callback
                next.callback= next_callback
                
                await ir.response.edit_message(embed=embed,view=view)                
            else:
                view.clear_items()
                await ir.response.edit_message(embed=embed,view=view)                
                
        add.callback= add_callback
        remove.callback=remove_callback
        wlist.callback= list_callback
        await i.response.send_message(embed=embed,view=view,ephemeral=True)
        async def on_timeout():
            view.clear_items()
            await i.edit_original_message(view=view)
        view.on_timeout=on_timeout
        return
    async def delete(self,i):
        user= i.user
        if not user.voice or not user.voice.channel:
            embed = discord.Embed(color=3092790,description=f"**You aren't connected to a voice channel**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.voice.channel.category_id !=979681214787121192:
            embed = discord.Embed(color=3092790,description=f"**The interface only works for join to create channels**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        data = await self.client.vm.find_one({"channel":user.voice.channel.id})
        if not data:
            embed = discord.Embed(color=3092790,description=f"**The channel wasn't registered in the database. Contact the staff for more info!**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        if user.id !=data["_id"]:
            owner = user.guild.get_member(data["_id"])
            embed = discord.Embed(color=3092790,description=f"**Only owner of the voice channel ({owner.mention}) can access the feature**")
            await i.response.send_message(embed=embed,ephemeral=True)
            return
        view=View()
        button = Button(label="Confirm",custom_id="vm_delete_confirm",button=discord.ButtonStyle.green)
        view.add_item(button)
        async def button_callback(ir):
            await user.voice.channel.delete()
            await self.client.vm.delete_one({"_id":user.id})
            await ir.response.edit_message(content=f"Deleted the VC",embed=None,view=view)
            
        embed = discord.Embed(color=3092790,title="Delete",description="[`Deletes`](https://discord.gg/xesty) the VC and all the user settings permanently. You can still make new VCs.**Usage:**\n・[`Confirm`](https://discord.gg/xesty): Click the button to delete the VC.")
        await i.response.send_message(embed=embed,view=view,ephemeral=True)
        async def on_timeout():
            view.clear_items()
            await i.edit_original_message(view=view)
        view.on_timeout=on_timeout
        return
    async def page(self,page:int,data):
        items_per_page = 10
        pages = math.ceil(len(data) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, id in enumerate(data[start:end], start=start):
            try:
                member = await self.client.fetch_user(id)
            except:
                continue
            queue += f'`{i+1}.` {member.mention} ({member.id})\n'

        embed = (discord.Embed(description='{}'.format(queue),color=3092790)
                .set_footer(text='page {}/{}'.format(page, pages)))
        return (embed,pages)
    @commands.command()
    async def vmsetup(self,ctx):
        view=View()
        guild = self.client.get_guild(944557938914263060)
        embed=discord.Embed(color=3092790,title="Xesty VoiceMaster",description="Click the buttons below to manage your voice channel\n\n**Button Usage**\n")
        emojis = guild.emojis
        desc = {
"rename": "[`Rename`](https://discord.gg/xesty) the voice channel",
"lock": "[`Lock`](https://discord.gg/xesty) the voice channel",
"unlock": "[`Unlock`](https://discord.gg/xesty) the voice channel",
"ghost": "[`Hide`](https://discord.gg/xesty) the voice channel",
"unghost": "[`Unhide`](https://discord.gg/xesty) the voice channel",
"ban": "[`Ban`](https://discord.gg/xesty) a member from the voice channel",
"unban": "[`Unban`](https://discord.gg/xesty) a member from the voice channel",
"whitelist": "[`Whitelist`](https://discord.gg/xesty) a member",
"activity": "[`Start`](https://discord.gg/xesty) an activity in the voice channel",
"delete": "[`Delete`](https://discord.gg/xesty) the voice channel",

        }
        for key in list(desc.keys()):
            emoji = get(emojis,name=key)
            if key =="ban":
                emoji = get(emojis,id=981429215385776158)
                
            button = Button(custom_id=f"vm{key}",emoji=emoji)
            embed.description+=f"{emoji} {desc[key]}\n"
            view.add_item(button)
        await ctx.send(embed=embed,view=view)
        
        
        
    @commands.command()
    @commands.is_owner()
    async def delete_all(self,ctx):
        a=await self.client.vm.delete_many({})
        await ctx.send(a)
 
async def setup(bot):
    await bot.add_cog(VM(bot))