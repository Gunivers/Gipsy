from typing import Union
from discord.ext import commands

class ActionType(commands.Converter):
    types = ['grant', 'revoke']

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
            return ActionType(argument)
        raise commands.errors.BadArgument("Unknown dependency action type")