import discord
import os
from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get
import json
import urllib.request
import urllib.error
import ffmpeg
import re
import praw
import time
from pystreamable import StreamableApi

Client = discord.Client()
bot_prefix = "!"
client = commands.Bot(command_prefix=bot_prefix)
reddit = praw.Reddit(client_id = 'Tr5ZjYeYiKW7ug', client_secret = 'LSpNRsz_W5yBEVaDUZ_znCxbvyg', username = 'ABotCreator', password = 'BotsAreGreat', user_agent = 'RedditVidsBotv1')
api = StreamableApi("ABotCreator@gmail.com","BotsAreGreat")
vid_str = None
embedVar = None
@client.event
async def on_ready():
    print("Bot Online")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))

@client.command()
async def embedVid(ctx,link):
    global vid_str
    submission = reddit.submission(url=link)
    embedVar = discord.Embed(
        title = submission.title,
        description = submission.selftext,
        colour = ctx.message.author.color
    )
    embedVar.add_field(name='Subreddit',value=submission.subreddit)
    embedVar.add_field(name='Author',value=submission.author)
    embedVar.set_footer(text="Requested by " + ctx.message.author.name)
    vid_str= submission.media["reddit_video"]["fallback_url"]
    audio_str = re.sub("_.*\.mp4","_audio.mp4",vid_str)
    message=await ctx.send("Processing the video, please wait")
    urllib.request.urlretrieve(vid_str, 'video.mp4') 
    urllib.request.urlretrieve(audio_str, 'audio.mp4')
    vid=ffmpeg.input("./video.mp4")
    audio=ffmpeg.input("./audio.mp4")
    title = submission.title
    for e in title:
        if not e.isalnum():
            e = '_'
    ffmpeg.concat(vid,audio,v=1,a=1).output("./"+title+".mp4").run()
    await message.delete()
    if os.stat("./"+title+".mp4").st_size < 8000000:
        message = await ctx.send("The video file is currently being uploaded, please wait")
        await ctx.send(file=discord.File("./"+title+".mp4"))
        await message.delete()
    else:
        message = ctx.send("The video is larger than 8MB, please wait while its uploading to Streamable")
        global api
        vid_dict = api.upload_video("./"+title+".mp4",title)
        await message.delete()
        time.sleep(5)
        await ctx.send("https://www.streamable.com/"+vid_dict['shortcode'])
    await ctx.send(embed=embedVar)
    os.remove("./video.mp4")
    os.remove("./audio.mp4")
    os.remove("./"+title+".mp4")

@embedVid.error
async def embedVid_error(ctx,error):
    if isinstance(error,commands.CommandInvokeError):
        if (isinstance(error.original,urllib.error.HTTPError)):
            if error.original.code == 403:
                global vid_str
                global embedVar
                await ctx.send(vid_str,embed=embedVar)
        else:
            await ctx.send(type(error.original))
    else:
        await ctx.send(type(error))



client.run("NzM1NTYwMzkyMTk3MTQ0NjEz.XxiCDw.vg4LDy8wD7NVT_ifXBBBswttiiY")
