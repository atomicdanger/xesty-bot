import os
# os.system("pip install -U git+https://github.com/Rapptz/discord.py")
import discord
from discord.ext import commands
from waitress import serve
from threading import Thread
from flask import Flask
import os
from motor import motor_asyncio
from discord import app_commands
from discord.ui import Button, View, TextInput, Modal
import datetime

#

app = Flask('')


@app.route('/')
def main():
	return "Your Bot Is Ready"


def run():
	serve(app, host="0.0.0.0", port=8080)


def keep_alive():
	server = Thread(target=run)
	server.start()


keep_alive()

# MY_GUILD = discord.Object(id=910395389172121600)
intents = discord.Intents.all()
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
          command_prefix="x!",
          intents=intents,
          help_command = None,
        application_id=961488558982582352
        )

    async def setup_hook(self):
        link = os.environ["mongodb_uri"]
        mongoClient = motor_asyncio.AsyncIOMotorClient(f"{link}")
        self.db = mongoClient['xesty']
        self.snipe=self.db["snipe"]
        self.vm=self.db["voicemaster"]
        for filename in os.listdir('./cogs'):
            if filename.endswith(".py"):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(filename)
        # self.tree.copy_global_to(guild=MY_GUILD)
        # await self.tree.sync(guild=MY_GUILD)

    async def on_ready(self):
    	print('The bot is working')
    	await self.change_presence(
    			status=discord.Status.dnd,
    			activity=discord.Game("Moderating Xesty"))
client=MyBot()
# async def status_task():
# 	# activity=discord.Streaming(name ='Central W',url="https://discord.gg/roast")
# 	# activity.game = ".gg/roast"
# 	# activity.twitch_name = "Central Moderator"
# 	# await client.change_presence(
# 	# 		status=discord.Status.dnd,
# 	# 		activity=activity)
# 	while True:
# 		await client.change_presence(
# 			status=discord.Status.dnd,
# 			activity=discord.Game("Moderating Xesty"))
		# await asyncio.sleep(5)
		# await client.change_presence(
		# 	status=discord.Status.dnd,
		# 	activity=discord.Activity(type=discord.ActivityType.watching, name="Haunt"))
		# await asyncio.sleep(5)
		# await client.change_presence(
		# 	status=discord.Status.dnd,
		# 	activity=discord.Game('''.gg/haunt'''))
		# await asyncio.sleep(5)

def owners(ctx):
	ids = [420342321746411521,535490443681595392,640405321285632021,549820835230253060]
	id = ctx.author.id
	if id in ids:
		return ctx.author.id
# @client.tree.context_menu(name="Timeout")
# async def timeout(i: discord.Interaction, member: discord.Member):
#     author= i.user
#     modal = Modal(title="Timeout")
#     time = TextInput(label="Time", custom_id=f"mute_time",style=discord.TextStyle.short,placeholder="Period of timeout (Optional)",default=f"5m")
#     reason = TextInput(label="Reason", custom_id=f"mute_reason",style=discord.TextStyle.short,placeholder="Reason for the timeout (Optional)",default=f"Unbanned by {author}: ")
#     embed= discord.Embed(color=3092790)
#     embed.set_image(url="https://i.imgur.com/8JT8UQG.png")
#     embed.set_author(name=str(author),icon_url=str(author.display_avatar))
#     async def text_callback(ir:discord.Interaction):
#         logs = author.guild.get_channel(977873814635560980)
#         x = time.value
#         r = reason.value
#         time_convert = {"s":1, "m":60, "h":3600,"d":86400}
#         tempmute= int(x[:-1]) * time_convert[x[-1]]
#         if tempmute >=2419200:
#             tempmute= 2419199
#             x = "28d"
#         amount = datetime.timedelta(seconds=int(tempmute))
#         await member.timeout(amount,reason=r)
#         embed.title="Timed out"
#         embed.description=f"Successfully timed out {member.mention} `({member.id})`"
#         await ir.response.send_message(embed=embed)
#         embed.description+=f"\n**Moderator: {author.mention}**"
#         await logs.send(embed=embed)
#     modal.add_item(time)
#     modal.add_item(reason)
#     modal.on_submit=text_callback
#     await i.response.send_modal(modal)

@client.command()
@commands.check(owners)
async def load(ctx, extension=None):
	if extension:
		try:
			await client.load_extension(f"cogs.{extension}")
			await ctx.send(f"Class {extension} loaded!")
		except Exception as e:
			await ctx.send(f"Failed to load the Cog: {extension}\n```python\n{e}```")
	else:
		await ctx.send("Please provide a class to load.")


@load.error
async def load_error(ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.send("Only Bot Team Members can use the command!")


@client.command(aliases=["reload"])
@commands.check(owners)
async def r(ctx, extension=None):
	if extension:
		try:
				
				await client.reload_extension(f"cogs.{extension}")
				await ctx.send(f"Class {extension} reloaded!")
		except Exception as e:
				await ctx.send(f"Failed to reload the Cog: {extension}\n```python\n{e}```")
	else:
		await ctx.send("Please provide a class to reload.")


@r.error
async def r_error(ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.send("Only Bot Team Members can use the command!")


@client.command()
@commands.check(owners)
async def unload(ctx, extension=None):
	if extension:
		try:
			await client.unload_extension(f"cogs.{extension}")
			await ctx.send(f"Class {extension} unloaded!")
		except Exception as e:
			await ctx.send(f"Failed to unload the Cog: {extension}\n```python\n{e}```")
	else:
		await ctx.send("Please provide a class to unload.")


@unload.error
async def unload_error(ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.send("Only Bot Team Members can use the command!")


token = os.environ.get("TOKEN")
client.run(token)