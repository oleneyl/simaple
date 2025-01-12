from typing import TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.keydown_trait as keydown_trait
import simaple.simulate.component.trait.simple_attack as simple_attack
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Keydown, LastingStack
from simaple.simulate.component.util import is_rejected
from simaple.simulate.component.view import Running
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class FinalCutState(TypedDict):
    cooldown: Cooldown
    dynamics: Dynamics


class FinalCutComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float
    sudden_raid_cooltime_reduce: float


class FinalCutComponent(Component):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    sudden_raid_cooltime_reduce: float

    def get_default_state(self) -> FinalCutState:
        return {
            "cooldown": Cooldown(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> FinalCutComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "sudden_raid_cooltime_reduce": self.sudden_raid_cooltime_reduce,
        }

    @reducer_method
    def elapse(self, time: float, state: FinalCutState):
        return simple_attack.elapse(state, {"time": time})

    @reducer_method
    def use(self, _: None, state: FinalCutState):
        return simple_attack.use_cooldown_attack(
            state,
            {},
            **self.get_props(),
        )

    @reducer_method
    def sudden_raid(self, _: None, state: FinalCutState):
        cooldown = state["cooldown"]
        cooldown.reduce_by_rate(self.sudden_raid_cooltime_reduce * 0.01)
        state["cooldown"] = cooldown

        return state, []

    @view_method
    def validity(self, state: FinalCutState):
        return cooldown_trait.validity_view(state, **self.get_props())


class BladeStormState(TypedDict):
    cooldown: Cooldown
    keydown: Keydown
    dynamics: Dynamics


class BladeStormComponentProps(TypedDict):
    id: str
    name: str
    maximum_keydown_time: float
    damage: float
    hit: float
    delay: float
    cooldown_duration: float
    keydown_prepare_delay: float
    keydown_end_delay: float
    prepare_damage: float
    prepare_hit: float


class BladeStormComponent(Component):
    maximum_keydown_time: float

    damage: float
    hit: float
    delay: float
    cooldown_duration: float

    keydown_prepare_delay: float
    keydown_end_delay: float

    prepare_damage: float
    prepare_hit: float

    def get_default_state(self) -> BladeStormState:
        return {
            "cooldown": Cooldown(time_left=0),
            "keydown": Keydown(interval=self.delay),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> BladeStormComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "maximum_keydown_time": self.maximum_keydown_time,
            "damage": self.damage,
            "hit": self.hit,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
            "keydown_prepare_delay": self.keydown_prepare_delay,
            "keydown_end_delay": self.keydown_end_delay,
            "prepare_damage": self.prepare_damage,
            "prepare_hit": self.prepare_hit,
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: BladeStormState,
    ):
        state, events = keydown_trait.use_keydown(
            state,
            {},
            **self.get_props(),
        )

        if not is_rejected(events):
            events.append(EmptyEvent.dealt(self.prepare_damage, self.prepare_hit))

        return state, events

    @reducer_method
    def elapse(self, time: float, state: BladeStormState):
        return keydown_trait.elapse_keydown(
            state,
            {"time": time},
            damage=self.damage,
            hit=self.hit,
            finish_damage=0,
            finish_hit=0,
            finish_delay=self.keydown_end_delay,
        )

    @reducer_method
    def stop(self, _, state: BladeStormState):
        return keydown_trait.stop_keydown(
            state,
            {},
            finish_damage=0,
            finish_hit=0,
            finish_delay=self.keydown_end_delay,
        )

    @view_method
    def validity(self, state: BladeStormState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def keydown(self, state: BladeStormState):
        return keydown_trait.keydown_view(state, **self.get_props())


class KarmaBladeTriggerState(TypedDict):
    cooldown: Cooldown
    lasting_stack: LastingStack
    dynamics: Dynamics


class KarmaBladeTriggerComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit: float
    delay: float
    triggable_count: int
    lasting_duration: float
    cooldown_duration: float

    finish_damage: float
    finish_hit: float


class KarmaBladeTriggerComponent(Component):
    name: str
    damage: float
    hit: float
    delay: float
    triggable_count: int
    lasting_duration: float
    cooldown_duration: float

    finish_damage: float
    finish_hit: float

    def get_default_state(self) -> KarmaBladeTriggerState:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting_stack": LastingStack(
                stack=0,
                maximum_stack=self.triggable_count,
                duration=self.lasting_duration,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> KarmaBladeTriggerComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "delay": self.delay,
            "triggable_count": self.triggable_count,
            "lasting_duration": self.lasting_duration,
            "cooldown_duration": self.cooldown_duration,
            "finish_damage": self.finish_damage,
            "finish_hit": self.finish_hit,
        }

    @reducer_method
    def elapse(self, time: float, state: KarmaBladeTriggerState):
        cooldown, lasting_stack = state["cooldown"], state["lasting_stack"]
        cooldown.elapse(time)

        was_running = lasting_stack.enabled()
        lasting_stack.elapse(time)

        if was_running and not lasting_stack.enabled():
            lasting_stack.reset()

            state["cooldown"], state["lasting_stack"] = cooldown, lasting_stack

            return (
                state,
                [EmptyEvent.dealt(self.finish_damage, self.finish_hit)],
            )

        state["cooldown"], state["lasting_stack"] = cooldown, lasting_stack

        return state, []

    @reducer_method
    def use(self, _: None, state: KarmaBladeTriggerState):
        lasting_stack = state["lasting_stack"]
        lasting_stack.reset()
        lasting_stack.increase(self.triggable_count)
        state["lasting_stack"] = lasting_stack

        return state, []

    @reducer_method
    def trigger(self, _: None, state: KarmaBladeTriggerState):
        if not state["lasting_stack"].enabled():
            return state, []
        if not state["cooldown"].available:
            return state, []

        cooldown, lasting_stack = state["cooldown"], state["lasting_stack"]

        cooldown.set_time_left(self.cooldown_duration)
        lasting_stack.decrease(1)

        if lasting_stack.stack <= 0:
            lasting_stack.reset()
            return (
                state,
                [
                    EmptyEvent.dealt(self.damage, self.hit),
                    EmptyEvent.dealt(self.finish_damage, self.finish_hit),
                ],
            )

        return (
            state,
            [EmptyEvent.dealt(self.damage, self.hit)],
        )

    @view_method
    def validity(self, state: KarmaBladeTriggerState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: KarmaBladeTriggerState):
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["lasting_stack"].time_left,
            lasting_duration=self.lasting_duration,
            stack=state["lasting_stack"].stack,
        )
