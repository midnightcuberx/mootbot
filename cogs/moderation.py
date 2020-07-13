import discord, pymongo, dns, asyncio, os
from discord.ext import commands
from discord import NotFound
from datetime import datetime

mongosecret = os.environ.get("mongosecret")
client = pymongo.MongoClient(mongosecret)
db = client["bot"]


def get_emoji(string: discord.Emoji):
  extra,extra1,extra2=string


def get_role(role):
  extra, role = role.split("@")
  role, extra = role.split(">")
  extra, role_id = role.split("&")
  return int(role_id)


class Mod(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  @commands.has_permissions(manage_roles=True)
  @commands.bot_has_permissions(manage_roles=True)
  async def rr(self, ctx, channel: discord.TextChannel = None):
    roles=[]
    reactions=[]
    channel = channel if channel else ctx.channel
    await ctx.send("Ok, now what would you like your title to be?")
    title = await self.bot.wait_for('message',check=lambda message: message.author.id == ctx.author.id)
    await ctx.send(f"Ok, your title will be {title.content}")
    await ctx.send("Ok, now what would you like your message to be?")
    msg = await self.bot.wait_for('message',check=lambda message: message.author.id == ctx.author.id)
    await ctx.send(f"Ok, your message will be {msg.content}")
    await ctx.send("Feel free to send cancel and stop this process anytime...\nNow how many reaction roles would you like to add to this message?")
    message = await self.bot.wait_for('message',check=lambda message: message.author.id == ctx.author.id)
    if message.content.lower() == "cancel":
      await ctx.send("Process cancelled")
      return
    loop=True
    while loop is True:
      try:
        times=int(message.content)
        loop=False
      except ValueError:
        if message.content.lower() == "cancel":
          await ctx.send("Process cancelled")
          return
        await ctx.send("That is not a valid integer")
        message = await self.bot.wait_for('message',check=lambda message: message.author.id == ctx.author.id)
        
    for i in range(times):
      await ctx.send("Please enter an emoji")
      message = await self.bot.wait_for('message',check=lambda message: message.author.id == ctx.author.id)
      loop = True
      while loop is True:
        try:
          emoji = message.content
          await message.add_reaction(emoji)
          reactions.append(emoji)
          #reaction = [r.emoji for r in message.reactions]
          #reaction = self.bot.get_emoji(reaction[0])
          #await ctx.send(reaction.id)
          loop = False
        except discord.errors.HTTPException:
          if message.content.lower() == "cancel":
            await ctx.send("Process cancelled")
            return
          await ctx.send("That is not a valid emoji, please try again")
          message = await self.bot.wait_for('message',check=lambda message: message.author.id == ctx.author.id)
      await ctx.send("Now, please mention the role you would like to allocate that reaction to")
      message = await self.bot.wait_for('message',check=lambda message: message.author.id == ctx.author.id)
      if message.content.lower() == "cancel":
        await ctx.send("Process cancelled")
        return
      loop = True
      while loop is True:
        try:
          role = get_role(message.content)
          roles.append(role)
          loop = False
        except Exception as e:
          if message.content.lower() == "cancel":
            await ctx.send("Process cancelled")
            return
          await ctx.send("That is not a valid role, please try again")
          await ctx.send(e)
          message = await self.bot.wait_for('message',check=lambda message: message.author.id == ctx.author.id)
          if message.content.lower() == "cancel":
            await ctx.send("Process cancelled")
            return
    embed=discord.Embed(title=title.content,description=msg.content,color=0xffff00,timestamp=datetime.utcnow())
    msg=await channel.send(embed=embed)
    collection=db["rr"]
    dict1={}
    for i in range(times):
      await msg.add_reaction(reactions[i])
      dict1[reactions[i]]=roles[i]
    collection.update_one({"_id":ctx.guild.id},{"$set":{str(msg.id):dict1}})
    await ctx.send("Please make sure that mootbot's role is above the roles you want to give, otherwise the reaction roles will not work!")

  @rr.error
  async def rr_error(self,ctx,error):
    if isinstance(error,commands.BadArgument):
      await ctx.send("That is not a valid channel!")
    
    elif isinstance(error,commands.MissingRequiredArgument):
      await ctx.send("Please enter the channel you would like to do reaction roles in")
    
    elif isinstance(error,commands.MissingPermissions):
      await ctx.send("You cannot use this command because you do not have the manage roles permission")
    
    elif isinstance(error,commands.BotMissingPermissions):
      await ctx.send("I cannot do this because I do not have manage roles permissions or the roles you want me to allocate is above my role")
    else:
      raise error
    #async def rr(self,ctx,messageid:int):
    '''
    try:
      msg = await ctx.guild.get_message(id=messageid)
    except NotFound:
      await ctx.send("That is not a valid message id!")
      return

    await msg.add_reaction'''

  @commands.command(aliases=["ui"])
  async def userinfo(self, ctx, user: discord.Member = None):
    if not user:
      user = ctx.message.author
    userroles = ", ".join([r.mention for r in user.roles])
    embed = discord.Embed(
        title=f"User info for {user}", description="", color=0xeee657)
    embed.add_field(name='User ID', value=user.id, inline=False)
    embed.add_field(name='Nick', value=user.nick, inline=False)
    embed.add_field(name='Status', value=user.status, inline=False)
    embed.add_field(name='Game', value=user.activity, inline=False)
    embed.add_field(name='Roles', value=userroles, inline=False)
    embed.add_field(
        name='Account Created', value=user.created_at, inline=False)
    embed.add_field(name='Join Date', value=user.joined_at, inline=False)
    embed.set_thumbnail(url=user.avatar_url)
    await ctx.send(embed=embed)

  @userinfo.error
  async def userinfo_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.send("You did not specify a valid member!")

  @commands.command()
  async def avatar(self, ctx, member: discord.Member = None):
    if not member:
      member = ctx.message.author
    embed = discord.Embed(title=f"{member}'s avatar", description="", color=0xeee657)
    embed.set_image(url=member.avatar_url)
    await ctx.send(embed=embed)

  @commands.command(aliases=["raidsetup", "protectionsetup"])
  @commands.has_permissions(manage_guild=True)
  async def setup(self, ctx, onoff="on"):
    onoff = onoff.lower()
    if onoff == "off":
      await ctx.send("Successfully switched raid protection off")
      time = 0
      dorw = "d"
    if onoff != "off" and onoff != "on":
      await ctx.send("That is not a valid option! You can only switch raid protection on and off!")
      return
    elif onoff == "on":
      await ctx.send("Succefully switched raid protection on")
      await ctx.send("What is the minimum age an account needs to be to pass the raid protection procedure? Answer with a whole number of days or weeks in this format: `<number> <d/w>`")
      intdays = False
      corform = False
      while intdays is False or corform is False:
        message = await self.bot.wait_for('message',check=lambda message: message.author.id == ctx.author.id)
        try:
          time, dorw = message.content.lower().split(" ")
          corform = True
        except ValueError:
          pass
          #await ctx.send("Please enter the amount of days/weeks in a valid format!")
        try:
          time = int(time)
          if time < 1:
            await ctx.send("Please try again, that is an invalid number of days/weeks")
          else:
            intdays = True
          if dorw != "d" and dorw != "w" and time >= 1:
            await ctx.send("Please enter in the format of <number> <d/w>!")
            intdays = False
        except (ValueError, UnboundLocalError):
          await ctx.send("That is not a valid number of days/weeks! Please enter again!")

      await ctx.send("Finally, what is the message you would like to send to a new member if their account is new?")
      message = await self.bot.wait_for('message',check=lambda message: message.author.id == ctx.author.id)

    time = time * 86400
    if dorw == "w":
      time = time * 7

    collection = db["raidprotection"]
    collection.update_one({"_id": ctx.guild.id}, {"$set": {"seconds": time}})
    collection.update_one({"_id": ctx.guild.id}, {"$set": {"message": message.content}})
    await ctx.send(f"Ok done! Your message to them will be {message.content}")

  @setup.error
  async def setup_error(self, ctx, error):
    if isinstance(error, commands.MissingPermissions):
      await ctx.send("You need manage server permissions to run this command!")
    else:
      raise error

  @commands.command(aliases=["logs", "log"])
  @commands.has_permissions(manage_guild=True)
  async def logsetup(self, ctx, channel: discord.TextChannel = None):
    if not channel:
      await ctx.send("You must enter a channel!")
      return
    collection = db["logs"]
    collection.update_one({"_id": ctx.guild.id}, {"$set": {"channel": channel.id}})
    await ctx.send(f"You have set your logging channel to {channel}")

  @commands.command()
  @commands.has_permissions(manage_guild=True)
  async def logtoggle(self, ctx, onoff="on"):
    onoff = onoff.lower()
    if onoff != "on" and onoff != "off":
      await ctx.send("Please enter on or off!")
      return
    collection = db["logs"]
    collection.update_one({"_id": ctx.guild.id}, {"$set": {"mode": onoff}})
    await ctx.send("You have toggled logs to " + onoff)

  @commands.command()
  @commands.has_permissions(manage_roles=True)
  async def warn(self,ctx,member:discord.Member = None,*,reason="no reason"):
    if not member:
      await ctx.send("You need to enter a member to warn!")
      return
    collection = db["warns"]
    serverwarns = collection.find_one({"_id": ctx.guild.id})

    list1 = []
    try:
      a = serverwarns[str(member.id)]
      memberwarns = serverwarns[str(member.id)]
      for key, value in sorted(
          memberwarns.items(), reverse=False, key=lambda item: item[0]):
        list1.append(key)
      numofwarns = int(list1[-1])
    except (KeyError, TypeError):
      serverwarns[str(member.id)] = {}
      numofwarns = 0

    numofwarns += 1
    serverwarns[str(member.id)][str(numofwarns)] = reason
    userwarns = serverwarns[str(member.id)]
    collection.update_one({"_id": ctx.guild.id}, {"$set": {str(member.id): userwarns}})
    await ctx.send(f"{member} has been warned for {reason}")

  @warn.error
  async def warn_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.send("You need to enter a valid member!")
    elif isinstance(error, commands.MissingPermissions):
      await ctx.send("You need manage roles permissions to run this command!")
    else:
      raise error

  @commands.command()
  async def warns(self, ctx, member: discord.Member = None):
    if not member:
      member = ctx.author
    collection = db["warns"]
    serverwarns = collection.find_one({"_id": ctx.guild.id})
    try:
      a = serverwarns[str(member.id)]
    except KeyError:
      await ctx.send("This user has no warnings in this server")
      return
    userwarns = serverwarns[str(member.id)]
    embed = discord.Embed(title=f"Warns for {member} in {ctx.guild}")
    for key, value1 in sorted(
        userwarns.items(), reverse=False, key=lambda item: item[0]):
      embed.add_field(name=f"#{key}", value=f"{value1}")
    await ctx.send(embed=embed)

  @commands.command()
  @commands.is_owner()
  async def warnsetup(self, ctx):
    collection = db["warns"]
    for guild in self.bot.guilds:
      collection.insert_one({"_id": guild.id})
    await ctx.send("done")

  @commands.command()
  @commands.has_permissions(ban_members=True)
  async def softban(self,ctx,member: discord.Member = None,*,reason="no reason"):
    if not member:
      await ctx.send("You need to enter a member to doftban!")
      return
    mrole = member.top_role
    arole = ctx.author.top_role
    if mrole >= arole:
      await ctx.send("I cannot softban that person due to role hierachy")
      return
    await member.ban(reason=reason)
    await member.unban(reason=reason)
    await ctx.send(f'Softbanned {member.mention} for {reason}')

  @softban.error
  async def softban_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.send("I could not recognise that user")
    elif isinstance(error, commands.MissingPermissions):
      await ctx.send("You do not have necessary permissions to do so!")
    elif isinstance(error, commands.BotMissingPermissions):
      await ctx.send("I do not have permission to ban that user!")

  '''    
  @commands.command()
  @commands.has_permissions(manage_messages=True)
  async def invitetoggle(self,ctx,onoff=None):
    collection=db["invites"]

    invite=collection.find_one({"_id":ctx.guild.id})
    invites=invite["mode"]
    if not onoff:
      if invites=="on":
        invites="off"
      else:
        invites="on"
      await ctx.send(f"Successfully toggled invite police to {invites}")
      invite[str(ctx.guild.id)]=invites
      with open('invitetoggle.json','w') as a:
        json.dump(invite,a,indent=4)
      return
    elif onoff.lower() != "on" and onoff.lower() != "off":
      await ctx.send("You must tell me to toggle it on or off!")
      return
    onoff=onoff.lower()
    invites=onoff
    await ctx.send(f"Successfully toggled invite police to {invites}")
    collection.update_one({"_id":ctx.guild.id},{"$set":{"mode":invites}})
  @invitetoggle.error
  async def invitetoggle_error(self,ctx,error):
    if isinstance(error,commands.MissingPermissions):
      await ctx.send("You can only use this command if you have the manage messages permission!")
  '''

  @commands.command()
  @commands.has_permissions(kick_members=True)
  async def kick(self,ctx,member: discord.Member = None,*,reason="no reason"):
    if not member:
      await ctx.send("You need to enter a member to kick!")
      return
    mrole = member.top_role
    arole = ctx.author.top_role
    if mrole >= arole:
      await ctx.send("I cannot mute that person due to role hierachy")
      return
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention} successfully! for {reason}')

  @kick.error
  async def kick_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.send("I could not recognise that user")
    elif isinstance(error, commands.MissingPermissions):
      await ctx.send("You do not have necessary permissions to do so!")
    elif isinstance(error, commands.BotMissingPermissions):
      await ctx.send("I do not have permission to kick that user!")

  @commands.command()
  @commands.has_permissions(ban_members=True)
  #@commands.is_owner()
  async def ban(self,ctx,member: discord.Member = None,*,reason="no reason"):
    if not member:
      await ctx.send("You need to enter a member to ban!")
      return
    mrole = member.top_role
    arole = ctx.author.top_role
    if mrole >= arole:
      await ctx.send("I cannot ban that person due to role hierachy")
      return
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention} for {reason}')

  @ban.error
  async def ban_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.send("I could not recognise that user")
    elif isinstance(error, commands.MissingPermissions):
      await ctx.send("You do not have necessary permissions to do so!")
    elif isinstance(error, commands.BotMissingPermissions):
      await ctx.send("I do not have permission to ban that user!")
    else:
      raise error

  @commands.command()
  @commands.has_permissions(manage_messages=True)
  async def purge(self, ctx, limit: int = 1):
    if not limit:
      await ctx.send("Ree! you must enter the amount of messages to purge")

    elif limit > 20:
      await ctx.send("I can only purge max 20 messages at once you nonce. But since Im feeling nice, I'll purge 20 messagss for you")
      limit = 20
      await asyncio.sleep(2)
    await ctx.message.delete()
    await ctx.channel.purge(limit=limit)
    await ctx.send('{} has successfully purged {} messages'.format(ctx.author.mention, limit),delete_after=1.0)

  @purge.error
  async def purge_error(self, ctx, error):
    if isinstance(error, commands.MissingPermissions):
      await ctx.send("You do not have necessary permissions to do so!")
    elif isinstance(error, commands.BotMissingPermissions):
      await ctx.send("I do not have permission to delete messages!")

  @commands.command(aliases=["shut"])
  @commands.has_permissions(kick_members=True)
  async def mute(self,ctx,member: discord.Member = None,*,reason="no reason"):
    guild = ctx.guild
    if not member:
      await ctx.send("You need to enter a member to mute!")
      return
    mrole = member.top_role
    arole = ctx.author.top_role
    if mrole >= arole:
      await ctx.send("I cannot mute that person due to role hierachy")
      return

    role = discord.utils.get(ctx.guild.roles, name='mootmoot')
    if role != None:
      await member.add_roles(role)
      await ctx.send(
          f"{member.mention} has successfully been muted for {reason}")
    elif not role:
      venimute = await guild.create_role(name="mootmoot")
      for channel in ctx.guild.text_channels:
        await channel.set_permissions(venimute, send_messages=False)
      await member.add_roles(venimute)
      await ctx.send(
          f"{member.mention} has successfully been muted for {reason}")

  @mute.error
  async def mute_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.send("Please enter a valid user to mute!")
    elif isinstance(error, commands.MissingPermissions):
      await ctx.send("You do not have permissions to mute people!")
    elif isinstance(error, commands.BotMissingPermissions):
      await ctx.send("I do not have permission to mute people!")
    else:
      raise error

  @commands.command()
  @commands.has_permissions(kick_members=True)
  async def unmute(self, ctx, member: discord.Member = None):
    if not member:
      await ctx.send("You need to enter a member to unmute!")
      return
    guild = ctx.guild
    for role in guild.roles:
      if role.name == "mootmoot":
        await member.remove_roles(role)
        await ctx.send(f"{member.mention} has been unmuted")

  @unmute.error
  async def unmute_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.send("Please enter a valid user to unmute!")
    elif isinstance(error, commands.MissingPermissions):
      await ctx.send("You do not have permissions to unmute people!")
    elif isinstance(error, commands.BotMissingPermissions):
      await ctx.send("I do not have permission to unmute people!")
    else:
      await ctx.send("You need to have a mootmoot role in order to unmute someone")


def setup(bot):
  bot.add_cog(Mod(bot))
