# pylint: disable=W0621
import pytest

from simaple.simulate.component.common.scheduled_damage_skill import (
    ScheduledDamageSkillComponent,
    ScheduledDamageSkillState,
)
from simaple.simulate.global_property import Dynamics


@pytest.fixture
def scheduled_damage_skill():
    component = ScheduledDamageSkillComponent(
        id="test",
        name="scheduled-damage-component",
        damage_schedule=[
            {"damage": 100, "hit": 1, "time": 0},
            {"damage": 200, "hit": 2, "time": 1000},
            {"damage": 300, "hit": 3, "time": 2000},
        ],
        delay=30,
        cooldown_duration=30_000,
    )
    return component


@pytest.fixture
def scheduled_damage_skill_state(
    scheduled_damage_skill: ScheduledDamageSkillComponent,
    dynamics: Dynamics,
):
    return ScheduledDamageSkillState.model_validate(
        {
            **scheduled_damage_skill.get_default_state(),
            "dynamics": dynamics,
        }
    )


def test_scheduled_damage_skill_use(
    scheduled_damage_skill: ScheduledDamageSkillComponent,
    scheduled_damage_skill_state: ScheduledDamageSkillState,
):
    # given
    _, events = scheduled_damage_skill.use(None, scheduled_damage_skill_state)

    # then
    assert events[0]["payload"] == {"damage": 100, "hit": 1.0, "modifier": None}


def test_scheduled_damage_skill_total(
    scheduled_damage_skill: ScheduledDamageSkillComponent,
    scheduled_damage_skill_state: ScheduledDamageSkillState,
):
    # given
    state, _ = scheduled_damage_skill.use(None, scheduled_damage_skill_state)
    state, elapse_events_0 = scheduled_damage_skill.elapse(500, state)
    state, elapse_events_1 = scheduled_damage_skill.elapse(500, state)
    state, elapse_events_2 = scheduled_damage_skill.elapse(2000, state)

    # then
    assert len(elapse_events_0) == 1
    assert elapse_events_1[0]["payload"] == {
        "damage": 200,
        "hit": 2.0,
        "modifier": None,
    }
    assert elapse_events_2[0]["payload"] == {
        "damage": 300,
        "hit": 3.0,
        "modifier": None,
    }
