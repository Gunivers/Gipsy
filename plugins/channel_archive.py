import discord
from discord.ext import commands
from utils import Gunibot, MyContext


class Channel_Archive(commands.Cog):

    def __init__(self, bot: Gunibot):
        self.bot = bot
        self.file = "channel_archive"
        self.config_options = ['archive_category']

    #-------------------#
    # Commande /archive #
    #-------------------#

    @commands.command(name="archive")
    @commands.guild_only()
    async def archive(self, ctx: MyContext):
        """Archive a channel"""

        embed = discord.Embed(
            description="Le salon a bien été déplacé même si en fait non pck pour le moment ça marche pas ...",
            colour=discord.Colour(51711)
        )

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Channel_Archive(bot))
