import discord
import requests
import os
import json
import typing
token = os.environ['TOKEN']
application_id = "865841283343450122"
api_url = f"https://discord.com/api/v9/applications/{application_id}/commands"
header = {"Authorization": f"Bot {token}"}
class Followup:
    def __init__(self,client,session,data,token):
        try:
            self._id = data["id"]
            self._token = token
            self._type = data["type"]
            self._application_id = data["application_id"]
            self._webhook_id = data["webhook_id"]
            self._content = data["content"]
            self._embeds = data["embeds"]
            self._channel_id = data["channel_id"]
            self._guild_id = data["message_reference"]["guild_id"]
            self._message_reference_id = data["message_reference"]["message_id"]
            self._client = client
            self._author_id = data["author"]["id"]
            self._flags = data["flags"]
            self._attachments = data["attachments"]
            self._mentions = data["mentions"]
            self._mention_roles = data["mention_roles"]
            self.request = session
        except Exception as e:
            print(e)
    @property
    def client(self):
        return self._client
    @property
    def message_id(self):
        return self._id
    @property
    def token(self):
        return self._token
    @property
    def type(self):
        return self._type
    @property
    def application_id(self):
        return self._application_id
    @property
    def webhook_id(self):
        return self._webhook_id
    @property
    def content(self):
        return self._guild
    @property
    def embeds(self):
        if len(self._embeds)>0:
            embeds = []
            for embed in self._embeds:
                embed = discord.Embed.from_dict(embed)
                embeds.append(embed)
            return embeds
        else:
            return self._embeds
    @property
    def channel_id(self):
        return self._channel_id
    @property
    def guild_id(self):
        return self._guild_id
    @property
    def message_reference_id(self):
        return self._message_reference_id
    @property
    def author_id(self):
        return self._author_id
    @property
    def flags(self):
        return self._flags
    @property
    def attachments(self):
        return self._attachments
    @property
    def mentions(self):
        return self._mentions
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
        url = f"https://discord.com/api/v9/webhooks/{self._application_id}/{self.token}/messages/{self.message_id}"
        self.request.patch(url, json=message)
        
    async def delete(self):
        url = f"https://discord.com/api/v9/webhooks/{self._application_id}/{self.token}/messages/{self.message_id}"
        self.request.delete(url, headers=header)
        
class ActionRow:
    def __init__(self,components:list):
        self._components = components
    def to_dict(self):
        ar = {}
        ar["type"] = 1
        components=ar["components"] = []
        for component in self._components:
            x = component.to_dict()
            components.append(x)
        return ar
    @classmethod
    def from_dict(cls,data):
        components = []
        for component in data["components"]:
            if component["type"] ==2:
                x = Button.from_dict(component)
                components.append(x)
            else:
                x = SelectMenu.from_dict(component)
                components.append(x)
        return cls(components=components)
class PEmoji:
    def __init__(self,data):
        self._id = data["id"]
        self._name = data["name"]
        try:
            self._animated = data["animated"]
        except KeyError:
            self._animated = False
    @property
    def id(self):
        return self._id
    @property
    def name(self):
        return self._name
    @property
    def animated(self):
        return self._animated
class Button:
    def __init__(self,label:str=None,emoji:typing.Union[discord.PartialEmoji,PEmoji]=None,custom_id:str=None,url:str=None,style:int=2,disabled:bool=False):
        self._label = label
        self._emoji = emoji
        self._custom_id = custom_id
        self._url = url
        self._style = style
        self._disabled = disabled
        
    def to_dict(self):
        button = {}
        button["type"] = 2 
        button["style"] = self._style
        if self._label: 
            button["label"] = self._label 
        if self._emoji:
            button["emoji"] = {"name":self._emoji.name,"id":self._emoji.id,"animated":self._emoji.animated}
        if self._style == 5:
            button["url"] = self._url
        else:
            button["custom_id"]= self._custom_id
        button["disabled"] = self._disabled
        return button
    @classmethod
    def from_dict(cls,data):
        try:
            emoji = PEmoji(data["emoji"])
        except KeyError:
            emoji = None
        try:
            disabled = data["disabled"]
        except KeyError:
            disabled = False
        style = data["style"]
        if style == 5:
            url = data["url"]
            custom_id = None
        else:
            url =None
            custom_id = data["custom_id"]
        return cls(label = data["label"],emoji = emoji,style = style,custom_id=custom_id,url=url,disabled=disabled)

class MenuOption:
    def __init__(self,label:str,value:str, description: typing.Optional[str]=None, emoji: discord.PartialEmoji=None, default:bool=False):
        self._label = label
        self._value = value
        self._description = description
        self._emoji = emoji
        self._default = default
    def set_as_default(self):
        self._default = True 
    def to_dict(self):
        menuoptions = {}
        menuoptions['label'] = self._label
        menuoptions['value'] = self._value
        if self._description:
            menuoptions['description'] = self._description
        if self._emoji:
            menuoptions['emoji'] = {"name": self._emoji.name, "id": self._emoji.id, "animated": self._emoji.animated}
        menuoptions['default'] = self._default
        return menuoptions
    @classmethod
    def from_dict(cls,data):
        label = data["label"]
        value = data["value"]
        try:
            emoji = PEmoji(data["emoji"])
        except KeyError:
            emoji = None
        try:
            desc = PEmoji(data["description"])
        except KeyError:
            desc = None
        try:
            default = data["default"]
        except KeyError:
            default = False    
        return cls(label =label,value=value,emoji=emoji,description=desc,default=default)

class SelectMenu:														
    def __init__(self,custom_id:str,options:list,placeholder:typing.Optional[str]=None,min_values:int=1,max_values:int=1,disabled:bool=False):
        self._custom_id = custom_id
        self._options = options
        self._placeholder = placeholder
        self._min_values = min_values
        self._max_values = max_values
        self._disabled = disabled
        
    def to_dict(self):
        selectmenu = {}
        selectmenu["type"] = 3
        selectmenu["custom_id"] = self._custom_id
        options=selectmenu["options"] = []
        for option in self._options:
            x = option.to_dict()
            options.append(x)
        if self._placeholder: 
            selectmenu["placeholder"] = self._placeholder
        else:
            selectmenu["placeholder"] = "Select from the menu" 
        selectmenu["min_values"] = self._min_values
        selectmenu["max_values"] = self._max_values
        selectmenu["disabled"] = self._disabled
        return selectmenu
    @classmethod
    def from_dict(cls,data):
        try:
            placeholder = data["placeholder"]
        except KeyError:
            placeholder = None
        try:
            disabled = data["disabled"]
        except KeyError:
            disabled = False
        try:
            min_values = data["min_values"]
        except KeyError:
            min_values = 1
        try:
            max_values= data["max_values"]
        except KeyError:
            max_values = 1
        options = []
        for option in data["options"]:
            x = MenuOption.from_dict(option)
            options.append(x)
        custom_id=data["custom_id"]
        return cls(custom_id=custom_id,options=options,placeholder=placeholder,min_values=min_values,max_values=max_values,disabled=disabled)