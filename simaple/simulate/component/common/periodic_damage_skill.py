from typing import Optional

from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Periodic
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    PeriodicElapseTrait,
    UsePeriodicDamageTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class PeriodicDamageSkillState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class PeriodicDamageSkillComponent(
    SkillComponent, UsePeriodicDamageTrait, PeriodicElapseTrait, CooldownValidityTrait
):
    name: str
    delay: float

    cooldown_duration: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    finish_damage: Optional[float] = None
    finish_hit: Optional[float] = None

    lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
        }

    @reducer_method
    def elapse(self, time: float, state: PeriodicDamageSkillState):
        was_running = state.periodic.enabled()
        state, events = self.elapse_periodic_damage_trait(time, state)
        is_running = state.periodic.enabled()

        if (
            self.finish_hit is not None
            and self.finish_damage is not None
            and was_running
            and not is_running
        ):
            events.append(
                self.event_provider.dealt(self.finish_damage, self.finish_hit)
            )

        return state, events

    @reducer_method
    def use(self, _: None, state: PeriodicDamageSkillState):
        return self.use_periodic_damage_trait(state)

    @view_method
    def validity(self, state: PeriodicDamageSkillState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: PeriodicDamageSkillState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: PeriodicDamageSkillState) -> float:
        return self.lasting_duration

    def _get_periodic_damage_hit(
        self, state: PeriodicDamageSkillState
    ) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit
