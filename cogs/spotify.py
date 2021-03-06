import discord
from discord.ext import commands
import asyncio
import requests
import spotipy
import time
import json
# import selenium
import os
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium import webdriver
# import webdriver_manager
# from webdriver_manager.chrome import ChromeDriverManager



class Spotify(commands.Cog):
    token = os.environ['TOKEN']
    application_id = "865841283343450122"
    api_url = f"https://discord.com/api/v9/applications/{application_id}/commands"
    header = {"Authorization": f"Bot {token}"}
    def __init__(self, client):
        self.client = client
        self.request = requests.Session()
        self.db = client.db["spotify"]
        self.auth = spotipy.oauth2.SpotifyOAuth(username=os.environ["su"],scope="playlist-modify-public",client_id=os.environ["sid"],client_secret=os.environ["scs"],redirect_uri='http://localhost:8888',open_browser=False)
    async def backend(self):
        ti = self.auth.get_cached_token()
        if ti:
            access_token = ti['access_token']
        else:
            data = await self.db.find_one({"_id":"spotify"})
            if not data:
                data ={}
                data["songs"]={}
                data["auth"]=None
            try:
                code_url=data["auth"]
            except:
                data["auth"]=None
            code=self.auth.parse_response_code(code_url)
            # url = self.auth.get_authorize_url()
            # chrome_options = Options()
            # chrome_options.add_argument('--headless')
            # chrome_options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")
            # chrome_options.add_argument('--no-sandbox')
            # chrome_options.add_argument('--disable-dev-shm-usage')
            # # chrome_options.add_argument("--incognito")
            # web = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=chrome_options)
            # web.get(url)
            # await asyncio.sleep(3)
            # code_url =web.current_url
            # print(code_url)
            # code=self.auth.parse_response_code(code_url)
            # print(code)
            access_token= self.auth.get_access_token(code,as_dict=False)
        return spotipy.Spotify(auth=access_token)
    @commands.group(invoke_without_command=True)
    async def song(self,ctx):
        return
    @song.command()
    @commands.is_owner()
    async def auth(self,ctx):
        url = self.auth.get_authorize_url()
        embed=discord.Embed(description=f"[Auth Url]({url})")
        await ctx.send(embed=embed)
    @song.command()
    @commands.is_owner()
    async def login(self,ctx,*,x:str):
        await ctx.message.delete()
        data = await self.db.find_one({"_id":"spotify"})
        if not data:
            data ={}
            data["songs"]={}
            data["auth"]=None
        data["auth"]=x
        await self.db.replace_one({"_id":"spotify"},data,True)
        await ctx.send("Added the login token!")
        
    @song.command()
    async def add(self,ctx,url:str):
        info = await self.db.find_one({"_id":ctx.author.id})
        data = await self.db.find_one({"_id":"spotify"})
        if not data:
            data ={}
            data["songs"]={}
            data["delay"]=88400
            data["auth"]=None
        if not info:
            info ={}
            info["cooldown"]=0
            info["songs"]={}
        cooldown = info["cooldown"]+data["delay"]
        if cooldown>time.time():
            return await ctx.send(f"You're on cooldown from adding songs. Cooldown ends <t:{cooldown}:R>")
        id = "spotify:track:"+url.split("track/")[1].split("?")[0]
        songs = list(data["songs"].keys())
        if id in songs:
            return await ctx.send("Song already in the playlist.")
        try:
            sp= await self.backend()
        except:
            return await ctx.send('Authorization failed! Contact Danger for authorization.')
        try:
            track = sp.track(id)
        except:
            return await ctx.send("Invalid Song Url")
        song = f'[{track["name"]}]({track["external_urls"]["spotify"]})'
        embed = discord.Embed(
            title="Song Added",
            description=f'**{song}**',
color= 3092790
            
        )
        ar= []
        a=" | "
        for artist in track["artists"]:
            ar.append(f'[{artist["name"]}]({artist["external_urls"]["spotify"]})')
        a=a.join(ar)
        embed.add_field(name="Artists",value=a)
        if track["album"]["album_type"]=="album":
            embed.add_field(name="Album",value=f'[{track["album"]["name"]}]({track["album"]["external_urls"]["spotify"]})')
        if len(track["album"]["images"])>0:
            embed.set_thumbnail(url=track["album"]["images"][0]["url"])
        embed.set_image(url="https://i.imgur.com/8JT8UQG.png")
        embed.set_author(name=str(ctx.author),icon_url=str(ctx.author.display_avatar))
        try:
            sp.playlist_add_items(playlist_id="14wjR1THtXs09VyGiIBJJQ",items=[id])
            info["songs"][id]=[song,time.time()]
            info["cooldown"]= time.time()
            await self.db.replace_one({"_id":ctx.author.id},info,True)
            data["songs"][id]=[ctx.author.id,song,time.time()]
            await self.db.replace_one({"_id":"spotify"},data,True)
        except:
            return await ctx.send("Something went wrong while adding the song to playlist! Contact the staff.")
        log = ctx.guild.get_channel(974948945220485150)
        await log.send(embed=embed)
        await ctx.send("Song Added")
    # @commands.group(invoke_without_command=True)
    # @commands.is_owner()
    # async def remove(self,ctx):
    #     return
    @commands.command()
    async def time(self,ctx,member:discord.Member):
        info = await self.db.find_one({"_id":ctx.author.id})
        info["time"]=0
        await self.db.replace_one({"_id":ctx.author.id},info,True)
        await ctx.send("Done")
    @song.command()
    async def remove(self,ctx,url:str):
        id = "spotify:track:"+url.split("track/")[1].split("?")[0]
        sp= await self.backend()
        if not sp:
            return await ctx.send('Something went wrong! Please contact the staff.')
        info = await self.db.find_one({"_id":ctx.author.id})
        info["time"]=0
        await self.db.replace_one({"_id":ctx.author.id},info,True)
        await ctx.send("Done")

async def setup(client):
    await client.add_cog(Spotify(client))