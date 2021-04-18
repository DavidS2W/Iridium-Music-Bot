import discord
import random
from discord.ext import commands
import asyncio
from lyrics_extractor import SongLyrics
import DiscordUtils

  
bot = commands.Bot(command_prefix = ';')
bot.remove_command('help')

play_words = ['Now playing', 'Now streaming audio for', 'Currently belting out the lyrics of', 'Currently playing', 'Now enjoying the beats of']

queue_words = ['is now logged in the queue', 'has been queued', 'has been added to the queue']

stop_words = ['Player has been stopped', 'Player stopped', 'I am now stopped from playing music', 'I have been stopped by']

colors = [0x1abc9c, 0x11806a, 0x3498db, 0x206694]


@bot.event
async def on_ready():
  print(f'We are now logged in as {bot.user}')
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Music | ;help'))


@bot.command()
async def join(ctx):
    await ctx.message.add_reaction('👍')
    await ctx.author.voice.channel.connect()
    await ctx.send('I have joined the voice channel.')

@join.error
async def join_error(ctx, error):
  await ctx.message.add_reaction('👍')
  if isinstance(error, commands.CommandInvokeError):
    await ctx.send('Please join a voice channel first!')

@bot.command()
async def leave(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    await ctx.message.add_reaction('👍')
    await ctx.voice_client.disconnect()
    await player.stop()
    await ctx.send('I have left the voice channel.')

@leave.error
async def leave_error(ctx, error):
  await ctx.message.add_reaction('👍')
  if isinstance(error, commands.CommandInvokeError):
    await ctx.send("I'm not in a voice channel!")

music = DiscordUtils.Music()

@bot.command()
async def ping(ctx):
  await ctx.send(f'The latency is {round((bot.latency)*1000)}ms.')

@bot.command()
async def play(ctx, *, url):
    player = music.get_player(guild_id=ctx.guild.id)
    await ctx.message.add_reaction('🎧')
    if not player:
        player = music.create_player(ctx, ffmpeg_error_betterfix=True)
    elif not ctx.voice_client.is_playing():
        await player.queue(url, search=True)
        song = await player.play()
        play_embed = discord.Embed(title=f'{random.choice(play_words)} {song.name}', description = f'Requested by {ctx.author.name}', color=random.choice(colors))
        play_embed.add_field(name='Duration', value= f'{round(song.duration)}s', inline=True)
        play_embed.add_field(name='Views', value=song.views, inline=True)
        play_embed.add_field(name='URL', value=f'[Click here]({song.url})', inline=True)
        play_embed.add_field(name='Channel', value= song.channel, inline= True)
        play_embed.add_field(name='Audio Source', value= f"[Click here]({song.source})", inline= True)
        play_embed.add_field(name= 'Looped?', value= song.is_looping, inline= True)
        play_embed.set_thumbnail(url=song.thumbnail)
        await ctx.send(embed = play_embed)
    elif ctx.voice_client.is_playing():
      song = await player.queue(url, search=True)
      play_embed = discord.Embed(title=f'{song.name} {random.choice(queue_words)}', description = f'Requested by {ctx.author.name}', color=random.choice(colors))
      play_embed.add_field(name='Duration', value= f'{round(song.duration)}s', inline=True)
      play_embed.add_field(name='Views', value=song.views, inline=True)
      play_embed.add_field(name='URL', value=f'[Click here]({song.url})', inline=True)
      play_embed.add_field(name='Channel', value= song.channel, inline= True)
      play_embed.add_field(name='Audio Source', value= f"[Click here]({song.source})", inline= True)
      play_embed.add_field(name= 'Looped?', value= song.is_looping, inline= True)
      play_embed.set_thumbnail(url=song.thumbnail)
      await ctx.send(embed = play_embed)

@play.error
async def play_error(ctx, error):
  player = music.get_player(guild_id=ctx.guild.id)
  await ctx.message.add_reaction('🎧')
  if isinstance(error, commands.CommandInvokeError):
      if not player:
        try:
          url = ctx.message.content.split(';play ', 1)[1]
          await ctx.author.voice.channel.connect()
          player2 = music.create_player(ctx, ffmpeg_error_betterfix=True)
          await player2.queue(url, search=True)
          song = await player2.play()
          play_embed = discord.Embed(title=f'{random.choice(play_words)} {song.name}', description = f'Requested by {ctx.author.name}', color=random.choice(colors))
          play_embed.add_field(name='Duration', value= f'{round(song.duration)}s', inline=True)
          play_embed.add_field(name='Views', value=song.views, inline=True)
          play_embed.add_field(name='URL', value=f'[Click here]({song.url})', inline=True)
          play_embed.add_field(name='Channel', value= song.channel, inline= True)
          play_embed.add_field(name='Audio Source', value= f"[Click here]({song.source})", inline= True)
          play_embed.add_field(name= 'Looped?', value= song.is_looping, inline= True)
          play_embed.set_thumbnail(url=song.thumbnail)
          await ctx.send(embed = play_embed)
        except:
          await ctx.send('You are not in a voice channel!')
      if player:
        await ctx.send('The name you have specified is invalid.')
  elif isinstance(error, commands.MissingRequiredArgument):
    await ctx.send('Please specify the song that you want to play.')

extract_lyrics = SongLyrics('AIzaSyCan0eMVlKM2ufB9fzpM8etVUJKh_IYJGg', '47df21fd6a119f6f3')

@bot.command()
async def lyrics(ctx, *, song):
  await ctx.message.add_reaction('🎼')
  data = extract_lyrics.get_lyrics(song)
  lys = data['lyrics']
  lytitle = data['title']
  lyem = discord.Embed(title=lytitle, description=lys, color=random.choice(colors))
  await ctx.send(embed=lyem)

@lyrics.error
async def lyrics_error(ctx, error):
  await ctx.message.add_reaction('🎼')
  player = music.get_player(guild_id=ctx.guild.id)
  if isinstance(error, commands.MissingRequiredArgument):
    if not player:
      await ctx.send('Please specify the song you want lyrics for.')
    else:
      song = player.now_playing()
      data = extract_lyrics.get_lyrics(song.title)
      lys = data['lyrics']
      info = (lys[:2045] + '..') if len(lys) > 2048 else lys
      lytitle = data['title']
      lyem = discord.Embed(title=f'Lyrics for {lytitle}', description=info, color=random.choice(colors))
      await ctx.send(embed=lyem)
  elif isinstance(error, commands.CommandInvokeError):
    await ctx.send('I cannot find lyrics for the song you have specified.')

@bot.command()
async def pause(ctx):
    await ctx.message.add_reaction('⏸')
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.pause()
    await ctx.send(f"{ctx.author.name} has paused {song.name}.")

@pause.error
async def pause_error(ctx, error):
  await ctx.message.add_reaction('⏸')
  if isinstance(error, commands.CommandInvokeError):
    await ctx.send('I am not playing anything!')

@bot.command()
async def resume(ctx):
    await ctx.message.add_reaction('👌') 
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.resume()
    await ctx.send(f"{ctx.author.name} has resumed {song.name}.")

@resume.error
async def resume_error(ctx, error):
  await ctx.message.add_reaction('👌') 
  if isinstance(error, commands.CommandInvokeError):
    await ctx.send("I'm not playing anything!")

@bot.command()
async def clear(ctx):
    await ctx.message.add_reaction('⏹')
    player = music.get_player(guild_id=ctx.guild.id)
    await player.stop()
    await ctx.send('The queue has been cleared.')

@clear.error
async def clear_error(ctx, error):
  await ctx.message.add_reaction('⏹')
  if isinstance(error, commands.CommandInvokeError):
    await ctx.send('Please join a voice channel first!')

@bot.command()
async def loop(ctx):
    await ctx.message.add_reaction('🔁')
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.toggle_song_loop()
    if song.is_looping:
        await ctx.send(f"Now looping {song.name}")
    else:
        await ctx.send(f"{ctx.author.name} has disabled loop for {song.name}.")

@loop.error
async def loop_error(ctx, error):
  await ctx.message.add_reaction('🔁')
  if isinstance(error, commands.CommandInvokeError):
    await ctx.send('I am not playing anything!')

@bot.command()
async def queue(ctx):
    await ctx.message.add_reaction('📃')
    player = music.get_player(guild_id=ctx.guild.id)
    queue_embed = discord.Embed(title = 'Showing the server playlist', description = f'`Requested by {ctx.author.name}`', color=random.choice(colors))
    templist = []
    for song in player.current_queue():
      templist.append(song)
    
    for song in templist:
      queue_embed.add_field(name=f'{templist.index(song)+1}. {song.name}', value=f'{round(song.duration)}s', inline=False)
    
    await ctx.send(embed = queue_embed)

@queue.error
async def queue_error(ctx, error):
  await ctx.message.add_reaction('📃')
  if isinstance(error, commands.CommandInvokeError):
    await ctx.send('I am not playing anything!')

@bot.command()
async def test(ctx):
  player = music.get_player(guild_id=ctx.guild.id)
  await ctx.send(player.queue[1])

@bot.command()
async def np(ctx):
    await ctx.message.add_reaction('🎵')
    player = music.get_player(guild_id=ctx.guild.id)
    song = player.now_playing()
    play_embed = discord.Embed(title=f'{random.choice(play_words)} {song.name}', description = song.description, color=random.choice(colors))
    play_embed.add_field(name='Duration', value= f'{song.duration}s', inline=True)
    play_embed.add_field(name='Views', value=song.views, inline=True)
    play_embed.add_field(name='URL', value=f'[Click here]({song.url})', inline=True)
    play_embed.set_thumbnail(url=song.thumbnail)
    await ctx.send(embed = play_embed)

@np.error
async def np_error(ctx, error):
  await ctx.message.add_reaction('🎵')
  if isinstance(error, commands.CommandInvokeError):
    await ctx.send('I am not playing anything!')

@bot.command()
async def skip(ctx):
    await ctx.message.add_reaction('⏭')
    player = music.get_player(guild_id=ctx.guild.id)
    await player.skip(force=True)
    await asyncio.sleep(1)
    song = player.now_playing()
    await ctx.send(f'Now playing {song.name}')

@skip.error
async def skip_error(ctx, error):
  await ctx.message.add_reaction('⏭')
  if isinstance(error, commands.CommandInvokeError):
    await ctx.send('I am not playing anything!')

@bot.command()
async def volume(ctx, vol):
    await ctx.message.add_reaction('🔊')
    num = float(vol)
    player = music.get_player(guild_id=ctx.guild.id)
    song, volume = await player.change_volume((num/100))
    if num < 200:
      await ctx.send(f"The volume has been changed to {volume*100}%")
    else:
      await ctx.send("The volume has been changed to 200%")

@volume.error
async def volume_error(ctx, error):
  await ctx.message.add_reaction('🔊')
  if isinstance(error, commands.CommandInvokeError):
    await ctx.send('Oops, something went wrong')
  else:
    await ctx.send('Please specify the volume you want after the command.')

@bot.command()
async def remove(ctx, index):
    num = int(index) - 1
    await ctx.message.add_reaction('🗑')
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.remove_from_queue(num)
    await ctx.send(f"{ctx.author.name} has removed {song.name} from the queue.")

@remove.error
async def remove_error(ctx, error):
  await ctx.message.add_reaction('🗑')
  if isinstance(error, commands.CommandInvokeError):
    await ctx.send('The song you are trying to remove is not in the list!')

@bot.command()
async def invite(ctx):
  invite = discord.Embed(title='The invite link for Iridium', description = 'https://discord.com/api/oauth2/authorize?client_id=790517797250662411&permissions=8&scope=bot', color=random.choice(colors))
  invite.add_field(name='Need a utility bot?', value='Add my gf, Iridia via [this link!](https://discord.com/api/oauth2/authorize?client_id=812554180258562079&permissions=8&scope=bot)', inline=False)
  invite.set_thumbnail(url=bot.user.avatar_url)
  await ctx.send(embed=invite)
  
@bot.command()
async def help(ctx):
  helpem=discord.Embed(title='A list of commands for Iridium', description = 'A feature-packed music bot', color=random.choice(colors))
  helpem.set_thumbnail(url=bot.user.avatar_url)
  helpem.add_field(name='play', value='Plays a song or url', inline=False)
  helpem.add_field(name='join', value='Use this command to make the bot join a voice channel', inline=False)
  helpem.add_field(name='leave', value='Use this command to kick the bot out of a voice channel', inline=False)
  helpem.add_field(name='loop', value='Loops the song currently being played', inline=False)
  helpem.add_field(name='pause', value='Pauses the music player', inline=False)
  helpem.add_field(name='np', value='Shows the song currently being played', inline=False)
  helpem.add_field(name='remove', value='Removes a song from the queue', inline=False)
  helpem.add_field(name='lyrics', value='Gets the lyrics of a specified song. If no song is provided, it will give the lyris of the current song being played.', inline=False)
  helpem.add_field(name='clear', value='Clears the queue', inline=False)
  helpem.add_field(name='resume', value='Resumes a paused music track', inline=False)
  helpem.add_field(name='skip', value='Skips to the next song in the queue', inline=False)
  helpem.add_field(name='volume', value='Changes the volume', inline=False)
  helpem.add_field(name='invite', value='Get the invite link', inline=False)
  await ctx.send(embed=helpem)

bot.run('NzkwNTE3Nzk3MjUwNjYyNDEx.X-BxEQ.ZfMyhJ7NrAo9iJi5M52LARiivOw')
