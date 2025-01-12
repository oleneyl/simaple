from typing import TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.feature import DamageAndHit
from simaple.simulate.global_property import Dynamics


class MultipleHitHexaSkillState(TypedDict):
    cooldown: Cooldown
    dynamics: Dynamics


class MultipleHitHexaSkillComponentProps(TypedDict):
    id: str
    name: str
    damage_and_hits: list[DamageAndHit]
    delay: float
    cooldown_duration: float


class MultipleHitHexaSkillComponent(
    Component,
):
    """
    MultipleHitHexaSkillComponent
    This describes skill that act like:
    - various Initial damage x hit
    """

    name: str
    damage_and_hits: list[DamageAndHit]
    delay: float

    cooldown_duration: float

    def get_default_state(self) -> MultipleHitHexaSkillState:
        return {
            "cooldown": Cooldown(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> MultipleHitHexaSkillComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage_and_hits": self.damage_and_hits,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
        }

    @reducer_method
    def elapse(self, time: float, state: MultipleHitHexaSkillState):
        return cooldown_trait.elapse_cooldown_only(state, {"time": time})

    @reducer_method
    def use(self, _: None, state: MultipleHitHexaSkillState):
        if not state["cooldown"].available:
            return state, [self.event_provider.rejected()]

        cooldown = state["cooldown"].model_copy()
        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        state["cooldown"] = cooldown

        return state, [
            self.event_provider.dealt(entry.damage, entry.hit)
            for entry in self.damage_and_hits
        ] + [
            self.event_provider.delayed(self.delay),
        ]

    @view_method
    def validity(self, state: MultipleHitHexaSkillState):
        return cooldown_trait.validity_view(state, **self.get_props())
