from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.skill import (
    CooldownState,
    IntervalState,
    SkillComponent,
)
from simaple.simulate.component.state import StackState
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    InvalidatableCooldownTrait,
    TickEmittingTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.util import is_rejected
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class EtherState(StackState):
    def get_sword_count(self) -> int:
        return min(self.stack // 100, 3) * 2


class AdeleEtherComponent(Component):
    maximum_stack: int
    tick_interval: float
    stack_per_tick: int
    stack_per_trigger: int

    listening_actions: dict[str, str] = {"디바이드.use": "trigger"}

    def get_default_state(self):
        return {
            "ether_state": EtherState(maximum_stack=self.maximum_stack),
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
        }

    @reducer_method
    def elapse(
        self, time: float, ether_state: EtherState, interval_state: IntervalState
    ):
        ether_state = ether_state.copy()
        interval_state = interval_state.copy()

        lapse_count = interval_state.elapse(time)
        ether_state.increase(lapse_count * self.stack_per_tick)

        return (interval_state), [self.event_provider.elapsed(time)]

    @reducer_method
    def trigger(self, _: None, ether_state: EtherState):
        ether_state = ether_state.copy()

        ether_state.increase(self.stack_per_trigger)

        return (ether_state), []


class AdeleResonanceComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait
):
    name: str
    damage: float
    hit: float
    delay: float

    ether_gain: int

    binds: dict[str, str] = {"ether_state": ".에테르.ether_state"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        dynamics: Dynamics,
        ether_state: EtherState,
    ):
        ether_state = ether_state.copy()
        ether_state.increase(self.ether_gain)

        (states, event) = self.use_simple_attack(cooldown_state, dynamics)

        return (*states, ether_state), event

    @reducer_method
    def elapse(self, time: float, cooldown_state: CooldownState):
        return self.elapse_simple_attack(time, cooldown_state)

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_invalidatable_cooldown_trait(cooldown_state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit


class AdeleWonderComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait
):
    name: str
    damage: float
    hit: float
    cooldown: float
    delay: float

    listening_actions: dict[str, str] = {"디바이드.use": "trigger"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, cooldown_state: CooldownState):
        return self.elapse_simple_attack(time, cooldown_state)

    @reducer_method
    def trigger(self, _: None, cooldown_state: CooldownState, dynamics: Dynamics):
        return self.use_simple_attack(cooldown_state, dynamics)

    @view_method
    def validity(self, cooldown_state):
        return self.validity_in_invalidatable_cooldown_trait(cooldown_state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit


class AdeleCreationComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait
):
    name: str
    damage: float
    hit: float
    cooldown: float
    delay: float

    listening_actions: dict[str, str] = {"디바이드.use": "trigger"}
    binds: dict[str, str] = {"ether_state": ".에테르.ether_state"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, cooldown_state: CooldownState):
        return self.elapse_simple_attack(time, cooldown_state)

    @reducer_method
    def trigger(
        self,
        _: None,
        cooldown_state: CooldownState,
        ether_state: EtherState,
        dynamics: Dynamics,
    ):
        return self.use_multiple_damage(
            cooldown_state, dynamics, ether_state.get_sword_count()
        )

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_invalidatable_cooldown_trait(cooldown_state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit


class AdeleOrderComponent(SkillComponent, TickEmittingTrait, CooldownValidityTrait):
    tick_interval: float
    tick_damage: float
    tick_hit: float
    duration: float
    ether_consume: int

    binds: dict[str, str] = {"ether_state": ".에테르.ether_state"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
            "stack_state": StackState(maximum_stack=6),
        }

    @reducer_method
    def elapse(
        self,
        _: float,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        stack_state: StackState,
        dynamics: Dynamics,
    ):
        return self.use_tick_emitting_trait(
            cooldown_state, interval_state, dynamics, hit_multiplier=stack_state.stack
        )

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        dynamics: Dynamics,
        stack_state: StackState,
        ether_state: EtherState,
    ):
        stack_state = stack_state.copy()
        ether_state = ether_state.copy()

        if ether_state.stack < self.ether_consume:
            return (
                cooldown_state,
                interval_state,
                dynamics,
                stack_state,
                ether_state,
            ), [self.event_provider.rejected()]

        states, events = self.use_tick_emitting_trait(
            cooldown_state, interval_state, dynamics
        )
        if not is_rejected(events):
            ether_state.decrease(self.ether_consume)
            stack_state.increase(2)

        return (*states, stack_state), events

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_cooldown_trait(cooldown_state)

    @view_method
    def running(
        self, interval_state: IntervalState, stack_state: StackState
    ) -> Running:
        return Running(
            name=self.name,
            time_left=interval_state.interval_time_left,
            duration=self._get_duration(),
            stack=stack_state.stack,
        )

    def _get_duration(self) -> float:
        return self.duration

    def _get_tick_damage_hit(self) -> tuple[float, float]:
        return self.tick_damage, self.tick_hit


class AdeleGatheringComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait
):
    binds: dict[str, str] = {"ether_state": ".에테르.ether_state"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        ether_state: EtherState,
        dynamics: Dynamics,
    ):
        return self.use_multiple_damage(
            cooldown_state, dynamics, ether_state.get_sword_count()
        )

    @reducer_method
    def elapse(self, time: float, cooldown_state: CooldownState):
        return self.elapse_simple_attack(time, cooldown_state)

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_invalidatable_cooldown_trait(cooldown_state)


class AdeleBlossomComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait
):
    binds: dict[str, str] = {"ether_state": ".에테르.ether_state"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        ether_state: EtherState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()
        sword_count = ether_state.get_sword_count()

        if not cooldown_state.available:
            return (cooldown_state, dynamics), self.event_provider.rejected()

        if sword_count <= 0:
            return (cooldown_state, dynamics), self.event_provider.rejected()

        cooldown_state.set_time_left(
            dynamics.stat.calculate_cooldown(self._get_cooldown())
        )

        damage, hit = self._get_simple_damage_hit()
        delay = self._get_delay()

        return (cooldown_state, dynamics), [self.event_provider.dealt(damage, hit)] + [
            self.event_provider.dealt(damage, hit)
            for _ in range(ether_state.get_sword_count() - 1)
        ] + [self.event_provider.delayed(delay)]

    @reducer_method
    def elapse(self, time: float, cooldown_state: CooldownState):
        return self.elapse_simple_attack(time, cooldown_state)

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_invalidatable_cooldown_trait(cooldown_state)


# class AdeleRuinComponent(
#     SkillComponent,
#     CooldownTrait,
#     DurationTrait,
#     EventProviderTrait,
#     DelayTrait,
#     CooldownValidityTrait,
# ):
#     tick_interval_first: float
#     tick_damage_first: float
#     tick_hit_first: float
#     duration_first: float

#     tick_interval_second: float
#     tick_damage_second: float
#     tick_hit_second: float
#     duration_second: float

#     def get_default_state(self):
#         return {
#             "cooldown_state": CooldownState(time_left=0),
#             "interval_state": IntervalState(
#                 interval=self.tick_interval_first, time_left=0
#             ),
#         }

#     @reducer_method
#     def elapse(
#         self,
#         time: float,
#         cooldown_state: CooldownState,
#         interval_state: IntervalState,
#     ):
#         cooldown_state = cooldown_state.copy()
#         interval_state = interval_state.copy()

#         cooldown_state.elapse(time)
#         lapse_count = interval_state.elapse(time)

#         tick_damage, tick_hit = self._get_tick_damage_hit(interval_state)

#         return (cooldown_state, interval_state), [self.event_provider.elapsed(time)] + [
#             self.event_provider.dealt(tick_damage, tick_hit) for _ in range(lapse_count)
#         ]

#     @reducer_method
#     def use(
#         self,
#         _: None,
#         cooldown_state: CooldownState,
#         interval_state: IntervalState,
#         dynamics: Dynamics,
#     ):
#         cooldown_state = cooldown_state.copy()
#         interval_state = interval_state.copy()

#         if not cooldown_state.available:
#             return (
#                 cooldown_state,
#                 interval_state,
#                 dynamics,
#             ), [self.event_provider.rejected()]

#         delay = self._get_delay()

#         cooldown_state.set_time_left(
#             dynamics.stat.calculate_cooldown(self._get_cooldown())
#         )
#         interval_state.set_time_left(self._get_duration())

#         return (cooldown_state, interval_state, dynamics), [
#             self.event_provider.delayed(delay),
#         ]

#     @view_method
#     def validity(self, cooldown_state: CooldownState):
#         return self.validity_in_cooldown_trait(cooldown_state)

#     @view_method
#     def running(
#         self, interval_state: IntervalState, stack_state: StackState
#     ) -> Running:
#         return Running(
#             name=self.name,
#             time_left=interval_state.interval_time_left,
#             duration=self._get_duration(),
#             stack=stack_state.stack,
#         )

#     def _get_duration(self) -> float:
#         return self.duration_first + self.duration_second

#     def _get_tick_damage_hit(
#         self, interval_state: IntervalState
#     ) -> tuple[float, float]:
#         if interval_state.interval_time_left < self.duration_second:
#             return self.tick_damage_second, self.tick_hit_second
#         else:
#             return self.tick_damage_first, self.tick_hit_first
