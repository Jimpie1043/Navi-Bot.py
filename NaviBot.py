    #Imports
import random
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, bot_has_permissions
import configparser
import pytube
import os
import sys


    #Initializing the bot
config = configparser.ConfigParser()
config.read(r'C:\Users\super\OneDrive\Bureau\Python-Projects\Navi-Bot\config.txt')
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
    print('Logged in as {0.user}'.format(bot))       #Returns this message when the bot goes online
    await bot.get_channel(1030245888154665000).send('Back online!')     #Sends message in a specific channel
    songs = [
        'Rhythm Doctor OST - wish i could care less (ft. Yeo)',
        "Breakbot - Baby I'm Yours (feat. Irfane)",
        'Discord (Remix) - Eurobeat Brony',
        'Warframe | We All Lift Together',
        'NOMA - Brain Power',
        'GLORYHAMMER - Hootsforce (Official Video) | Napalm Records',
        'ECHO【Gumi English】Crusher-P: The Living Tombstone Remix',
        'ロストアンブレラ',
        'Terraria Calamity Mod Music - "1NF3S+@+!0N" - Theme of Crabulon',
        'Legend (ft. Backchat)',
        'Fall Out Boy - Centuries',
        'Goddess (feat. Nonon)',
        'Hammer And The Anvil',
        'Wii Shop Channel [Eurobeat Remix]',
        "Kirby's Dreamland 3 - Sand Canyon 1",
        'Super Smash Bros. Ultimate - Lifelight [Eurobeat Remix]',
        "CYBERPUNK 2077 SOUNDTRACK - WHO'S READY FOR TOMORROW by Rat Boy & IBDY",
        'Mario Kart DS - Waluigi Pinball [Eurobeat Remix]',
        'Bury The Heart(Gigachad Vergil)',
        '20201005~20201007',
        "Windows XP Theme but it's an rpg soundtrack (full version)",
        'Driftveil City - Pokémon Black & White (Metal Cover by RichaadEB)',
        'Sonic Boom/Snake Pit ~ Brass Fanfare',
        '【東方Vocal】【東方永夜抄】Silver Forest Lunatic EURO'
    ]
    rand_song = random.choice(songs)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=rand_song))      #Changes the bot's displayed status to a random song from the list


@bot.event
async def on_message(message):      #This section of code will create a log of all messages in the server
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')
    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    await bot.get_channel(1031492160404594698).send(f'Hey <@!{member.id}>! Welcome to {member.guild.name} <:Cool:1031669832845901965>')     #Send welcome message


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


@bot.command(name='download_mp3', aliases = ['download.mp3', 'download_audio'], description='Download a video from youtube as a .mp3 file.')
async def download_mp3(ctx, url):        #Download yt audio command
    if listening == True:       #Will be set to False if !disconnect is used
        yt = pytube.YouTube(url)
        stream = yt.streams.first()
        stream.download(output_path=r'D:\Downloads\videos', filename='video.mp3')
        await ctx.send(file=discord.File(r'D:\Downloads\videos\video.mp3'))
        os.remove(r'D:\Downloads\videos\video.mp3')


@bot.command(name='download_mp4', aliases=['download.mp4', 'download_video'], description='Download a video from youtube as a .mp4 file.')
async def download_mp4(ctx, url):        #Download yt video command
    if listening == True:       #Will be set to False if !disconnect is used
        yt = pytube.YouTube(url)
        stream = yt.streams.first()
        stream.download(output_path=r'D:\Downloads\videos', filename='video.mp4')
        await ctx.send(file=discord.File(r'D:\Downloads\videos\video.mp4'))
        os.remove(r'D:\Downloads\videos\video.mp4')


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
            except: # Error handler
                await ctx.send('Please enter a valid integer as amount.')
            else:
                await ctx.channel.purge(limit=amount)


"""@bot.command(name='prefix', description="Change the bot's prefix.")
@has_permissions(administrator=True)
@commands.guild_only()
async def prefix(ctx, prefix=''):        #Prefix command
    if listening == True:       #Will be set to False if !disconnect is used
        custom_prefix[ctx.guild.id] = prefix.split() or default_prefix      #Changes the prefix for all commands
        await ctx.send(f'Prefix changed to "{prefix}"!')"""


    #Running the bot
bot.run(token)