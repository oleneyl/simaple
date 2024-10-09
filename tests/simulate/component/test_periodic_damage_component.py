# pylint: disable=W0621
import pytest

from simaple.simulate.component.common.periodic_damage_skill import (
    PeriodicDamageSkillComponent,
    PeriodicDamageSkillState,
)
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


@pytest.fixture
def periodic_damage_component_with_finish():
    component = PeriodicDamageSkillComponent(
        id="test",
        name="periodic-damage-component",
        finish_damage=1000,
        finish_hit=1,
        delay=30,
        periodic_interval=120,
        periodic_damage=50,
        periodic_hit=3,
        lasting_duration=1_000,
        cooldown_duration=30_000,
    )
    return component


@pytest.fixture
def periodic_damage_component_without_finish():
    component = PeriodicDamageSkillComponent(
        id="test",
        name="periodic-damage-component",
        delay=30,
        periodic_interval=120,
        periodic_damage=50,
        periodic_hit=3,
        lasting_duration=1_000,
        cooldown_duration=30_000,
    )
    return component


@pytest.fixture
def periodic_damage_state(
    periodic_damage_component_with_finish: PeriodicDamageSkillComponent,
    dynamics: Dynamics,
):
    return PeriodicDamageSkillState.model_validate(
        {
            **periodic_damage_component_with_finish.get_default_state(),
            "dynamics": dynamics,
        }
    )


def test_periodic_damage_component_reject(
    periodic_damage_component_with_finish: PeriodicDamageSkillComponent,
    periodic_damage_state: PeriodicDamageSkillState,
):
    # given
    state, events = periodic_damage_component_with_finish.use(
        None, periodic_damage_state
    )
    state, events = periodic_damage_component_with_finish.use(None, state)

    # then
    assert events[0]["tag"] == Tag.REJECT


def test_periodic_damage_component_emit_after(
    periodic_damage_component_with_finish: PeriodicDamageSkillComponent,
    periodic_damage_state: PeriodicDamageSkillState,
):
    # given
    state, _ = periodic_damage_component_with_finish.use(None, periodic_damage_state)
    state, events = periodic_damage_component_with_finish.elapse(120 * 8, state)

    # then
    dealing_count = sum([e["tag"] == Tag.DAMAGE for e in events])
    assert dealing_count == 8


def test_periodic_damage_component_full_emit(
    periodic_damage_component_with_finish: PeriodicDamageSkillComponent,
    periodic_damage_state: PeriodicDamageSkillState,
):
    # given
    state, _ = periodic_damage_component_with_finish.use(None, periodic_damage_state)
    state, events = periodic_damage_component_with_finish.elapse(120 * 30, state)

    # then
    dealing_count = sum([e["tag"] == Tag.DAMAGE for e in events])
    assert dealing_count == 8 + 1
    assert events[-1]["payload"]["damage"] == 1000


def test_periodic_damage_component_without_finish_full_emit(
    periodic_damage_component_without_finish: PeriodicDamageSkillComponent,
    periodic_damage_state: PeriodicDamageSkillState,
):
    # given
    state, _ = periodic_damage_component_without_finish.use(None, periodic_damage_state)
    state, events = periodic_damage_component_without_finish.elapse(120 * 30, state)

    # then
    dealing_count = sum([e["tag"] == Tag.DAMAGE for e in events])
    assert dealing_count == 8
    assert events[-1]["payload"]["damage"] == 50
