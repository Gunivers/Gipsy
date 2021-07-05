import discord
from discord.ext import commands
from utils import Gunibot


# Moves a message from its original channel to a parameterized channel using a given webhook
async def moveMessage(msg: discord.Message, webhook: discord.Webhook):
    files = [await x.to_file() for x in msg.attachments]
    # grab mentions from the source message
    mentions = discord.AllowedMentions(
        everyone=msg.mention_everyone,
        users=msg.mentions,
        roles=msg.role_mentions)
    new_msg: discord.WebhookMessage = await webhook.send(content=msg.content,
                                                         files=files,
                                                         embeds=msg.embeds,
                                                         avatar_url=msg.author.avatar_url,
                                                         username=msg.author.name,
                                                         allowed_mentions=discord.AllowedMentions.none(),
                                                         wait=True)
    # edit the message to include mentions without notifications
    if mentions.roles or mentions.users or mentions.everyone:
        await new_msg.edit(allowed_mentions=mentions)
    await msg.delete()

class MessageManager(commands.Cog):

    def __init__(self, bot: Gunibot):
        self.bot = bot
        self.file = ""

    #-------------------#
    # Command /imitate #
    #-------------------#

    @commands.command(name="imitate")
    @commands.guild_only()
    async def imitate(self, ctx: commands.Context, user: discord.User = None, *, text=None):
        """Say something with someone else's appearance"""

        if user and text and ctx.author.permissions_in(ctx.channel).manage_messages and ctx.author.permissions_in(ctx.channel).manage_nicknames:
            # Create a webhook in the image of the targeted member
            webhook = await ctx.channel.create_webhook(name=user.name)
            await webhook.send(content=text, avatar_url=user.avatar_url)

            # Deletes the original message as well as the webhook
            await webhook.delete()
            await ctx.message.delete()

    #----------------#
    # Command /move #
    #----------------#

    @commands.command(names="move", aliases=['mv'])
    @commands.guild_only()
    async def move(self, ctx: commands.Context, msg: discord.Message, channel: discord.TextChannel, *, confirm=True):
        """Move a message in another channel"""

        # Creates a webhook to resend the message to another channel
        webhook = await channel.create_webhook(name="Gunipy Hook")
        await moveMessage(msg, webhook)
        await webhook.delete()

        if confirm:
            # Creates an embed to notify that the message has been moved
            embed = discord.Embed(
                description=await self.bot._(ctx.guild.id, 'message_manager.move.confirm', user=msg.author.mention, channel=channel.mention),
                colour=discord.Colour(51711)
            )
            embed.set_footer(text=await self.bot._(ctx.guild.id, 'message_manager.move.footer', user=ctx.author.name))
            await ctx.send(embed=embed)

        # Deletes the command
        await ctx.message.delete()

    #-------------------#
    # Command /moveall #
    #-------------------#

    @commands.command(names="moveall", aliases=['mva'])
    @commands.guild_only()
    async def moveall(self, ctx: commands.Context, msg1: discord.Message, msg2: discord.Message, channel: discord.TextChannel, *, confirm=True):
        """Move several messages in another channel

        msg1 and msg2 need to be from the same channel"""

        embed = discord.Embed(
            description=await self.bot._(ctx.guild.id, 'message_manager.moveall.running', channel=channel.mention),
            colour=discord.Colour.blue()
        )
        embed.set_footer(text=await self.bot._(ctx.guild.id, 'message_manager.moveall.footer', user=ctx.author.name))
        await ctx.send(embed=embed)

        channel = self.bot.get_channel(channel.id)

        # Permission check
        perm1: discord.Permissions = ctx.channel.permissions_for(ctx.guild.me)
        perm2: discord.Permissions = channel.permissions_for(ctx.guild.me)

        if not (perm1.read_messages and perm1.read_message_history and perm1.manage_messages and perm2.manage_messages):
            await ctx.send(await self.bot._(ctx.guild.id, "message_manager.moveall.missing-perm"))
            self.bot.log.info(f"Alakon - /moveall: Missing permissions on guild \"{ctx.guild.name}\"")
            return

        # Checks that the messages are in the same channel
        if msg1.channel != msg2.channel:
            await ctx.send(await self.bot._(ctx.guild.id, "message_manager.moveall.channel-conflict"))
            return

        # Ensures that msg1 is indeed the first message of the two
        if msg1.created_at > msg2.created_at:
            msg2, msg1 = msg1, msg2

        # Retrieves the message list from msg1
        msgList = await msg1.channel.history(limit=100, after=msg1).flatten()
        if len(msgList) == 0:
            await ctx.send(await self.bot._(ctx.guild.id, "message_manager.moveall.no-msg"))
            return

        # Webhook creation (common to all messages)
        webhook = await channel.create_webhook(name="Gunipy Hook")

        # Moves successively all the messages in the list until msg2 is reached
        msg = msg1
        await moveMessage(msg, webhook)

        i = 0
        msg = msgList[0]
        while msg != msg2:
            await moveMessage(msg, webhook)
            i += 1
            msg = msgList[i]

        msg = msg2
        await moveMessage(msg, webhook)

        if confirm:
            # Creates an embed to notify that the messages have been moved
            embed = discord.Embed(
                description=await self.bot._(ctx.guild.id, 'message_manager.moveall.confirm', channel=channel.mention),
                colour=discord.Colour.green()
            )
            embed.set_footer(text=await self.bot._(ctx.guild.id, 'message_manager.moveall.footer', user=ctx.author.name))
            await ctx.send(embed=embed)
            await ctx.message.delete()

        await webhook.delete()


# The End.
def setup(bot):
    bot.add_cog(MessageManager(bot))
