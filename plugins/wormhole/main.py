from typing import List, Union
import discord
from discord.ext import commands

import checks
from utils import Gunibot, MyContext
from aiohttp import ClientSession


async def sendMessage(msg: discord.Message, webhook: discord.Webhook, username: str, pp_guild: bool):
    files = [await x.to_file() for x in msg.attachments]
    # grab mentions from the source message
    mentions = discord.AllowedMentions(
        everyone=msg.mention_everyone,
        users=msg.mentions,
        roles=msg.role_mentions)
    username = username.replace("{user}", msg.author.name, 10).replace("{guild}", msg.guild.name, 10).replace(
        "{channel}", msg.channel.name, 10)
    avatar_url = msg.author.avatar_url
    if pp_guild:
        avatar_url = msg.guild.icon_url
    new_msg: discord.WebhookMessage = await webhook.send(content=msg.content,
                                                         files=files,
                                                         embeds=msg.embeds,
                                                         avatar_url=avatar_url,
                                                         username=username,
                                                         allowed_mentions=discord.AllowedMentions.none(),
                                                         wait=True)
    # edit the message to include mentions without notifications
    if mentions.roles or mentions.users or mentions.everyone:
        await new_msg.edit(allowed_mentions=mentions)


class PermissionType(commands.Converter):
    types = ['w', 'r', 'wr']

    def __init__(self, action: Union[str, int] = None):
        if isinstance(action, str):
            self.type = self.types.index(action)
        elif isinstance(action, int):
            self.type = action
        else:
            return
        self.name = self.types[self.type]

    async def convert(self, ctx: commands.Context, argument: str):
        if argument in self.types:
            return PermissionType(argument)
        raise commands.errors.BadArgument("Unknown permission type")


class Wormhole:
    def __init__(self, name: str, privacy: bool, owners: List[int], bot: Gunibot, channels: int):
        self.bot = bot
        self.name = name
        self.privacy = privacy
        self.owners = owners
        self.channels = channels

    def to_str(self) -> str:
        """Transform the Wormhole to a human-readable string"""
        private = (self.privacy == 1)
        owners: List[str] = []
        for o in self.owners:
            user = self.bot.get_user(o)
            owners.append(user.name if user else "Unknown user")
        return f"Wormhole: {self.name}\n????????? Private: {private} - Admins: {', '.join(owners)} - **{self.channels}** Discord channels are linked"


class WormholeChannel:
    def __init__(self, name: str, channelID: int, guildID: int, perms: str):
        self.wh = name
        self.channelID = channelID
        self.guildID = guildID
        self.perms = perms

    def to_str(self) -> str:
        """Transform the Channel to a human-readable string"""
        perms = "Write and Read" if self.perms == "wr" else "Read" if self.perms == "r" else "Write"
        return f"Channel: <#{self.channelID}>\n????????? Linked to **{self.wh}** - Permissions: *{perms}*"


