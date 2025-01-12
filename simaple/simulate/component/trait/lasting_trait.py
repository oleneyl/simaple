from typing import TypedDict, TypeVar

from typing_extensions import Unpack

from simaple.simulate.component.entity import Cooldown, Lasting
from simaple.simulate.component.view import Running
from simaple.simulate.core import Event
from simaple.simulate.core.action import ElapseActionPayload, UseActionPayload
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class _State(TypedDict):
    cooldown: Cooldown
    dynamics: Dynamics
    lasting: Lasting


_StateT = TypeVar("_StateT", bound=_State)


class StartLastingWithCooldownProps(TypedDict):
    cooldown_duration: float
    lasting_duration: float
    delay: float
    apply_buff_duration: bool


def start_lasting_with_cooldown(
    state: _StateT,
    _payload: UseActionPayload,
    **props: Unpack[StartLastingWithCooldownProps],
) -> tuple[_StateT, list[Event]]:
    """
    New version for `use_buff_trait`
    """
    cooldown_duration, lasting_duration, delay, apply_buff_duration = (
        props["cooldown_duration"],
        props["lasting_duration"],
        props["delay"],
        props["apply_buff_duration"],
    )

    cooldown = state["cooldown"].model_copy()
    lasting = state["lasting"].model_copy()

    if not cooldown.available:
        return state, [EmptyEvent.rejected()]

    cooldown.set_time_left(state["dynamics"].stat.calculate_cooldown(cooldown_duration))

    lasting.set_time_left(
        state["dynamics"].stat.calculate_buff_duration(lasting_duration)
        if apply_buff_duration
        else lasting_duration
    )

    state["cooldown"] = cooldown
    state["lasting"] = lasting

    return state, [EmptyEvent.delayed(delay)]


class ElapseLastingWithCooldownProps(TypedDict):
    ...


def elapse_lasting_with_cooldown(
    state: _StateT,
    payload: ElapseActionPayload,
    **_props: Unpack[ElapseLastingWithCooldownProps],
) -> tuple[_StateT, list[Event]]:
    """
    New version for `elapse_buff_trait`
    """
    time = payload["time"]

    cooldown = state["cooldown"].model_copy()
    lasting = state["lasting"].model_copy()

    cooldown.elapse(time)
    lasting.elapse(time)

    state["cooldown"] = cooldown
    state["lasting"] = lasting

    return state, []


class _StateWithoutCooldown(TypedDict):
    lasting: Lasting
    dynamics: Dynamics


class RunningViewProps(TypedDict):
    id: str
    name: str


def running_view(
    state: _StateWithoutCooldown, **props: Unpack[RunningViewProps]
) -> Running:
    """
    New version for `running_in_buff_trait`
    """
    return Running(
        id=props["id"],
        name=props["name"],
        time_left=state["lasting"].time_left,
        lasting_duration=state["lasting"].assigned_duration,
    )
