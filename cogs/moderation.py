import discord,pymongo,dns,asyncio,os
from discord.ext import commands

mongosecret=os.environ.get("mongosecret")
client = pymongo.MongoClient(mongosecret)
db=client["bot"]

class Mod(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  @commands.has_permissions(manage_roles=True)
  async def warn(self,ctx,member:discord.Member,*,reason):
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
    await ctx.send(f"{member} has been wanred for {reason}")

  @commands.command()
  async def warns(self,ctx,member:discord.Member):
    collection=db["warns"]
    serverwarns=collection.find_one({"_id":ctx.guild.id})
    if not serverwarns[str(member.id)]:
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
