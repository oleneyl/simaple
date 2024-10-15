from typing import TypedDict, TypeVar

from simaple.simulate.component.entity import Cooldown
from simaple.simulate.core import Event
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


class CoolDownState(TypedDict):
    cooldown: Cooldown
    dynamics: Dynamics


CoolDownStateT = TypeVar("CoolDownStateT", bound=CoolDownState)


class UseSimpleAttackPayload(TypedDict):
    cooldown_duration: float
    damage: float
    hit: float
    delay: float


def use_cooldown_attack(
    state: CoolDownStateT,
    cooldown_duration: float,
    damage: float,
    hit: float,
    delay: float,
) -> tuple[CoolDownStateT, list[Event]]:
    if not state["cooldown"].available:
        return state, [EmptyEvent.rejected()]

    cooldown = state["cooldown"].model_copy()
    cooldown.set_time_left(state["dynamics"].stat.calculate_cooldown(cooldown_duration))
    state["cooldown"] = cooldown

    return state, [
        EmptyEvent.dealt(damage, hit),
        EmptyEvent.delayed(delay),
    ]


def elapse(state: CoolDownStateT, time: float) -> tuple[CoolDownStateT, list[Event]]:
    cooldown = state["cooldown"].model_copy()
    cooldown.elapse(time)
    state["cooldown"] = cooldown

    return state, [EmptyEvent.elapsed(time)]


def get_dot_event(name: str, damage: float, lasting_duration: float) -> Event:
    return {
        "name": name,
        "payload": {
            "damage": damage,
            "lasting_time": lasting_duration,
            "name": name,
        },
        "tag": Tag.MOB,
        "method": "add_dot",
        "handler": None,
    }
