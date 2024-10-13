from typing import TypedDict, TypeVar

from simaple.simulate.component.entity import Cooldown
from simaple.simulate.component.view import KeydownView, Running, Validity
from simaple.simulate.core import Event
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class _State(TypedDict):
    cooldown: Cooldown


StateT = TypeVar("StateT", bound=_State)


def reset_cooldown(state: StateT) -> tuple[StateT, list[Event]]:
    cooldown = state["cooldown"].model_copy()
    cooldown.set_time_left(0)

    state["cooldown"] = cooldown

    return state, []


def validity_view(
    state: _State, id: str, name: str, cooldown_duration: float
) -> Validity:
    """
    Renewal for `validity_in_invalidatable_cooldown_trait`.
    """
    return Validity(
        id=id,
        name=name,
        time_left=state["cooldown"].minimum_time_to_available(),
        valid=state["cooldown"].available,
        cooldown_duration=cooldown_duration,
    )
