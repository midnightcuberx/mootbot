import discord,dns,pymongo,os,random,time,asyncio
from discord.ext import commands
from datetime import datetime

mongosecret=os.environ.get("mongosecret")
client = pymongo.MongoClient(mongosecret)
db=client["bot"]

class Events(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

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
        embed=discord.Embed(title=member,description=f"{member} has joined the server",color=0xffff00,timestamp=timenow)
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
        embed=discord.Embed(title=member,description=f"{member} has left the server",color=0xffff00,timestamp=timenow)
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
      embed=discord.Embed(title="Member nickname changed",description=f"{before.display_name} --> {after.display_name}",color=0xffff00,timestamp=timenow)
      await channel.send(embed=embed)

		elif before.roles != after.roles:
			embed = discord.Embed(title="Role updates for a member",
						  color=0xffff00,
						  timestamp=datetime.utcnow())
			fields = [("Before", ", ".join([r.mention for r in before.roles]), False),
					  ("After", ", ".join([r.mention for r in after.roles]), False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)
      await ctx.send(embed=embed)


  
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
        await channel.send(embed=embed)
  
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

def setup(bot):
  bot.add_cog(Events(bot))
