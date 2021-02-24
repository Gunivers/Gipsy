from utils import Gunibot, MyContext
import discord
import random
from discord.ext import commands

class Misc(commands.Cog):

    def __init__(self, bot: Gunibot):
        self.bot = bot
        self.file = "misc"

    #------------------#
    # Commande /cookie #
    #------------------#

    @commands.command(name="cookie")
    @commands.guild_only()
    async def cookie(self, ctx: MyContext, *, user: discord.User = None):
        """The most usefull command: give a cookie to yourself or someone else."""
        if user:
            message = await self.bot._(ctx.guild.id, 'misc.cookie.give', to=user.mention, giver=ctx.author.mention)
        else:
            message = await self.bot._(ctx.guild.id, 'misc.cookie.self', to=ctx.author.mention)

        # Créer un webhook qui prend l'apparence d'un Villageois
        webhook: discord.Webhook = await ctx.channel.create_webhook(name=f"Villager #{random.randint(1, 9)}")
        await webhook.send(content=message, avatar_url="https://d31sxl6qgne2yj.cloudfront.net/wordpress/wp-content/uploads/20190121140737/Minecraft-Villager-Head.jpg")
        await webhook.delete()
        await ctx.message.delete()

    #---------------------#
    # Commande /flipacoin #
    #---------------------#

    @commands.command(name="flipacoin", aliases=['fc'])
    async def flip(self, ctx: MyContext):
        """Flip a coin."""
        a = random.randint(-100, 100)
        if a > 0:
            await ctx.send(await self.bot._(ctx.guild.id, 'misc.flipacoin.tails'))
        elif a < 0:
            await ctx.send(await self.bot._(ctx.guild.id, 'misc.flipacoin.heads'))
        else:
            await ctx.send(await self.bot._(ctx.guild.id, 'misc.flipacoin.side'))

    #------------------#
    # Commande /dataja #
    #------------------#

    @commands.command(name="dataja")
    async def dataja(self, ctx: MyContext):
        """Don't ask to ask, just ask."""
        await ctx.send(await self.bot._(ctx.guild.id, 'misc.dataja'))
    

    @commands.command(name="kill")
    async def kill(self, ctx: MyContext, *, target: str=None):
        """Wanna kill someone?"""
        if target is None: # victim is user
            victime = ctx.author.display_name
            ex = ctx.author.display_name.replace(" ","_")
        else: # victim is target
            victime = target
            ex = target.replace(" ","_")
        author = ctx.author.mention
        tries = 0
        # now let's find a random answer
        msg = 'misc.kills'
        while msg.startswith('misc.kills') or ('{0}' in msg and target is None and tries<50):
            choice = random.randint(0, 23)
            msg = await self.bot._(ctx.channel, f"misc.kills.{choice}")
            tries += 1
        # and send it
        await ctx.send(msg.format(author, victime, ex), allowed_mentions=discord.AllowedMentions.none())


# The end.
def setup(bot):
    bot.add_cog(Misc(bot))
