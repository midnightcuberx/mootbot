import discord,dns,pymongo,os,random
from discord.ext import commands


mongosecret=os.environ.get("mongosecret")
client = pymongo.MongoClient(mongosecret)
db=client["bot"]

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def help(self,ctx,cat=None):
    collection=db["prefix"]
    try:
      prefixes=collection.find_one({"_id":ctx.guild.id})
      prefix=prefixes["prefix"]
    except AttributeError:
      prefix=";"
    r = random.randint(0, 255)
    g=random.randint(0, 255)
    b=random.randint(0, 255)
    colour = discord.Colour.from_rgb(r=r, g=g, b=b)
    if not cat:
      embed=discord.Embed(title="Help menu for Mootbot",description=f"Prefix: `{prefix}`\nModeration: \nmute, unmute, softban, ban, kick, invitetoggle,purge",color=colour)
      await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Help(bot))
