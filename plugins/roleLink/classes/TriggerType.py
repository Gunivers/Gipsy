from typing import Union
from discord.ext import commands

class TriggerType(commands.Converter):
    types = ['get-one', 'get-all', 'loose-one', 'loose-all']

    def __init__(self, trigger: Union[str, int] = None):
        if isinstance(trigger, str):
            self.type = self.types.index(trigger)
        elif isinstance(trigger, int):
            self.type = trigger
        else:
            return
        self.name = self.types[self.type]

    async def convert(self, ctx: commands.Context, argument: str):
        if argument in self.types:
            return TriggerType(argument)
        raise commands.errors.BadArgument("Unknown dependency trigger type")