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
      embed=discord.Embed(title="Help menu for Mootbot",description=f"Prefix: `{prefix}`\nCommands: \nmute, unmute, softban, ban, kick, warn, purge, setup (raid protection setup), warns, log, logtoggle (turns logs on or off), avatar, invite, userinfo, say, rr",color=colour,timestamp=datetime.utcnow())
      embed.set_footer(text="Run ;help description for a more in depth guide on the commands")
    
    elif cat.lower()=="description":
      embed=discord.Embed(title="Help menu for Mootbot",description=f"Prefix: `{prefix}`\nCommands:\n**invite** : This gives the bot invite link. \n**mute** : This command mutes a user. Use it like `;mute <member>`\n**unmute** : This command unmutes a user. Use it like `;unmute <member>` \n**softban** : This command bans then unbans a user. Use it like `;softban <member>`\n**ban** :This command bans a user. Use it like `;ban <member>`\n**kick** : This command kicks a user. Use it like `kick <user>`\n**warn** : This command warns a user; use it like `;warn <user> <reason>`\n**removewarn** : Ths command removes warns from a user. Use it like `;removewarn <user> <warn number>`\n**purge** : Bulk deletes messages. use it like `;purge <number of messages>`\n**setup** : sets up the raid protection. Just run `;setup` to get started or if you want to turn it off, run `;setup off`\n**warns** : Checks warns for a user, run `;warns <user>` to get their warns\n**log**: Use it to switch logging channels. You have to use logtoggle command to turn logs on or off. Use the log command like `;log <channel>`\n**logtoggle** : This command toggles logs on or off. Must have it set to on to have logs. It defaults to on if you only run the command. Use it like `;logtoggle <on or off>`\n**avatar** : shows your avatar or a users avatar. Use it like `;avatar <user>` Defaults to yourself.\n**userinfo** : Gives info on the user. Defaults to yourself. Use it like `;ui <user>`\n**say** : say a message in a channel. The channel argument is optional and defaults to the current channel Use it like `;say <channel> <message>`\n**rr** : sets up reaction roles in a channel. Run it like `;rr <channel>`. The channel defaults to the current channel",color=colour,timestamp=datetime.utcnow())
    else:
      embed=discord.Embed(title="Help menu for mootbot",description=f"Unfortunately the help category of {cat} could not be found",color=colour,timestamp=datetime.utcnow())
    await ctx.send(embed=embed)

  @commands.command()
  async def info(self,ctx):
    embed=discord.Embed(title="Info for Mootbot",description="Mootbot is a bot made to prevent raids\nand moot new users if their account is too\nnew. It also has reaction roles and moderation\nfeatures to help protect you and your server\nfrom toxic raiders! If you are a server owner, mootbot is a must for you and your community!",color=0xffff00,timestamp=datetime.utcnow())
    embed.add_field(name="Developer:",value="This bot was made possible by Venimental#1289.\nThanks to [YT] Cubeblazer(CFOP-9 PB3.944)#0031 for helping out when I needed it",inline=False)
    embed.add_field(name="Server count:",value=len(self.bot.guilds),inline=False)
    embed.add_field(name="Invite:",value="run `;invite`",inline=False)
    embed.add_field(name="Support server:",value="Yet to come",inline=False)
    await ctx.send(embed=embed)



def setup(bot):
  bot.add_cog(Help(bot))
