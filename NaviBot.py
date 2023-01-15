    #Imports
import configparser
import os
import random
import re
import sys
import threading
from datetime import datetime
from time import sleep

import discord
import pytube
from discord.ext import commands
from discord.ext.commands import bot_has_permissions, has_permissions
from pushover import PushoverClient
from pytube import Playlist
from pytz import timezone
from termcolor import colored

    #Initializing the bot   
file_location = os.path.dirname(os.path.realpath(__file__))     #The location of the bot's files
main_channel = 1030245888154665000      #The channel the bot will connect to

config = configparser.ConfigParser()
config.read(rf'{file_location}/config.txt')
discord_token = config.get('CONFIG', 'DISCORD_TOKEN')
pushover_token = config.get('CONFIG', 'PUSHOVER_TOKEN')
pushover_api = config.get('CONFIG', 'PUSHOVER_API')
intent = discord.Intents.all()
intent.members = True
intent.message_content = True
default_prefix = '!'
bot = commands.Bot(command_prefix=default_prefix, intents = intent)        #Sets the prefix and intents for all commands
listening = True        #If this is set to False, the bot won't listen to any command, except for owner only commands


    #Defining events
@bot.event
async def on_ready():
    print(colored('Logged in as {0.user}'.format(bot), "green", attrs=["bold"]))       #Returns this message when the bot goes online
    global main_channel
    await bot.get_channel(main_channel).send('Back online!')     #Sends message in a specific channel
    playlist = Playlist('https://www.youtube.com/playlist?list=PLdQuoZISCj_5xtPcDWPP6AwMwydh-VU4Y')
    songs = []
    for video in playlist.videos:
        songs.append(video.title)
    rand_song = random.choice(songs)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=rand_song))      #Changes the bot's displayed status to a random song from the playlist


@bot.event
async def on_message(message):      #This section of code will create a log of all messages in the server
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = '#' + str(message.channel.name)
    tz = timezone('America/New_York')        #Eastern Time timezone
    message_time = datetime.now(tz)     #Gets the current time with the specified timezone
    formatted_message_time = message_time.strftime("%b-%d-%Y %H:%M:%S")     #Changes the time to the specified format (Ex: Oct-18-2022 13:28:08)
    print(f'{colored(formatted_message_time, "grey")} {colored(channel.upper(), "blue", attrs=["bold"])}    {colored(username, "red", attrs=["bold"])}: {user_message}')
    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    global main_channel
    await bot.get_channel(main_channel).send(f'Hey <@!{member.id}>! Welcome to {member.guild.name} <:Cool:1031669832845901965>')     #Send welcome message


    #Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Error: Required arguments missing.')
        print('Error: Required arguments missing.')

    if isinstance(error, commands.BadArgument):
        await ctx.send('Error: Invalid argument used.')
        print('Error: Invalid argument used.')

    if isinstance(error, commands.NotOwner):
        await ctx.send('Error: Only the owner can use this command!')
        print('Error: Owner command only.')


    #Check if the bot is in a guild
@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


    #Defining commands
@bot.command(name='disconnect', description='Makes the bot go offline. In this state, it will only listen to commands related to the owner of the bot. Use the "connect" command to get it back online. Can only be used by the owner of the bot')
@commands.is_owner()
async def disconnect(ctx):      #Disconnect command
    global listening
    listening = False
    await ctx.send('Disconnecting...')
    await bot.change_presence(status=discord.Status.offline)
    return listening


@bot.command(name='connect', description='Re-connects the bot. Use the "disconnect" command to get it back offline.')
@commands.is_owner()
async def connect(ctx):     #Connect command
    await bot.change_presence(status=discord.Status.online)
    global listening
    listening = True
    await ctx.send('Connecting...')
    return listening


@bot.command(name='exit', description="Shuts down the bot. Can only be used by the owner of the bot")
@commands.is_owner()
async def exit(ctx):        #Shutdown command
    await ctx.send('Shutting the bot down...')
    await bot.close()


@bot.command(name='refresh', aliases=['reload', 'restart', 'relaunch'], description="Reloads the code while it is currently running. Can only be used by the owner of the bot")
@commands.is_owner()
async def refresh(ctx):     #Refresh command
    await ctx.send('Refreshing the bot...')
    os.execv(sys.executable, ['python'] + sys.argv)


@bot.command(name='ping', description='Pings the bot.')
async def ping(ctx):        #Ping command
    if listening != True:       #Will be set to False if !disconnect is used
        await ctx.send(f"I am currently set to answer <@!309650289932369922>'s commands only. Please try again later.")
        return
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
        


#Download_mp3 variables
global download_mp3_limit
download_mp3_limit = 5       #Limits the !download_mp3 command
global download_mp3_uses
download_mp3_uses = 0       #Represents the amount of times the !download_mp3 command is being used


