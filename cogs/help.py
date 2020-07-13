import discord,dns,pymongo,os,random
from discord.ext import commands
from datetime import datetime


mongosecret=os.environ.get("mongosecret")
client = pymongo.MongoClient(mongosecret)
db=client["bot"]

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def help(self,ctx,cat=None):
    '''collection=db["prefix"]
    try:
      prefixes=collection.find_one({"_id":ctx.guild.id})
      prefix=prefixes["prefix"]
    except AttributeError:
      prefix=";"'''
    prefix=";"
    r = random.randint(0, 255)
    g=random.randint(0, 255)
    b=random.randint(0, 255)
    colour = discord.Colour.from_rgb(r=r, g=g, b=b)
    if not cat:
      embed=discord.Embed(title="Help menu for Mootbot",description=f"Prefix: `{prefix}`\nModeration: \nmute, unmute, softban, ban, kick, warn, purge, setup (raid protection setup), warns, log, logtoggle (turns logs on or off), avatar, userinfo, say, rr\nRun ;help description for a more in depth guide on the commands",color=colour)
    
    elif cat.lower()=="description":
      embed=discord.Embed(title="Help menu for Mootbot",description=f"Prefix: `{prefix}`\nModeration: \nmute:This command mutes a user. Use it like `;mute <member>`\nunmute: This command unmutes a user. Use it like `;unmute <member>` \nsoftban:this command bans then unbans a user. Use it like `;softban <member>`\nban:This command bans a user. Use it like `;ban <member>`\nkick:This command kicks a user. Use it like `kick <user>` \nwarn: this command warns user; use it like `;warn <user> <reason>\nremovewarn: Ths command removes warns from a user. use it like `;removewarn <user> <warn number>`\npurge: Bulk deletes messages. use it like `;purge <number of messages>\nsetup: sets up the raid protection. Just run `;setup` to get started or if you want to turn it off, run `;setup off`\nwarns: Checks warns for a user, run `;warns <user>` to get their warns\nlog: Use it to switch logging channels. You have to use logtoggle command to turn logs on or off. Use the log command like `;log <channel>`\nlogtoggle: This command toggles logs on or off. Must have it set to on to have logs. It defaults to off. Use it like `;logtoggle <on or off>`\navatar: shows your avatar or a users avatar. Use it like `;avatar <user>` Defaults to yourself.\nuserinfo: Gives info on the user. Defaults to yourself. Use it like `;ui <user>`\nsay: say a message in a channel. The channel argument is optional and defaults to the current channel Use it like `;say <channel> <message>`\nrr: sets up reaction roles in a channel. Run it like `;rr <channel>`. The channel defaults to the current channel",color=colour)
    await ctx.send(embed=embed)

  @commands.command()
  async def info(self,ctx):
    embed=discord.Embed(title="Info for Mootbot",description="Mootbot is a bot made to prevent raids\nand moot new users if their account is too\nnew. It also has reaction roles and moderation\nfeatures to help protect you and your server\nfrom toxic raiders!",color=0xffff00,timestamp=datetime.utcnow())
    embed.add_field(name="Developer:",value="This bot was made possible by Venimental#1289.\nThanks to [YT] Cubeblazer(CFOP-9 PB3.944)#0031 for helping out when I needed it",inline=False)
    embed.add_field(name="Server count:",value=len(self.bot.guilds),inline=False)
    embed.add_field(name="Invite:",value="run `;invite`",inline=False)
    embed.add_field(name="Support server:",value="Yet to come",inline=False)
    await ctx.send(embed=embed)



def setup(bot):
  bot.add_cog(Help(bot))
