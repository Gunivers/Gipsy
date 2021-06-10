import discord
from discord.ext import commands
from utils import Gunibot, MyContext
from typing import List


class roleSaver(commands.Cog):

    def __init__(self, bot: Gunibot):
        self.bot = bot
        self.file = "roleSaver"
        self.config_options = ['rs_enabled', 'rs_blacklist', 'rs_nickname']

    def db_get_savedrole(self, memberID: int, guildID: int) -> List[discord.Role]:
        """Get every saved role of a specific user on a specific guild"""
        query = 'SELECT rowid, * FROM saved_role WHERE memberID=? AND guild=?'
        liste = self.bot.db_query(query, (memberID, guildID), astuple=True)
        # comes as: (rowid, guild, memberID, roles, nickname)
        res: List[discord.Role] = list()
        for row in liste:
            print(row)
            res.append(row[3])
            #res[-1].id = row[0]
        return res if len(res) > 0 else None
    
    def db_saverole(self, member: discord.Member):
        is_saved = self.db_get_savedrole(member.id, member.guild.id)
        if is_saved is None:
            query = 'INSERT INTO saved_role (roles, nickname, memberID, guild) VALUES (?, ?, ?, ?)'
        else:
            query = "UPDATE saved_role SET roles=? AND nickname = ? WHERE memberID=? AND guild=?"
        roles = ''
        for i in member.roles:
            roles += str(i.id)+","
        roles = roles[:-1]
        self.bot.db_query(query, (roles, member.nick, member.id, member.guild.id))

    async def give_saved_roles(self, member: discord.Member):
        g = member.guild
        config = self.bot.server_configs[g.id]
        enabled = config["rs_enabled"]
        if not enabled:  # if nothing has been setup
            return

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Called when a member joins a guild"""
        g = member.guild
        if not g.me.guild_permissions.manage_roles:  # if not allowed to manage roles
            self.bot.log.info(f"Module - RoleSaver: Missing \"manage_roles\" permission on guild \"{g.name}\"")
            return

    @commands.command(name="test")
    async def test(self, ctx: MyContext):
        print(self.db_get_savedrole(ctx.author.id, ctx.guild.id))
    
    @commands.command(name="test2")
    async def test2(self, ctx: MyContext):
        self.db_saverole(ctx.author)


def setup(bot):
    bot.add_cog(roleSaver(bot))
