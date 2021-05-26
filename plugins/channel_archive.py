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
    async def archive(self, ctx: MyContext, channel: discord.TextChannel=None):
        """Archive a channel"""

        # Get archive category
        config = self.bot.server_configs[ctx.guild.id]
        archive = self.bot.get_channel(config["archive_category"])

        # Get target channel
        if channel is None:
            channel = ctx.channel

        # Check permissions
        if ctx.author.permissions_in(channel).manage_channels is True and ctx.author.permissions_in(channel).manage_permissions is True:

            # Move channel
            await channel.move(beginning=True, category=archive, sync_permissions=True, reason="Channel archived")

            # Success message
            embed = discord.Embed(
                description=await self.bot._(ctx.guild.id, 'archive_channel.success', channel=channel.mention),
                colour=discord.Colour(51711)
            )
        else:

            # Missing permission message
            embed = discord.Embed(
                description=await self.bot._(ctx.guild.id, 'archive_channel.missing_permission'),
                colour=0x992d22
            )
        
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Channel_Archive(bot))
