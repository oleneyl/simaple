from itertools import accumulate

from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Schedule
from simaple.simulate.component.feature import DamageSchedule
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import InvalidatableCooldownTrait
from simaple.simulate.global_property import Dynamics


class ScheduledDamageSkillState(ReducerState):
    cooldown: Cooldown
    schedule: Schedule
    dynamics: Dynamics


class ScheduledDamageSkillComponent(
    SkillComponent,
    InvalidatableCooldownTrait,
):
    """
    MultipleAttackSkillComponent
    This describes skill that act like:
    - various Initial damage x hit
    """

    name: str
    delay: float
    cooldown_duration: float
    damage_schedule: list[DamageSchedule]  # relative times

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "schedule": Schedule(
                scheduled_times=list(
                    accumulate([entry.time for entry in self.damage_schedule])
                )
            ),
        }

    @reducer_method
    def elapse(self, time: float, state: ScheduledDamageSkillState):
        state = state.deepcopy()
        state.cooldown.elapse(time)
        index_start, index_end = state.schedule.elapse(time)
        return state, [
            self.event_provider.dealt(entry.damage, entry.hit)
            for entry in self.damage_schedule[index_start:index_end]
        ] + [self.event_provider.elapsed(time)]

    @reducer_method
    def use(self, _: None, state: ScheduledDamageSkillState):
        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state = state.deepcopy()

        delay = self._get_delay()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )
        index_start, index_end = state.schedule.start()

        return state, [
            self.event_provider.dealt(entry.damage, entry.hit)
            for entry in self.damage_schedule[index_start:index_end]
        ] + [
            self.event_provider.delayed(delay),
        ]

    @view_method
    def validity(self, state: ScheduledDamageSkillState):
        return self.validity_in_invalidatable_cooldown_trait(state)
