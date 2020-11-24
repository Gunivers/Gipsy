import discord
import time
from discord.ext import commands, tasks
from utils import Gunibot, MyContext
from checks import is_roles_manager


class Hypesquad(commands.Cog):

    def __init__(self, bot: Gunibot):
        self.bot = bot
        self.file = "hypesquad"
        self.roles_loop.start()
        if bot.get_cog("Sconfig"):
            bot.get_command("config hypesquad").enabled = True

    def cog_unload(self):
        self.roles_loop.cancel()
        if self.bot.get_cog("Sconfig"):
            self.bot.get_command("config hypesquad").enabled = False

    @tasks.loop(hours=12)
    async def roles_loop(self):
        """Check every 12h the members roles"""
        t1 = time.time()
        self.bot.log.debug("[hypesquad] Started roles check")
        count = 0 # count of edited members
        for g in self.bot.guilds:
            try:
                roles = await self.get_roles(g)
                if any(roles.values()): # if at least a role is set
                    for member in g.members:
                        count += await self.edit_roles(member, roles)
            except discord.Forbidden:
                # missing a perm
                self.bot.log.warn(f'[hypesquad] Unable to give roles in guild {g.id} ({g.name})')
        delta = round(time.time()-t1, 2)
        self.bot.log.info(f"[hypesquad] Finished roles check in {delta}s with {count} editions")

    @roles_loop.before_loop
    async def before_roles_loop(self):
        """Waiting until the bot is ready"""
        await self.bot.wait_until_ready()
    
    @roles_loop.error
    async def error_roles_loop(self, error: Exception):
        """When something went wrong during a loop round"""
        await self.bot.get_cog("Errors").on_error(error)

    async def edit_roles(self, member: discord.Member, roles: dict[str, discord.Role]) -> bool:
        """Add or remove roles to a member based on their hypesquad
        Returns True if a role has been given/removed"""
        if member.bot: # we don't want bots here
            return False
        roles_list = list(member.roles)
        unwanted = list()
        if member.public_flags.hypesquad_bravery:
            if roles['hs_bravery_role']:
                if roles['hs_bravery_role'] not in member.roles:
                    # add bravery
                    roles_list.append(roles['hs_bravery_role'])
                # remove brilliance balance none
                unwanted = (roles['hs_brilliance_role'], roles['hs_balance_role'], roles['hs_none_role'])
        elif member.public_flags.hypesquad_brilliance:
            if roles['hs_brilliance_role']:
                if roles['hs_brilliance_role'] not in member.roles:
                    # add brilliance
                    roles_list.append(roles['hs_brilliance_role'])
                # remove bravery balance none
                unwanted = (roles['hs_bravery_role'], roles['hs_balance_role'], roles['hs_none_role'])
        elif member.public_flags.hypesquad_balance:
            if roles['hs_balance_role']:
                # add balance
                if roles['hs_balance_role'] not in member.roles:
                    roles_list.append(roles['hs_balance_role'])
                # remove brilliance bravery none
                unwanted = (roles['hs_brilliance_role'], roles['hs_bravery_role'], roles['hs_none_role'])
        elif roles['hs_none_role']:
            if roles['hs_none_role'] not in member.roles:
                # add none
                roles_list.append(roles['hs_none_role'])
            # remove brilliance balance bravery
            unwanted = (roles['hs_brilliance_role'], roles['hs_balance_role'], roles['hs_bravery_role'])
        roles_list = [r for r in roles_list if r not in unwanted] # we remove unwanted roles
        roles_list = list(set(roles_list)) # we remove duplicates
        if set(roles_list) != set(member.roles): # check for any change (set doesn't care about ordering)
            # if changes were applied
            await member.edit(roles=roles_list, reason="Hypesquad roles")
            return True
        return False
    
    async def get_roles(self, guild: discord.Guild) -> dict[str, discord.Role]:
        """Get the hypesquads roles according to the guild config"""
        config = self.bot.server_configs[guild.id]
        result = dict()
        for k in ('hs_bravery_role', 'hs_brilliance_role', 'hs_balance_role', 'hs_none_role'):
            if config[k] is None:
                result[k] = None
            else:
                result[k] = guild.get_role(config[k])
        return result
    
    @commands.group(name="hypesquad")
    async def hs_main(self, ctx: MyContext):
        """Hypesquads-related commands"""
        if ctx.subcommand_passed is None:
            await ctx.send_help("hypesquad")

    @hs_main.command(name="reload")
    @commands.check(is_roles_manager)
    async def hs_reload(self, ctx: MyContext, *, user: discord.Member):
        """Reload Hypesquad roles for a member"""
        roles = await self.get_roles(ctx.guild)
        if not any(roles.values()):
            await ctx.send(await self.bot._(ctx.guild.id, 'hypesquad.no-role'))
            return
        try:
            edited = await self.edit_roles(user, roles)
        except discord.Forbidden:
            await ctx.send(await self.bot._(ctx.guild.id, 'hypesquad.forbidden'))
            return
        if edited:
            await ctx.send(await self.bot._(ctx.guild.id, 'hypesquad.edited', user=user))
        else:
            await ctx.send(await self.bot._(ctx.guild.id, 'hypesquad.not-edited', user=user))

    @hs_main.command()
    async def test(self, ctx):
        return 3/0

def setup(bot):
    bot.add_cog(Hypesquad(bot))