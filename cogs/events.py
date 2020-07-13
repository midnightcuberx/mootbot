import discord,dns,pymongo,os,random,time,asyncio
import datetime as date
from discord.ext import commands
from datetime import datetime

mongosecret=os.environ.get("mongosecret")
client = pymongo.MongoClient(mongosecret)
db=client["bot"]

class Events(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.Cog.listener()
  async def on_raw_reaction_add(self,payload):
    print(payload.emoji)
    guildid=payload.guild_id
    collection=db["rr"]
    rr=collection.find_one({"_id":guildid})
    try:
      a=rr[str(payload.message_id)]
    except KeyError:
      return
    if len(a)<=0:
      return
    try:
      a=rr[str(payload.message_id)][str(payload.emoji)]
    except KeyError:
      return
    guild=discord.utils.get(self.bot.guilds,id=guildid)
    role=discord.utils.get(guild.roles,id=a)
    member=discord.utils.get(guild.members,id=payload.user_id)
    await member.add_roles(role)

  @commands.Cog.listener()
  async def on_raw_reaction_remove(self,payload):
    print(payload.emoji)
    guildid=payload.guild_id
    collection=db["rr"]
    rr=collection.find_one({"_id":guildid})
    try:
      a=rr[str(payload.message_id)]
    except KeyError:
      return
    if len(a)<=0:
      return
    try:
      a=rr[str(payload.message_id)][str(payload.emoji)]
    except KeyError:
      return
    guild=discord.utils.get(self.bot.guilds,id=guildid)
    role=discord.utils.get(guild.roles,id=a)
    member=discord.utils.get(guild.members,id=payload.user_id)
    await member.remove_roles(role)
    
  @commands.Cog.listener()
  async def on_member_join(self,member):
    current_time=time.time()
    member_created=member.created_at.timestamp()
    if member.guild.id==431906396032991232:
      if current_time - member_created < 1814400:
        role = discord.utils.get(member.guild.roles, id=587216429233733632)
        await asyncio.sleep(1.5)
        await member.add_roles(role)
        channel=discord.utils.get(member.guild.channels,id=552609849939329027)
        await channel.send(f"Account {member.name} was created less than 3 weeks ago and was muted successfully")
        await member.send("Due to your account being created recently, you have been automuted. \
                    \n To gain access to the server, DM <@575252669443211264> for access and the staff team will respond as soon as possible. ")
    else:
      collection=db["raidprotection"]
      guildsettings=collection.find_one({"_id":member.guild.id})
      seconds=guildsettings["seconds"]
      if current_time - member_created < seconds:
        role = discord.utils.get(member.guild.roles, name="mootmoot")
        await member.add_roles(role)
        message=guildsettings["message"]
        await member.send(message)
    collection=db["logs"]
    a=collection.find_one({"_id":member.guild.id})
    if a["mode"]=="on":
      channel=a["channel"]
      if channel!=0:
        channel=discord.utils.get(member.guild.channels,id=channel)
        timenow=datetime.utcnow()
        embed=discord.Embed(title=f"{member} has joined the server",description=f"{member} has joined the server",color=0xffff00,timestamp=timenow)
        embed.set_thumbnail(url=member.avatar_url)
        difference=current_time-member_created
        collection=db["raidprotection"]
        guildsettings=collection.find_one({"_id":member.guild.id})
        seconds=guildsettings["seconds"]
        if member.guild.id==431906396032991232:
          seconds=1814400
        if difference<seconds:
          days=round(difference/86400)
          embed.add_field(name="⚠️ Warning! ⚠️",value=f"This account was created {days} days ago")
        await channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_member_remove(self,member):
    collection=db["logs"]
    a=collection.find_one({"_id":member.guild.id})
    if a["mode"]=="on":
      channel=a["channel"]
      if channel!=0:
        channel=discord.utils.get(member.guild.channels,id=channel)
        timenow=datetime.utcnow()
        embed=discord.Embed(title=f"{member} has left the server",description=f"{member} has left the server",color=0xffff00,timestamp=timenow)
        embed.set_thumbnail(url=member.avatar_url)
        await channel.send(embed=embed)    
  '''
  @commands.Cog.listener()
  async def on_raw_message_delete(self,payload):
    guild=self.bot.get_guild(payload.guild_id)
    channel=discord.utils.get(guild.channels,id=payload.channel_id)
    await channel.send(payload.message_id)
    await channel.send("est")'''

  @commands.Cog.listener()
  async def on_member_update(self,before, after):
    collection=db["logs"]
    a=collection.find_one({"_id":after.guild.id})
    if a["mode"]!="on":
      return
    channel=a["channel"]
    if channel==0:
      return
    
    channel=discord.utils.get(after.guild.channels,id=channel)
    timenow=datetime.utcnow()
 
    n = after.display_name 
    if n!=before.display_name:
      embed=discord.Embed(title=f"{after} nickname changed",description=f"{before.display_name} --> {after.display_name}",color=0xffff00,timestamp=timenow)
      embed.set_thumbnail(url=after.avatar_url)
      await channel.send(embed=embed)

    if before.roles!=after.roles:
      embed = discord.Embed(title=f"Role updates for {after}",
      color=0xffff00,
      timestamp=datetime.utcnow())
      embed.set_thumbnail(url=after.avatar_url)
      after_roles=[r.mention for r in after.roles if r not in before.roles]
      before_roles=[r.mention for r in before.roles if r not in after.roles]

      if len(after_roles)>0:
        embed.add_field(name=f"+{len(after_roles)} roles",value=", ".join(after_roles),inline=False)
      if len(before_roles)>0:
        embed.add_field(name=f"-{len(before_roles)} roles",value=", ".join(before_roles),inline=False)
      await channel.send(embed=embed)
    

  @commands.Cog.listener()
  async def on_message_edit(self,before,after):
    collection=db["logs"]
    a=collection.find_one({"_id": before.guild.id})
    if a["mode"]!="on":
      return
      
    channel=a["channel"]
    if channel==0:
      return
    channel=discord.utils.get(after.guild.channels,id=channel)
    
    if before.content != after.content:
      embed = discord.Embed(title=f"Message edited in {after.channel}", description=f"Edit by {after.author}.",#.display_name
      colour=0xffff00,
      timestamp=datetime.utcnow())
      embed.set_thumbnail(url=after.author.avatar_url)
      fields = [("Before", before.content, False),
      ("After", after.content, False)]

      for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

      await channel.send(embed=embed)

  
  @commands.Cog.listener()
  async def on_message_delete(self,message):
    collection=db["logs"]
    a=collection.find_one({"_id":message.guild.id})
    if a["mode"]=="on":
      channel=a["channel"]
      if channel!=0:
        channel=discord.utils.get(message.guild.channels,id=channel)
        timenow=datetime.utcnow() 
        embed=discord.Embed(title=f"A message by {message.author} was deleted in {message.channel}",description=message.content,color=0xffff00,timestamp=timenow)
        embed.set_thumbnail(url=message.author.avatar_url)
        await channel.send(embed=embed)
    coll=db["rr"]
    rrr=coll.find_one({"_id":message.guild.id})
    rr=rrr["rr"]
    try:
      a= str(message.id)
      rr1=[]
      for key in rr:
        if key!=a:
          rr1[key]=rr[key]

      coll.update_one({"_id":message.guild.id},{"$set":{"rr":rr1}})
    except KeyError:
      pass
  @commands.Cog.listener()
  async def on_bulk_message_delete(self,messages):
    collection=db["logs"]
    a=collection.find_one({"_id":messages.guild_id})
    if a["mode"]=="on":
      channel=a["channel"]
      if channel!=0:
        channel=discord.utils.get(messages.guild.channels,id=channel)
        timenow=datetime.utcnow() 
        embed=discord.Embed(title=f"Messages bulk deleted in {messages.channel}",description=len(messages),color=0xffff00,timestamp=timenow)

        await channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_user_update(self, before, after):
    collection=db["logs"]
    for guild in self.bot.guilds:
      a=collection.find_one({"_id":guild.id})
      if a["mode"]=="on":
        user=discord.utils.get(guild.members, id=after.id)
        if not user:
          pass
        else:
          channel=a["channel"]
          if channel!=0:
            channel=discord.utils.get(guild.channels,id=channel)

            if before.name != after.name:
              embed = discord.Embed(title=f"Username change by {after}",
              colour=0xffff00,
              timestamp=datetime.utcnow())
              embed.set_thumbnail(url=after.avatar_url)
              fields = [("Before", before, False),#.name
              ("After", after, False)]

              for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
              embed.set_thumbnail(url=after.avatar_url)
              await channel.send(embed=embed)

            if before.discriminator != after.discriminator:
              embed = discord.Embed(title=f"{after} changed their discriminator",
              colour=0xffff00,
              timestamp=datetime.utcnow())
              embed.set_thumbnail(url=after.avatar_url)

              fields = [("Before", before.discriminator, False),
                    ("After", after.discriminator, False)]

              for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

              await channel.send(embed=embed)

            if before.avatar_url != after.avatar_url:
              embed = discord.Embed(title="Avatar change by {after}",
              colour=0xffff00,
              timestamp=datetime.utcnow())

              embed.set_thumbnail(url=after.avatar_url)
              embed.set_image(url=after.avatar_url)
              await channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_guild_channel_create(self,channel):
    role=discord.utils.get(channel.guild.roles,name="mootmoot")
    await channel.set_permissions(role,send_messages=False)
    collection=db["logs"]
    a=collection.find_one({"_id":channel.guild.id})
    if a["mode"]!="on":
      return
      
    channels=a["channel"]
    if channels==0:
      return
    channelss=discord.utils.get(channel.guild.channels,id=channels)
    embed=discord.Embed(title=f"A channel was created in {channel.category}",description=f"{channel.mention} was created at {channel.created_at}",color=0xffff00,timestamp=datetime.utcnow())
    embed.add_field(name="Channel overwrites:",value=channel.overwrites,inline=False)
    await channelss.send(embed=embed)

  @commands.Cog.listener()
  async def on_guild_channel_delete(self,channel):
    collection=db["logs"]
    a=collection.find_one({"_id":channel.guild.id})
    if a["mode"]!="on":
      return
      
    channels=a["channel"]
    if channels==0:
      return
    channelss=discord.utils.get(channel.guild.channels,id=channels)
    embed=discord.Embed(title=f"A channel was deleted in {channel.category}", 
    description=f"{channel.mention} was deleted at {channel.created_at}",color=0xffff00,timestamp=datetime.utcnow())
    await channelss.send(embed=embed)

  @commands.Cog.listener()
  async def on_webhooks_update(self,channel):
    collection=db["logs"]
    a=collection.find_one({"_id":channel.guild.id})
    if a["mode"]!="on":
      return
      
    channels=a["channel"]
    if channels==0:
      return

    channels=discord.utils.get(channel.guild.channels,id=channels)

    embed=discord.Embed(title="A webhook was created",description=f"A webhook was created in {channel.mention} in {channel.category}",color=0xffff00,timestamp=datetime.utcnow())
    await channels.send(embed=embed)

  @commands.Cog.listener()
  async def on_guild_role_create(self,role):
    collection=db["logs"]
    a=collection.find_one({"_id":role.guild.id})
    if a["mode"]!="on":
      return
      
    channel=a["channel"]
    if channel==0:
      return

    channel=discord.utils.get(role.guild.channels,id=channel)

    embed=discord.Embed(title="A role was created",description=f"{role.mention} was created at {role.created_at}\nPermissions: {role.permissions}",timestamp=datetime.utcnow())
    await channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_guild_role_delete(self,role):
    collection=db["logs"]
    a=collection.find_one({"_id":role.guild.id})
    if a["mode"]!="on":
      return
      
    channel=a["channel"]
    if channel==0:
      return

    channel=discord.utils.get(role.guild.channels,id=channel)


    embed=discord.Embed(title="A role was deleted",description=f"{role.mention} was deleted\nPermissions: {role.permissions}",timestamp=datetime.utcnow())
    await channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_member_ban(self,guild,user):
    collection=db["logs"]
    a=collection.find_one({"_id":guild.id})
    if a["mode"]!="on":
      return
      
    channel=a["channel"]
    if channel==0:
      return

    channel=discord.utils.get(guild.channels,id=channel)

    embed=discord.Embed(title=f"{user} was banned!",description=f"{user} must have been a bad boy/girl!",timestamp=datetime.utcnow())

    await channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_member_unban(self,guild,user):
    collection=db["logs"]
    a=collection.find_one({"_id":guild.id})
    if a["mode"]!="on":
      return
      
    channel=a["channel"]
    if channel==0:
      return

    channel=discord.utils.get(guild.channels,id=channel)

    embed=discord.Embed(title=f"{user} was unbanned!",description="I wonder why they were banned in the first place",timestamp=datetime.utcnow())

    await channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_invite_create(self,invite):
    pass
  #https://discordpy.readthedocs.io/en/latest/api.html#discord.on_raw_message_edit


  @commands.Cog.listener()
  async def on_guild_channel_update(self,before,after):
    collection=db["logs"]
    a=collection.find_one({"_id":after.guild.id})
    if a["mode"]!="on":
      return
      
    channel=a["channel"]
    if channel==0:
      return

    channel=discord.utils.get(after.guild.channels,id=channel)
    
    if before.name!=after.name:
      embed=discord.Embed(title=f"{after.name} was updated",name=f"**Channel name update:**{before} ---> {after}",color=0xffff00,timestamp=datetime.utcnow())
      await channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_voice_state_update(self,member,before,after):
    pass
  
  '''@commands.Cog.listener()
  async def on_guild_emojis_update(self,guild,before,after):
    collection=db["logs"]
    a=collection.find_one({"_id":guild.id})
    if a["mode"]!="on":
      return
      
    channel=a["channel"]
    if channel==0:
      return

    channel=discord.utils.get(guild.channels,id=channel)
    
    if before.guild.emojis'''

  @commands.Cog.listener()
  async def on_guild_role_update(self,before,after):
    collection=db["logs"]
    a=collection.find_one({"_id":after.guild.id})
    if a["mode"]!="on":
      return
      
    channel=a["channel"]
    if channel==0:
      return

    channel=discord.utils.get(after.guild.channels,id=channel)
    if before.name!=after.name:
      embed=discord.Embed(title=f"{after.name} was updated",description=f"**Role name change:** {before.name} ---> {after.name}",color=0xffff00,timestamp=datetime.utcnow())
    
    elif before.role.permissions!=after.role.permissions:
      embed=discord.Embed(title=f"{after.name} was updated",description=f"Role permissions were updated for {after.name}",color=0xffff00,timestamp=datetime.utcnow())
    
    await channel.send(embed=embed)

    
      
    



def setup(bot):
  bot.add_cog(Events(bot))