class Wormholes(commands.Cog):

    def __init__(self, bot: Gunibot):
        self.bot = bot
        self.file = "wormhole"

    def db_get_wormholes(self) -> List[Wormhole]:
        """Get every wormhole"""
        query = 'SELECT rowid, * FROM wormhole_list'
        wormholes = self.bot.db_query(query, (), astuple=True)
        # comes as: (rowid, name, privacy)
        res: List[Wormhole] = list()
        for row in wormholes:
            query = "SELECT rowid, * FROM wormhole_admin WHERE name = ?"
            owners = self.bot.db_query(query, (row[1],), astuple=True)
            # come as: (rowid, name, admin)
            owner_list: List[int] = []
            for o in owners:
                owner_list.append(o[2])
            query = "SELECT * FROM wormhole_channel WHERE name = ?"
            channels = len(self.bot.db_query(query, (row[1],), astuple=True))
            res.append(Wormhole(*row[1:3], owner_list, self.bot, channels))
            res[-1].id = row[0]
        return res if len(res) > 0 else None

    def db_get_channels(self, guildID: int):
        """Get every channel linked to a wormhole in this channel"""
        query = "SELECT rowid, * FROM wormhole_channel WHERE guildID = ?"
        channels = self.bot.db_query(query, (guildID,), astuple=True)
        # come as: (rowid, name, channelID, guildID, type, webhookID, webhookTOKEN)
        res: List[WormholeChannel] = []
        for row in channels:
            res.append(WormholeChannel(*row[1:5]))
            res[-1].id = row[0]
        return res if len(res) > 0 else None

    def check_is_admin(self, wormhole: str, user: int):
        """Check if the provided user is an admin of the provided wormhole"""
        query = "SELECT 1 FROM wormhole_admin WHERE name = ? AND admin = ?"
        query_res = self.bot.db_query(query, (wormhole, user))
        return len(query_res) > 0

    def check_wh_exists(self, wormhole: str):
        """Check if a wormhole already exist with the provided name"""
        query = "SELECT 1 FROM wormhole_list WHERE name = ?"
        query_res = self.bot.db_query(query, (wormhole,), astuple=True)
        # comes as: (name, privacy, webhook_name, webhook_pp_guild)
        return len(query_res) > 0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Executed every time a message is sent"""
        if message.author.bot or "wormhole unlink" in message.content or "wh unlink" in message.content:
            return
        query = "SELECT name, type FROM wormhole_channel WHERE channelID = ?"
        wh_channel = self.bot.db_query(query, (message.channel.id,), astuple=True, fetchone=True)
        # come as: (name, type)
        if len(wh_channel) == 0:  # Check if there is a wormhole linked to the current channel
            return
        if "w" not in wh_channel[1]:  # Check if the current channel as Write permissions
            return
        wh_name = wh_channel[0]
        query = "SELECT * FROM wormhole_channel WHERE name = ? AND type LIKE '%r%' AND NOT channelID = ?"
        wh_targets = self.bot.db_query(query, (wh_name, message.channel.id), astuple=True)
        # come as: (name, channelID, guildID, type, webhookID, webhookTOKEN)
        query = "SELECT webhook_name, webhook_pp FROM wormhole_list WHERE name = ?"
        wormhole = self.bot.db_query(query, (wh_name,), astuple=True, fetchone=True)
        # come as: (webhook_name, webhook_pp)
        async with ClientSession() as session:
            async_adaptater = discord.AsyncWebhookAdapter(session)
            for row in wh_targets:
                # We're starting to send the message in all the channels linked to that wormhole
                channel: discord.TextChannel = self.bot.get_channel(row[1])
                if channel:
                    webhook = discord.Webhook.partial(row[4], row[5], adapter=async_adaptater)
                    await sendMessage(message, webhook, wormhole[0], wormhole[1])


    @commands.group(name="wormhole", aliases=["wh"])
    @commands.guild_only()
    @commands.cooldown(2, 15, commands.BucketType.channel)
    async def wormhole(self, ctx: MyContext):
        """Connect 2 points through space-time (or 2 text channels if you prefer)"""
        if ctx.subcommand_passed is None:
            await ctx.send_help("wormhole")


    @wormhole.command(name="add")
    async def add(self, ctx: MyContext, name: str, privacy: bool = True, webhook_name: str = "{user}",
                  webhook_pp_guild: bool = False):
        """Create a wormhole
        webhook_name is for how names will be displayed:
        for example: "{user} - {guild}"
        will display "fantomitechno - Gunivers"
        ?????? The " are required if you want spaces in your webhook name
        Available variables are {user}, {guild} and {channel}
        webhook_pp_guild is for which avatar will be the profile picture of the webhook
        if True it will be the Guild from where it comes
        and if False it will be the User who sent the message
        """
        if self.check_wh_exists(name):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.already-exists", name=name))
            return
        query = "INSERT INTO wormhole_list (name, privacy, webhook_name, webhook_pp) VALUES (?, ?, ?, ?)"
        self.bot.db_query(query, (name, privacy, webhook_name, webhook_pp_guild))
        query = "INSERT INTO wormhole_admin (name, admin) VALUES (?,?)"
        self.bot.db_query(query, (name, ctx.author.id))
        await ctx.send(await self.bot._(ctx.guild.id, "wormhole.success.wormhole-created"))

    @wormhole.command(name="link")
    @commands.check(checks.is_server_manager)
    async def link(self, ctx: MyContext, wormhole: str, perms: PermissionType = PermissionType("wr")):
        """Link the current channel to a wormhole
        Permissions are Write and/or Read, defined by their first letter
        Examples:
            - a channel with the permissions 'wr' can Send and Receive messages from the wormhole
            - a channel with 'r' can only receive
        """
        query = "SELECT * FROM wormhole_channel WHERE channelID = ?"
        row = self.bot.db_query(query, (ctx.channel.id,), fetchone=True)
        if len(row) != 0:
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.already-linked", c=ctx.channel))
            return
        if not self.check_wh_exists(wormhole):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-exists", name=wormhole))
        else:
            if not self.check_is_admin(wormhole, ctx.author.id):
                await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-admin"))
                return
            query = "INSERT INTO wormhole_channel (name, channelID, guildID, type, webhookID, webhookTOKEN) VALUES (?, ?, ?, ?, ?, ?)"
            webhook: discord.Webhook = await ctx.channel.create_webhook(name=wormhole)
            self.bot.db_query(query, (wormhole, ctx.channel.id, ctx.guild.id, perms.name, webhook.id, webhook.token))
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.success.channel-linked"))

    @wormhole.command(name="unlink")
    @commands.check(checks.is_server_manager)
    async def unlink(self, ctx: MyContext):
        """Unlink the current channel to a wormhole"""
        query = "SELECT * FROM wormhole_channel WHERE channelID = ?"
        wh_channel = self.bot.db_query(query, (ctx.channel.id,), astuple=True, fetchone=True)
        # comes as: (name, channelID, guildID, type, webhookID, webhookTOKEN)
        if len(wh_channel) == 0:
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-linked"))
            return
        query = "DELETE FROM wormhole_channel WHERE channelID = ? AND name = ?"
        async with ClientSession() as session:
            webhook = discord.Webhook.partial(wh_channel[4], wh_channel[5], adapter=discord.AsyncWebhookAdapter(session))
            await webhook.delete()
        self.bot.db_query(query, (wh_channel[0], ctx.channel.id))
        await ctx.send(await self.bot._(ctx.guild.id, "wormhole.success.channel-unlinked"))

    @wormhole.command(name="remove", aliases=["delete"])
    async def remove(self, ctx: MyContext, wormhole: str):
        """Delete a wormhole"""
        if not self.check_wh_exists(wormhole):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-exists", name=wormhole))
            return
        if not self.check_is_admin(wormhole, ctx.author.id):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-admin"))
            return
        query = "DELETE FROM wormhole_channel WHERE name = ?"
        self.bot.db_query(query, (wormhole,))
        query = "DELETE FROM wormhole_admin WHERE name = ?"
        self.bot.db_query(query, (wormhole,))
        query = "DELETE FROM wormhole_list WHERE name = ?"
        self.bot.db_query(query, (wormhole,))
        await ctx.send(await self.bot._(ctx.guild.id, "wormhole.success.wormhole-deleted"))

    @wormhole.group(name="modify", aliases=["edit"])
    async def modify(self, ctx: MyContext):
        """Edit a wormhole"""
        if ctx.subcommand_passed is None:
            await ctx.send_help("wormhole modify")

    @modify.command(name="privacy")
    async def modify_privacy(self, ctx: MyContext, wormhole: str, privacy: str):
        """Edit the privacy of a wormhole
        Options for privacy are "public" and "private" """
        if privacy.lower() not in ["public", "private"]:
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-privacy"))
            return
        if not self.check_wh_exists(wormhole):
            return await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-exists", name=wormhole))
        if not self.check_is_admin(wormhole, ctx.author.id):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-admin"))
            return
        query = "UPDATE wormhole_list SET privacy = ? WHERE name = ?"
        private = privacy.lower() == "private"
        self.bot.db_query(query, (private, wormhole))
        await ctx.send(await self.bot._(ctx.guild.id, "wormhole.success.modified"))

    @modify.command(name="webhook_name")
    async def modify_webhook_name(self, ctx: MyContext, wormhole: str, *, webhook_name: str):
        """webhook_name is for how names will be displayed:
        for example: "{user} - {guild}"
        will display "fantomitechno - Gunivers"
        Available variables are {user}, {guild} and {channel}"""
        if not self.check_wh_exists(wormhole):
            return await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-exists", name=wormhole))
        if not self.check_is_admin(wormhole, ctx.author.id):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-admin"))
            return
        query = "UPDATE wormhole_list SET webhook_name = ? WHERE name = ?"
        self.bot.db_query(query, (webhook_name, wormhole))
        await ctx.send(await self.bot._(ctx.guild.id, "wormhole.success.modified"))

    @modify.command(name="webhook_pp")
    async def modify_webhook_pp(self, ctx: MyContext, wormhole: str, webhook_pp: bool):
        """webhook_pp_guild is for which avatar will be the profile picture of the webhook
        if True it will be the Guild from where it comes
        and if False it will be the User who sent the message"""
        if not self.check_wh_exists(wormhole):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-exists", name=wormhole))
            return
        if not self.check_is_admin(wormhole, ctx.author.id):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-admin"))
            return
        query = "UPDATE wormhole_list SET webhook_pp = ? WHERE name = ?"
        self.bot.db_query(query, (webhook_pp, wormhole))
        await ctx.send(await self.bot._(ctx.guild.id, "wormhole.success.modified"))

    @wormhole.group(name="admin")
    async def admin(self, ctx: MyContext):
        """Add or remove Wormhole Admins"""
        if ctx.subcommand_passed is None:
            await ctx.send_help("wormhole admin")

    @admin.command(name="add")
    async def admin_add(self, ctx: MyContext, wormhole: str, user: discord.User):
        """Add a user as a wormhole admin"""
        if not self.check_wh_exists(wormhole):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-exists", name=wormhole))
            return
        if not self.check_is_admin(wormhole, ctx.author.id):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-admin"))
            return
        query = "SELECT 1 FROM wormhole_admin WHERE name = ? AND admin = ?"
        isAlready = len(self.bot.db_query(query, (wormhole, user.id))) > 0
        if not isAlready:
            query = "INSERT INTO wormhole_admin (name, admin) VALUES (?, ?)"
            self.bot.db_query(query, (wormhole, user.id))
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.success.admin-added"))
        else:
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.already-admin", user=user.name))

    @admin.command(name="remove", aliases=['revoke'])
    async def admin_remove(self, ctx: MyContext, wormhole: str, user: discord.User):
        """Revoke an admin of a wormhole"""
        if not self.check_wh_exists(wormhole):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-exists", name=wormhole))
            return
        if not self.check_is_admin(wormhole, ctx.author.id):
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-admin"))
            return
        query = "SELECT 1 FROM wormhole_admin WHERE name = ? AND admin = ?"
        isAlready = len(self.bot.db_query(query, (wormhole, user.id))) > 0
        if isAlready:
            query = "DELETE FROM wormhole_admin WHERE admin = ? AND name = ?"
            self.bot.db_query(query, (user.id, wormhole))
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.success.admin-removed"))
        else:
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.not-admin", user=user.name))

    @wormhole.group(name="list")
    async def list(self, ctx: MyContext):
        """Get a list of available wormholes or channels"""
        if ctx.subcommand_passed is None:
            await ctx.send_help("wormhole list")

    @list.command(name="wormhole", aliases=["wh"])
    async def list_wh(self, ctx: MyContext):
        """List all wormholes"""
        wormholes = self.db_get_wormholes()
        if not wormholes:  # we can't send an empty list
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.no-wormhole", p=ctx.prefix))
            return
        txt = "\n".join([w.to_str() for w in wormholes])
        await ctx.send(txt)

    @list.command(name="channel")
    async def list_channel(self, ctx: MyContext):
        """List all channels linked to a Wormhole in the current server"""
        channels = self.db_get_channels(ctx.guild.id)
        if not channels:  # we can't send an empty list
            await ctx.send(await self.bot._(ctx.guild.id, "wormhole.error.no-channels", p=ctx.prefix))
            return
        txt = "\n".join([c.to_str() for c in channels])
        await ctx.send(txt)


def setup(bot):
    bot.add_cog(Wormholes(bot))
