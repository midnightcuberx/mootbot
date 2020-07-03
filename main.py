import discord,datetime,time,os,pymongo,dns
from discord.ext import commands, tasks
from itertools import cycle

mongosecret=os.environ.get("mongosecret")
client = pymongo.MongoClient(mongosecret)
db=client["bot"]

start_time=time.time()

def get_prefix(bot,message):
  mongosecret=os.environ.get("mongosecret")
  client = pymongo.MongoClient(mongosecret)
  db = client["bot"]
  collection=db["prefix"]
  try:
    collection.insert_one({"_id":message.guild.id,"prefix":";"})
    return ";"
  except pymongo.errors.DuplicateKeyError:
    collection=db["prefix"]
    results=collection.find({"_id":message.guild.id})
    for result in results:
      prefix=result
    return prefix["prefix"]
  except AttributeError:
    return ";"

bot = commands.Bot(command_prefix= get_prefix)

status=cycle(["with Rubiks cubes",";help","ping me for help","with raiders","with corona","with myself","with my gf","with your mum"])

@tasks.loop(seconds=10)
async def change_status():
  await bot.change_presence(activity=discord.Game(next(status)))

@bot.event
async def on_ready():
    change_status.start()
    #activity = discord.Game(name="with Rubiks cubes | +help", type=3)
    await bot.change_presence(status=discord.Status.idle)
    print('Bot is ready')
    print('------')
  
@bot.event
async def on_guild_join(guild):
  collection=db["prefix"]
  collection.insert_one({"_id":guild.id,"prefix":";"})
  collection=db["invites"]
  collection.insert_one({"_id":guild.id,"mode":"off"})

@bot.event
async def on_guild_remove(guild):
  collection=db["prefix"]
  collection.delete_one({"_id":guild.id})
  collection=db["invites"]
  collection.delete_one({"_id":guild.id})

@bot.event
async def on_member_join(member):
  if member.guild.id!=431906396032991232:
    return
  current_time=time.time()
  member_created=member.created_at.timestamp()
  if current_time - member_created < 604800:
    role = discord.utils.get(member.guild.roles, name='mootmoot')
    if not role:
      role = await member.guild.create_role(name="mootmoot")
      for channel in member.guild.text_channels:
        await channel.set_permissions(role,send_messages=False)
    await member.add_roles(role)
    channel=discord.utils.get(member.guild.channels,id=696457320208662670)
    await channel.send("@everyone a new account has joined")
    await member.send("We have noticed you are a new account. Please contact an admin if you intend to part of our server.")

@bot.event
async def on_message(message):
  if message.author.bot:
    return
  '''
  if message.content.lower().startswith("discord.gg") or message.content.lower().startswith("https://discord.gg"):
    collection=db["invites"]
    invite=collection.find_one()
    invites=invite[str(message.guild.id)]
    if invites=="on":
      return
    await message.delete()
    await message.channel.send(f"{message.author.mention}, Invites are not permitted in this server sorry")'''
  await bot.process_commands(message)

bot.remove_command('help')
for filename in os.listdir('./cogs'):
  if filename.endswith(".py"):
    bot.load_extension(f"cogs.{filename[:-3]}")

@bot.command()
@commands.is_owner()
async def load(ctx,extension):
  bot.load_extension(f"cogs.{extension}")

@bot.command()
@commands.is_owner()
async def unload(ctx,extension):
  bot.unload_extension(f"cogs.{extension}")

@bot.command()
async def invite(ctx):
  await ctx.send("https://discord.com/api/oauth2/authorize?client_id=679522730000777289&permissions=8&scope=bot")

@bot.command()
async def uptime(ctx):
    current_time = time.time()
    difference = int(round(current_time - start_time))
    text = str(datetime.timedelta(seconds=difference))
    await ctx.send(f"The bot has been up for {text}")

@bot.command()
@commands.is_owner()
async def reload(ctx,*,file=None):
  if not file:
    for filename in os.listdir('./cogs'):
      if filename.endswith(".py"):
        bot.unload_extension(f"cogs.{filename[:-3]}")
        bot.load_extension(f"cogs.{filename[:-3]}")
        await ctx.send(f"Successfully reloaded {filename}!")
    return

  bot.unload_extension(f"cogs.{file[:-3]}")
  bot.load_extension(f"cogs.{file[:-3]}")
  await ctx.send(f"Successfully reloaded {file}!")




@bot.command(aliases=["prefix","newprefix"])
@commands.has_permissions(administrator=True)
async def setprefix(ctx,newprefix):
  collection=db["prefix"]
  try:
    collection.insert_one({"_id":ctx.guild.id,"prefix":newprefix})
  except pymongo.errors.DuplicateKeyError:
    collection.update_one({"_id":ctx.guild.id},{"$set":{"prefix":newprefix}})
  await ctx.send(f'prefix is changed to {newprefix}')
@setprefix.error
async def setprefix_error(ctx,error):
  if isinstance(error,commands.MissingPermissions):
    await ctx.send("You do not have permission to change my prefix! You need admin to do so.")
  elif isinstance(error,commands.MissingRequiredArgument):
    await ctx.send("You did not specify what to change the prefix to!")

  
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Shutting down")
    await ctx.bot.logout()

@shutdown.error
async def shutdown_error(ctx,error):
  if isinstance(error,commands.MissingPermissions):
    await ctx.send("Sorry, Only my owner, Venimental#1289 can use this command")
  

token=os.environ.get("botsecret")
bot.run(token, reconnect=True)
