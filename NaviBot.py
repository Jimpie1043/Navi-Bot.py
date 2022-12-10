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
from pytube import Playlist
from pytz import timezone
from termcolor import colored

    #Initializing the bot
file_location = r'C:\Users\super\Desktop\PythonProjects\Navi-Bot'     #The location of the bot's files
main_channel = 1051041777211158628      #The channel the bot will connect to (should be private)

config = configparser.ConfigParser()
config.read(rf'{file_location}\config.txt')
token = config.get('CONFIG', 'DISCORD_TOKEN')
intent = discord.Intents.all()
intent.members = True
intent.message_content = True
default_prefix = '!'
bot = commands.Bot(command_prefix=default_prefix, intents = intent)        #Sets the prefix and intents for all commands
listening = True        #If this is set to False, the bot won't listen to any command, except for !connect which turns this variable back to True and !exit which exits the code completely


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
    if listening == True:       #Will be set to False if !disconnect is used
        await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
    else:
        await ctx.send(f"I am currently set to answer <@!309650289932369922>'s commands only. Please try again later.")


#Download_mp3 variables
global download_mp3_limit
download_mp3_limit = 5       #Limits the !download_mp3 command
global download_mp3_uses
download_mp3_uses = 0       #Represents the amount of times the !download_mp3 command is being used


@bot.command(name='download', description='Download a video from youtube as a .mp3 file.')
async def download(ctx, url):        #Download yt audio command
    if listening == True:       #Listening will be set to False if !disconnect is used
        global download_mp3_uses
        download_mp3_uses += 1
        if download_mp3_uses <= download_mp3_limit:       #Represents the amount of times this command is being used at a time compared to the limit that is allowed (default is 1)
            yt = pytube.YouTube(url)
            filesize = yt.streams.first().filesize
            if filesize < 24000000:       #Checks if the file is bigger than 24 MB
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
            else:
                await ctx.send(f'Error: File is bigger than 24 MB. Maximum video length is about 40 minutes.')
                sleep(3)
                download_mp3_uses -= 1
        else:
            await ctx.send(f'Please do not spam this command!')
            sleep(3)
            download_mp3_uses -= 1
    else:
        await ctx.send(f"I am currently set to answer <@!309650289932369922>'s commands only. Please try again later.")


@bot.command(name='download_playlist', aliases = ['playlist_download'], description='Download all the videos from a youtube playlist as .mp3 files.')
async def download_playlist(ctx, playlist_url):        #Download playlist audio command
    if listening == True:       #Listening will be set to False if !disconnect is used
        playlist = Playlist(playlist_url)
        await ctx.send(f'Downloading all videos from "{playlist.title}"')
        for video in playlist.videos:
            filesize = video.streams.first().filesize
            if filesize < 24000000:       #Checks if the file is bigger than 24 MB
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
            else:
                await ctx.send(f'Error: File is bigger than 24 MB. Max video length is about 40 minutes.')
    else:
        await ctx.send(f"I am currently set to answer <@!309650289932369922>'s commands only. Please try again later.")


@bot.command(name='clear', aliases=['purge'], description='Deletes the specified amount of messages in a channel.')
@has_permissions(manage_messages=True)
@bot_has_permissions(manage_messages=True)
async def clear(ctx, amount=None):       #Clear command (default value is None)
    if listening == True:
        if amount == None:
            await ctx.channel.purge(limit=1000000)
        else:
            try:
                int(amount)
            except:     #Error handler
                await ctx.send('Please enter a valid integer as the amount of messages to clear.')
            else:
                await ctx.channel.purge(limit=int(amount))
    else:
        await ctx.send(f"I am currently set to answer <@!309650289932369922>'s commands only. Please try again later.")


#!play command variables
global play_limit
play_limit = 1       #Limits the !play command to n uses
global play_uses
play_uses = 0       #Represents the amount of times the !play command is being used
global song_list
song_list = []      #Creates a list of youtube url's. Every time you use the !play command, the url will get added to the list and be used for the next song
global song_number
song_number = 0


async def after_play(ctx, file_name):       #After song stops playing in !play command
    global file_location
    os.remove(rf'{file_location}\videos\{file_name}')
    global song_list
    if list != []:
        await play(ctx, song_list[0])       #If the list is not empty, plays the next song in the list after the bot is done playing the current song and removes it from the list
        song_list.remove[0]



async def play_download_mp3(ctx, url, vc):      #Download and play the .mp3 file for the !play command
    yt = pytube.YouTube(url)
    filesize = yt.streams.first().filesize
    if filesize < 24000000:       #Checks if the file is bigger than 24 MB
        title = yt.streams[0].title
        if filesize > 12000000:     #If we're dealing with a bigger file, display longer download time
            await ctx.send(f'Downloading "{title}". This could take up to 30 seconds.')
        elif filesize > 6000000:
            await ctx.send(f'Downloading "{title}". This should take less than 20 seconds.')
        stream = yt.streams.first()
        global song_number
        file_name = f'video{song_number}.mp3'       #What the file is going to be saved as in the computer
        stream.download(output_path=rf'{file_location}\videos', filename=file_name)
        await ctx.send(f'Playing "{title}" in {vc}.')
        print(vc)
        connected = await vc.connect()
        connected.play(discord.FFmpegPCMAudio(executable='ffmpeg.exe', source=rf'{file_location}\videos\{file_name}'), after=lambda e: (await after_play(ctx, file_name) for _ in '_').__anext__())
                #Plays the song that's been downloaded and goes to after_play() after it's done
        sleep(5)        #5 second delay to prevent anyone from spamming this command
        return
    else:
        await ctx.send(f'Error: File is bigger than 24 MB. Max video length is about 40 minutes.')
        sleep(3)
        return


@bot.command(name='play', description='Plays music in the vc where users are currently connected.')
async def play(ctx, url):        #Play command
    if listening == True:       #Will be set to False if !disconnect is used
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild) # This allows for more functionality with voice channels
        if voice != None:       #If bot is currently playing something, add url to the list
            global song_list
            song_list += url
        else:
            global play_uses
            play_uses += 1
            if play_uses <= play_limit:       #Represents the amount of times this command is being used at a time compared to the limit that is allowed (default is 1)
                if ctx.author.voice and ctx.author.voice.channel:
                    play_uses -= 1
                    vc = ctx.author.voice.channel
                    await play_download_mp3(ctx, url, vc)
                    return
                else:
                    await ctx.send(f'You need to be in a vc or to specify the name of the vc to use this command!')
                    play_uses -= 1
            else:
                await ctx.send(f'Please do not spam this command!')
                sleep(3)
                play_uses -= 1
    else:
        await ctx.send(f"I am currently set to answer <@!309650289932369922>'s commands only. Please try again later.")
        play_uses -= 1


@bot.command(name='playlist', description='Shows you a list of the songs that are about to play.')
async def playlist(ctx):        #List command
    if listening == True:
        global song_list
        await ctx.send(f"Here's the current playlist: {song_list}")
    else:
        await ctx.send(f"I am currently set to answer <@!309650289932369922>'s commands only. Please try again later.")
        play_uses -= 1


    #Running the bot
"""def printEveryNSeconds():       #Prints the value of something every 5 seconds if you need to debug
  threading.Timer(5.0, printit).start()
  global play_uses
  print(play_uses)
printEveryNSeconds()"""



bot.run(token)