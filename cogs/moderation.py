import discord,pymongo,dns,asyncio,os
from discord.ext import commands

mongosecret=os.environ.get("mongosecret")
client = pymongo.MongoClient(mongosecret)
db=client["bot"]

class Mod(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  @commands.command()
  async def test(self,ctx,channel:discord.TextChannel):
    await ctx.send(channel.id)
  @commands.command()
  @commands.has_permissions(manage_guild=True)
  async def setup(self,ctx,onoff="on"):
    onoff=onoff.lower()
    if onoff=="off":
      await ctx.send("Successfully switched raid protection off")
      time=0
      dorw="d"
    if onoff !="off" and onoff !="on":
      await ctx.send("That is not a valid option! You can only switch raid protection on and off!")
      return
    elif onoff=="on":
      await ctx.send("Succefully switched raid protection on")
      await ctx.send("What is the minimum age an account needs to be to pass the raid protection procedure? Answer with a whole number of days or weeks in this format: `<number> <d/w>`")
      intdays=False
      corform=False
      while intdays is False or corform is False:
        message = await self.bot.wait_for('message', check=lambda message: message.author.id == ctx.author.id)
        try:
          time,dorw=message.content.lower().split(" ")
          corform=True
        except ValueError:
          print("Please enter the amount of days/weeks in a valid format!")
        try:
          time=int(time)
          if dorw!= "d" and dorw!="w":
            await ctx.send("Please enter in the format of <number> <d/w>!")
            intdays=False
          if time<1:
            await ctx.send("Please try again, that is an invalid number of days/weeks")
          elif time>=1 and intdays is True:
            intdays=True
        except (ValueError,UnboundLocalError):
          await ctx.send("That is not a valid number of days/weeks! Please enter again!")
        
      await ctx.send("Finally, what is the message you would like to send to a new member if their account is new?")
      message = await self.bot.wait_for('message', check=lambda message: message.author.id == ctx.author.id)
      await ctx.send(f"Ok done! Your message to them will be {message.content}")


    
    time=time*86400
    if dorw=="w":
      time=time*7

    collection=db["raidprotection"]
    collection.update_one({"_id":ctx.guild.id},{"$set":{"seconds":time}})
    collection.update_one({"_id":ctx.guild.id},{"$set":{"message":message.content}})

  @setup.error
  async def setup_error(self,ctx,error):
    if isinstance(error,commands.MissingPermissions):
      await ctx.send("You need manage server permissions to run this command!")
    else:
      raise error

  @commands.command()
  @commands.is_owner()
  async def raidsetup(self,ctx):
    collection=db["raidprotection"]
    for guild in self.bot.guilds:
      collection.insert_one({"_id":guild.id,"seconds":0,"message":"None"})

  @commands.command(aliases=["logs","log"])
  @commands.has_permissions(manage_guild=True)
  async def logsetup(self,ctx,channel:discord.TextChannel=None):
    if not channel:
      await ctx.send("You must enter a channel!")
      return
    collection=db["logs"]
    collection.update_one({"_id":ctx.guild.id},{"$set":{"channel":channel.id}})
    await ctx.send(f"You have set your logging channel to {channel}")

  @commands.command()
  @commands.has_permissions(manage_guild=True)
  async def logtoggle(self,ctx,onoff="on"):
    onoff=onoff.lower()
    if onoff!="on" and onoff !="off":
      await ctx.send("Please enter on or off!")
      return
    collection=db["logs"]
    collection.update_one({"_id":ctx.guild.id},{"$set":{"mode":onoff}})
    await ctx.send("You have toggled logs to" + onoff)



  @commands.command()
  @commands.has_permissions(manage_roles=True)
  async def warn(self,ctx,member:discord.Member=None,*,reason="no reason"):
    if not member:
      await ctx.send("You need to enter a member to warn!")
      return
    collection=db["warns"]
    serverwarns=collection.find_one({"_id":ctx.guild.id})

    list1=[]
    try:
      a=serverwarns[str(member.id)]
      memberwarns=serverwarns[str(member.id)]
      for key,value in sorted(memberwarns.items(),reverse=False, key=lambda item:item[0]):
        list1.append(key)
      numofwarns=int(list1[-1])
    except (KeyError,TypeError):
      serverwarns[str(member.id)]={}
      numofwarns=0

    numofwarns+=1
    serverwarns[str(member.id)][str(numofwarns)]=reason
    userwarns=serverwarns[str(member.id)]
    collection.update_one({"_id":ctx.guild.id},{"$set":{str(member.id):userwarns}})
    await ctx.send(f"{member} has been warned for {reason}")
  
  @warn.error
  async def warn_error(self,ctx,error):
    if isinstance(error,commands.BadArgument):
      await ctx.send("You need to enter a valid member!")
    elif isinstance(error,commands.MissingPermissions):
      await ctx.send("You need manage roles permissions to run this command!")

  @commands.command()
  async def warns(self,ctx,member:discord.Member=None):
    if not member:
      member=ctx.author
    collection=db["warns"]
    serverwarns=collection.find_one({"_id":ctx.guild.id})
    try:
      a=serverwarns[str(member.id)]
    except KeyError:
      await ctx.send("This user has no warnings in this server")
      return
    userwarns=serverwarns[str(member.id)]
    embed=discord.Embed(title=f"Warns for {member} in {ctx.guild}")
    for key,value1 in sorted(userwarns.items(),reverse=False, key=lambda item:item[0]):
      embed.add_field(name=f"#{key}",value=f"{value1}")
    await ctx.send(embed=embed)
  
  @commands.command()
  @commands.is_owner()
  async def warnsetup(self,ctx):
    collection=db["warns"]
    for guild in self.bot.guilds:
      collection.insert_one({"_id":guild.id})
    await ctx.send("done")

    

  @commands.command()
  @commands.has_permissions(ban_members=True)
  async def softban(self,ctx, member : discord.Member=None, *, reason=None):
    if not member:
      await ctx.send("You need to enter a member to ban!")
      return
    await member.ban(reason=reason)
    await member.unban(reason=reason)
    await ctx.send(f'Softbanned {member.mention}')
  @softban.error
  async def softban_error(self,ctx,error):
    if isinstance(error, commands.BadArgument):
      await ctx.send("I could not recognise that user")
    elif isinstance(error,commands.MissingPermissions):
      await ctx.send("You do not have necessary permissions to do so!")
    elif isinstance(error,commands.BotMissingPermissions):
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
  async def kick(self,ctx, member : discord.Member=None, *, reason=None):
    if not member:
      await ctx.send("You need to enter a member to kick!")
      return
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention} successfully! for {reason}')
  @kick.error
  async def kick_error(self,ctx,error):
    if isinstance(error, commands.BadArgument):
      await ctx.send("I could not recognise that user")
    elif isinstance(error,commands.MissingPermissions):
      await ctx.send("You do not have necessary permissions to do so!")
    elif isinstance(error,commands.BotMissingPermissions):
      await ctx.send("I do not have permission to kick that user!")

  @commands.command()
  @commands.has_permissions(ban_members=True)
  #@commands.is_owner()
  async def ban(self,ctx, member : discord.Member=None, *, reason=None):
    if not member:
      await ctx.send("You need to enter a member to ban!")
      return
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')
  @ban.error
  async def ban_error(self,ctx,error):
    if isinstance(error, commands.BadArgument):
      await ctx.send("I could not recognise that user")
    elif isinstance(error,commands.MissingPermissions):
      await ctx.send("You do not have necessary permissions to do so!")
    elif isinstance(error,commands.BotMissingPermissions):
      await ctx.send("I do not have permission to ban that user!")
    else:
      raise error

  @commands.command()
  @commands.has_permissions(manage_messages=True)
  async def purge(self,ctx, limit: int=1):
    if not limit:
        await ctx.send("Ree! you must enter the amount of messages to purge")
        
    elif limit>20:
        await ctx.send("I can only purge max 20 messages at once you nonce. But since Im feeling nice, I'll purge 20 messagss for you")
        limit=20
        await asyncio.sleep(2)
    await ctx.message.delete()
    await ctx.channel.purge(limit=limit)
    await ctx.send('{} has successfully purged {} messages'.format(ctx.author.mention,limit),delete_after=1.0)

  @purge.error
  async def purge_error(self,ctx,error):
    if isinstance(error,commands.MissingPermissions):
      await ctx.send("You do not have necessary permissions to do so!")
    elif isinstance(error,commands.BotMissingPermissions):
      await ctx.send("I do not have permission to delete messages!")

  @commands.command()
  @commands.has_permissions(kick_members=True)
  async def mute(self,ctx, member: discord.Member=None,*,reason="no reason"):
    guild=ctx.guild
    if not member:
      await ctx.send("You need to enter a member to mute!")
      return
    role = discord.utils.get(ctx.guild.roles, name='mootmoot')
    if role !=None:
      await member.add_roles(role)
      await ctx.send(f"{member.mention} has successfully been muted for {reason}")
    elif not role:
      venimute = await guild.create_role(name="mootmoot")
      for channel in ctx.guild.text_channels:
        await channel.set_permissions(venimute,send_messages=False)
      await member.add_roles(venimute)
      await ctx.send(f"{member.mention} has successfully been muted for {reason}")
  @mute.error
  async def mute_error(self,ctx,error):
    if isinstance(error,commands.BadArgument):
      await ctx.send("Please enter a valid user to mute!")
    elif isinstance(error,commands.MissingPermissions):
      await ctx.send("You do not have permissions to mute people!")
    elif isinstance(error,commands.BotMissingPermissions):
      await ctx.send("I do not have permission to mute people!")


  @commands.command()
  @commands.has_permissions(kick_members=True)
  async def unmute(self,ctx, member : discord.Member=None):
    if not member:
      await ctx.send("You need to enter a member to unmute!")
      return
    guild = ctx.guild
    for role in guild.roles:
      if role.name == "mootmoot":
        await member.remove_roles(role)
        await ctx.send(f"{member.mention} has been unmuted")
  @unmute.error
  async def unmute_error(self,ctx,error):
    if isinstance(error,commands.BadArgument):
      await ctx.send("Please enter a valid user to unmute!")
    elif isinstance(error,commands.MissingPermissions):
      await ctx.send("You do not have permissions to unmute people!")
    elif isinstance(error,commands.BotMissingPermissions):
      await ctx.send("I do not have permission to unmute people!")
    else:
      await ctx.send("You need to have a mootmoot role in order to unmute someone")

def setup(bot):
  bot.add_cog(Mod(bot))