@bot.command(name='download', description='Download a video from youtube as a .mp3 file.')
async def download(ctx, url):        #Download yt audio command
    if listening != True:       #Listening will be set to False if !disconnect is used
        await ctx.send(f"I am currently set to answer <@!309650289932369922>'s commands only. Please try again later.")
        return
    global download_mp3_uses
    download_mp3_uses += 1
    if download_mp3_uses > download_mp3_limit:       #Times this command is being used at a time compared to the limit that is allowed (default is 1)
        await ctx.send(f'Please do not spam this command!')
        sleep(3)
        download_mp3_uses -= 1
        return
    yt = pytube.YouTube(url)
    filesize = yt.streams.first().filesize
    if filesize > 24000000:       #Checks if the file is bigger than 24 MB
        await ctx.send(f'Error: File is bigger than 24 MB. Maximum video length is about 40 minutes.')
        sleep(3)
        download_mp3_uses -= 1
        return
    title = yt.streams[0].title
    if filesize > 12000000:     #If we're dealing with a bigger file, display longer download time
        await ctx.send(f'Downloading "{title}". This could take up to 30 seconds.')
    elif filesize > 6000000:
        await ctx.send(f'Downloading "{title}". This should take less than 20 seconds.')
    else:
        await ctx.send(f'Downloading "{title}"')
    stream = yt.streams.first()
    file_name = re.sub('[^A-Za-z0-9]+', ' ', title)
    global file_location
    stream.download(output_path=rf'{file_location}\videos', filename=f'{file_name}.mp3')
    await ctx.send(file=discord.File(rf'{file_location}\videos\{file_name}.mp3'))
    os.remove(rf'{file_location}\videos\{file_name}.mp3')
    sleep(5)        #5 second delay to prevent anyone from spamming this command
    download_mp3_uses -= 1
        
        


@bot.command(name='download_playlist', aliases = ['playlist_download'], description='Download all the videos from a youtube playlist as .mp3 files.')
async def download_playlist(ctx, playlist_url):        #Download playlist audio command
    if listening != True:       #Listening will be set to False if !disconnect is used
        await ctx.send(f"I am currently set to answer <@!309650289932369922>'s commands only. Please try again later.")
        return
    playlist = Playlist(playlist_url)
    await ctx.send(f'Downloading all videos from "{playlist.title}"')
    for video in playlist.videos:
        filesize = video.streams.first().filesize
        if filesize > 24000000:       #Checks if the file is bigger than 24 MB
            await ctx.send(f'Error: File is bigger than 24 MB. Max video length is about 40 minutes.')
            return
        title = video.streams[0].title
        if filesize > 12000000:     #If we're dealing with a bigger file, display longer download time
            await ctx.send(f'Downloading "{title}". This could take up to 30 seconds.')
        elif filesize > 6000000:
            await ctx.send(f'Downloading "{title}". This should take less than 20 seconds.')
        else:
            await ctx.send(f'Downloading "{title}"')
        stream = video.streams.first()
        file_name = re.sub('[^A-Za-z0-9]+', ' ', title)
        global file_location
        stream.download(output_path=rf'{file_location}\videos', filename=f'{file_name}.mp3')
        await ctx.send(file=discord.File(rf'{file_location}\videos\{file_name}.mp3'))
        os.remove(rf'{file_location}\videos\{file_name}.mp3')
            


@bot.command(name='clear', aliases=['purge'], description='Deletes the specified amount of messages in a channel.')
@has_permissions(manage_messages=True)
@bot_has_permissions(manage_messages=True)
async def clear(ctx, amount=None):       #Clear command (default value is None)
    if listening != True:
        await ctx.send(f"I am currently set to answer <@!309650289932369922>'s commands only. Please try again later.")
        return
    if amount != None:
        try:
            int(amount)
        except:     #Error handler
            await ctx.send('Please enter a valid integer as the amount of messages to clear.')
        else:
            await ctx.channel.purge(limit=int(amount) + 1)
        return
    await ctx.channel.purge(limit=1000000)
        


@bot.command(name='notif', aliases=['notification'], description='Sends a notification on iOS')
@commands.is_owner()
async def notif(ctx, message):        #Notif command
    await ctx.send('Sending a notification...')
    client = PushoverClient(pushover_token, api_token=pushover_api)
    client.send_message(message, title='Navi Bot')


    #Running the bot
"""def printEveryNSeconds():       #Prints the value of something every 5 seconds if you need to debug
  threading.Timer(5.0, printit).start()
  global play_uses
  print(play_uses)
printEveryNSeconds()"""



bot.run(discord_token)