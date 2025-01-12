from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.lasting_trait as lasting_trait
from simaple.core.base import Stat
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class BuffSkillState(TypedDict):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class BuffSkillComponentProps(TypedDict):
    id: str
    name: str
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    apply_buff_duration: bool


class BuffSkillComponent(Component):
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    apply_buff_duration: bool = True
    # TODO: use apply_cooldown_reduction argument to apply cooltime reduction

    def get_default_state(self) -> BuffSkillState:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> BuffSkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "stat": self.stat,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "lasting_duration": self.lasting_duration,
            "apply_buff_duration": self.apply_buff_duration,
        }

    @reducer_method
    def use(self, _: None, state: BuffSkillState):
        return lasting_trait.start_lasting_with_cooldown(
            state,
            {},
            **self.get_props(),
        )

    @reducer_method
    def elapse(self, time: float, state: BuffSkillState):
        return lasting_trait.elapse_lasting_with_cooldown(
            state, {"time": time}, **self.get_props()
        )

    @view_method
    def validity(self, state: BuffSkillState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def buff(self, state: BuffSkillState) -> Optional[Stat]:
        if state["lasting"].enabled():
            return self.stat

        return None

    @view_method
    def running(self, state: BuffSkillState) -> Running:
        return lasting_trait.running_view(state, **self.get_props())
