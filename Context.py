import discord
import requests
import os
import json
import typing
from Messages import Followup, ActionRow

token = os.environ['TOKEN']
application_id = "865841283343450122"
api_url = f"https://discord.com/api/v9/applications/{application_id}/commands"
header = {"Authorization": f"Bot {token}"}
class SlashContext:
	def __init__(self,client,session,data):
		try:
			self._type =2
			self._token = data["token"]
			self._interaction_id = data["id"]
			self._application_id = data["application_id"] 
			self._command_id = data["data"]["id"]
			self._command_name = data["data"]["name"]
			self._options = data["data"]["options"]
			self._guild_id = data["guild_id"] 
			self._channel_id = data["channel_id"]
			self._client = client
			self._member_id = data["member"]["user"]["id"]
			self._guild = client.get_guild(int(self._guild_id))
			self._channel = client.get_channel(int(self._channel_id))
			self.request = session
			self._callback_url =  f"https://discord.com/api/v9/interactions/{self._interaction_id}/{self._token}/callback"
		except Exception as e:
			print(e)
	@property
	def client(self):
		return self._client
	@property
	def command_id(self):
		return self._command_id
	@property
	def command_name(self):
		return self._command_name
	@property
	def token(self):
		return self._token
	@property
	def interaction_id(self):
		return self._interaction_id
	@property
	def application_id(self):
		return self._application_id
	@property
	def member_id(self):
		return int(self._member_id)
	@property
	def guild(self):
		return self._guild
	@property
	def channel(self):
		return self._channel
	@property
	def options(self):
		return self._options
	@property
	def callback_url(self):
		return self._callback_url
	async def member(self):
		member = await self.guild.fetch_member(self.member_id)
		return member
	async def callback(self,content:typing.Optional[str]=None,embed:typing.Optional[discord.Embed]=None,components:list=None,callback_type=4,flags=None):
		message = {}
		message["type"] = callback_type
		data=message["data"] = {}
		if content:
			data["content"] = content
		if embed:
			data["embeds"] = [embed.to_dict()]
		if components:
			comp = data["components"] = []
			for component in components:
				x = component.to_dict()
				comp.append(x)
		if flags:
			data["flags"] = flags
		self.request.post(self.callback_url, json=message)
	async def edit(self,content:typing.Optional[str]=None,embed:typing.Optional[discord.Embed]=None,components:list=None,flags=None):
		data=message= {}
		if content: 
			data["content"] = content
		if embed:
			data["embeds"] = [embed.to_dict()]
		if components:
			comp = data["components"] = []
			for component in components:
				x = component.to_dict()
				comp.append(x)
		if flags:
			data["flags"] = flags
		url = f"https://discord.com/api/v9/webhooks/{self.application_id}/{self.token}/messages/@original"
		self.request.patch(url, json=message)    
	async def followup(self,content:typing.Optional[str]=None,embed:typing.Optional[discord.Embed]=None,components:list=None,flags=None):
		data=message= {}
		if content: 
			data["content"] = content
		if embed:
			data["embeds"] = [embed.to_dict()]
		if components:
			comp = data["components"] = []
			for component in components:
				x = component.to_dict()
				comp.append(x)
		if flags:
			data["flags"] = flags
		url = f"https://discord.com/api/v9/webhooks/{self.application_id}/{self.token}"
		r= self.request.post(url, json=message)    
		followup = Followup(self.client,self.request,r.json(),self.token)
		return followup
	async def delete(self):
		url = f"https://discord.com/api/v9/webhooks/{self.application_id}/{self.token}/messages/@original"
		self.request.delete(url, headers=header)

class ComponentContext:
	def __init__(self,client,session,data):
		try:
			self._type =3
			self._client = client
			self._token = data["token"]
			self._interaction_id = data["id"]
			self._application_id = data["application_id"] 
			self._custom_id = data["data"]["custom_id"]
			self._component_type = data["data"]["component_type"]
			if self._component_type ==3:
				self._values = data["data"]["values"]
			else:
				self._values = None
			self._guild_id = data["guild_id"] 
			self._channel_id = data["channel_id"] 
			self._member_id = data["member"]["user"]["id"]
			self._author_id = data["message"]["author"]["id"]
			self._message_id = data["message"]["id"] 
			self._guild = client.get_guild(int(self._guild_id))
			self._channel = client.get_channel(int(self._channel_id))
			self._author = self._guild.get_member(int(self._author_id))
			self._member = self._guild.get_member(int(self._member_id))
			self._components = data["message"]["components"]
			self.request = session
			self._callback_url =  f"https://discord.com/api/v9/interactions/{self._interaction_id}/{self._token}/callback"
		except Exception as e:
			print(e)
	@property
	def type(self):
		return self._type
	@property
	def client(self):
		return self._client
	@property
	def token(self):
		return self._token
	@property
	def interaction_id(self):
		return self._interaction_id
	@property
	def application_id(self):
		return self._application_id
	@property
	def custom_id(self):
		return self._custom_id
	@property
	def component_type(self):
		return self._component_type
	@property
	def values(self):
		return self._values
	@property
	def guild(self):
		return self._guild
	@property
	def channel(self):
		return self._channel
	@property
	def member_id(self):
		return self._member_id
	@property
	def member(self):
		return self._member
	
	@property
	def author(self):
		return self._author
	@property
	def message_id(self):
		return self._message_id
	@property
	def components(self):
		components=[]
		for component in self._components:
			x = ActionRow.from_dict(component)
			components.append(x)
	@property
	def callback_url(self):
		return self._callback_url
	# async def member(self):
	#     member = await self.guild.fetch_member(self.member_id)
	#     return member
	async def callback(self,content:typing.Optional[str]=None,embed:typing.Optional[discord.Embed]=None,components:list=None,callback_type=4,flags=None):
		message = {}
		message["type"] = callback_type
		data=message["data"] = {}
		if content:
			data["content"] = content
		if embed:
			data["embeds"] = [embed.to_dict()]
		if components:
			comp = data["components"] = []
			for component in components:
				x = component.to_dict()
				comp.append(x)
		if flags:
			data["flags"] = flags
		self.request.post(self.callback_url, json=message)

	async def edit(self,content:typing.Optional[str]=None,embed:typing.Optional[discord.Embed]=None,components:list=None,flags=None):
		data=message= {}
		if content: 
			data["content"] = content
		if embed:
			data["embeds"] = [embed.to_dict()]
		if components:
			comp = data["components"] = []
			for component in components:
				x = component.to_dict()
				comp.append(x)
		if flags:
			data["flags"] = flags
		url = f"https://discord.com/api/v9/webhooks/{self.application_id}/{self.token}/messages/@original"
		self.request.patch(url, json=message)    
	async def followup(self,content:typing.Optional[str]=None,embed:typing.Optional[discord.Embed]=None,components:list=None,flags=None):
		data=message= {}
		if content: 
			data["content"] = content
		if embed:
			data["embeds"] = [embed.to_dict()]
		if components:
			comp = data["components"] = []
			for component in components:
				x = component.to_dict()
				comp.append(x)
		if flags:
			data["flags"] = flags
		url = f"https://discord.com/api/v9/webhooks/{self.application_id}/{self.token}"
		r= self.request.post(url, json=message)   
		followup = Followup(self.client,self.request,r.json(),self.token)
		return followup
	async def delete(self):
		url = f"https://discord.com/api/v9/webhooks/{self.application_id}/{self.token}/messages/@original"
		self.request.delete(url, headers=header)