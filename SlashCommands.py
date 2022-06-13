import discord
import requests
import os
import json
import typing
token = os.environ['TOKEN']
application_id = "865841283343450122"
api_url = f"https://discord.com/api/v9/applications/{application_id}/commands"
header = {"Authorization": f"Bot {token}"}
class SlashCore:
    async def get_commands():
        bot_commands = []
        url = f"https://discord.com/api/v9/applications/{application_id}/commands"
        r = requests.get(url,headers=header)
        return r.json()
        return bot_commands
    async def run_func(ctx): 
        func = ctx.command_name
        command = ctx.client.get_command(func)
        await command(ctx)

    

        