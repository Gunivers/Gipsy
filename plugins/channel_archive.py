import discord
from discord.ext import commands
from utils import Gunibot, MyContext


class Channel_Archive(commands.Cog):

    def __init__(self, bot: Gunibot):
        self.bot = bot
        self.file = "channel_archive"
        self.config_options = ['archive_category','archive_duration']

    #-------------------#
    # Commande /archive #
    #-------------------#

    @commands.command(name="list_archive")
    @commands.guild_only()
    async def list_archive(self, ctx: MyContext):

        # Get records
        query = f"SELECT * FROM archive WHERE guild = {ctx.guild.id}"
        records = self.bot.db_query(query, ())

        # Print each record
        i = 0
        message = ""
        if len(records) > 0:
            for record in records:
                i+=1
                if i != 1:
                    message += "\n"
                if self.bot.get_channel(record["channel"]) is not None:
                    message += self.bot.get_channel(record["channel"]).mention + " - " + record["timestamp"]
                else:
                    message += "#deleted-channel - " + record["timestamp"]
            await ctx.send(embed=discord.Embed(description=message,colour=discord.Colour.red()))

        else:
            await ctx.send(embed=discord.Embed(description=await self.bot._(ctx.guild.id, 'archive_channel.no_channel'),colour=discord.Colour.red()))

    @commands.command(name="clear_archive")
    @commands.guild_only()
    async def clear_archive(self, ctx: MyContext):

        # Get archive duration
        config = self.bot.server_configs[ctx.guild.id]
        duration = config["archive_duration"]
        archive_category = config["archive_category"]

        # Clear db records corresponding to channels outside the archive category
        query = f"SELECT * FROM archive WHERE guild = {ctx.guild.id}"
        records = self.bot.db_query(query, ())
        
        unarchived = 0

        for record in records:
            if self.bot.get_channel(record["channel"]) is not None:
                if self.bot.get_channel(record["channel"]).category.id != archive_category:
                    query = f"DELETE FROM archive WHERE channel = {record['channel']} AND guild = {ctx.guild.id}"
                    unarchived += 1
                    self.bot.db_query(query, ())

        # Get & delete old channels
        query = f"SELECT * FROM archive WHERE timestamp <= datetime('now','-{duration} seconds') AND guild = {ctx.guild.id}"
        records = self.bot.db_query(query, ())

        removed_channels = 0
        removed_records = 0

        for record in records:
            if self.bot.get_channel(record["channel"]) is not None:
                if self.bot.get_channel(record["channel"]).category.id == archive_category:

                    # Remove channels
                    removed_channels += 1
                    await self.bot.get_channel(record["channel"]).delete(reason="Exceeded archive duration.")

                    # Remove record
                    removed_records += 1
                    query = f"DELETE FROM archive WHERE channel = {record['channel']} AND guild = {ctx.guild.id}"
                    self.bot.db_query(query, ())

            else:
                # Remove records associated to deleted channels
                removed_records += 1
                query = f"DELETE FROM archive WHERE channel = {record['channel']} AND guild = {ctx.guild.id}"
                self.bot.db_query(query, ())


        # Send confirmation
        message = ""
        if removed_channels == 0:
            message += await self.bot._(ctx.guild.id, 'archive_channel.channel_no_deleted')
        elif removed_channels == 1:
            message += await self.bot._(ctx.guild.id, 'archive_channel.channel_one_deleted')
        else:
            message += await self.bot._(ctx.guild.id, 'archive_channel.channel_several_deleted', count=removed_channels)

        message += "\n"
        if unarchived == 0:
            message += await self.bot._(ctx.guild.id, 'archive_channel.unarchived_no_deleted')
        elif unarchived == 1:
            message += await self.bot._(ctx.guild.id, 'archive_channel.unarchived_one_deleted')
        else:
            message += await self.bot._(ctx.guild.id, 'archive_channel.unarchived_several_deleted', count=unarchived)

        message += "\n"
        if removed_records == 0:
            message += await self.bot._(ctx.guild.id, 'archive_channel.record_no_deleted')
        elif removed_records == 1:
            message += await self.bot._(ctx.guild.id, 'archive_channel.record_one_deleted')
        else:
            message += await self.bot._(ctx.guild.id, 'archive_channel.record_several_deleted', count=removed_records)


        await ctx.send(embed=discord.Embed(description=message,colour=discord.Colour.green()))

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

            # Add record to database
            query = "INSERT INTO archive (guild, channel) VALUES (?, ?)"
            self.bot.db_query(query, (ctx.guild.id, channel.id))

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
