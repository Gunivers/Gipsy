import ActionType
import TriggerType
from typing import List
from marshal import dumps

class Dependency:
    def __init__(self, action: ActionType, target_role: int, trigger: TriggerType, trigger_roles: List[int], guild: int):
        self.action = action
        self.target_role = target_role
        self.trigger = trigger
        self.trigger_roles = trigger_roles
        self.b_trigger_roles = dumps(trigger_roles)
        self.guild = guild
        self.id = None

    def to_str(self, useID: bool = True) -> str:
        triggers = ' '.join([f'<@&{r}>' for r in self.trigger_roles])
        target = f'<@&{self.target_role}>'
        ID = f"{self.id}. " if useID else ''
        return f"{ID}{self.action.name} {target} when {self.trigger.name.replace('-', ' ')} of {triggers}"

class ConflictingCyclicDependencyError(Exception):
    """Used when a loop is found when analyzing a role dependencies system"""
    pass