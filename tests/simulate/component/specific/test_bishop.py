import pytest

from simaple.simulate.component.specific.bishop import (
    DivineMark,
    DivineMinion,
    DivineMinionState,
    HexaAngelRayComponent,
    HexaAngelRayState,
    HolyAdvent,
    HolyAdventState,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


@pytest.fixture
def holy_advent_component():
    component = HolyAdvent(
        id="test",
        name="periodic-damage-component",
        damage_and_hits=[{"damage": 100, "hit": 1}, {"damage": 200, "hit": 3}],
        delay=30,
        periodic_01={
            "interval": 120,
            "damage": 50,
            "hit": 3,
        },
        periodic_02={
            "interval": 120,
            "damage": 50,
            "hit": 3,
        },
        periodic_03={
            "interval": 60,
            "damage": 50,
            "hit": 3,
        },
        lasting_duration=1_000,
        cooldown_duration=30_000,
        synergy={},
    )
    return component


@pytest.fixture
def holy_advent_state(
    holy_advent_component: HolyAdvent,
    dynamics: Dynamics,
):
    return HolyAdventState.model_validate(
        {
            **holy_advent_component.get_default_state(),
            "dynamics": dynamics,
        }
    )


def test_holy_advent_component_emit_initial_damage(
    holy_advent_component: HolyAdvent,
    holy_advent_state: HolyAdventState,
):
    # given
    holy_advent_state, events = holy_advent_component.use(None, holy_advent_state)

    # then
    assert len(events) == 3

    assert events[0]["payload"] == {"damage": 100, "hit": 1.0, "modifier": None}
    assert events[1]["payload"] == {"damage": 200, "hit": 3.0, "modifier": None}
    assert events[2]["payload"] == {"time": 30.0}

    holy_advent_state, events = holy_advent_component.elapse(120.1, holy_advent_state)

    assert len(events) == 5  # 1+1+2 event + 1(elapse)

    holy_advent_state, events = holy_advent_component.elapse(240, holy_advent_state)

    assert len(events) == 9  # 2+2+4 event + 1(elapse)


@pytest.fixture
def hexa_angle_ray_component():
    component = HexaAngelRayComponent(
        id="test",
        name="periodic-damage-component",
        damage=10,
        hit=3,
        delay=30,
        punishing_damage=10,
        punishing_hit=5,
        stack_resolve_amount=12,
        cooldown_duration=0,
        synergy={},
    )
    return component


@pytest.fixture
def hexa_angle_ray_state(
    hexa_angle_ray_component: HexaAngelRayComponent,
    dynamics: Dynamics,
) -> HexaAngelRayState:
    return HexaAngelRayState.model_validate(
        {
            **hexa_angle_ray_component.get_default_state(),
            "dynamics": dynamics,
            "divine_mark": DivineMark(advantage=None),
        }
    )


def test_hexa_angle_ray(
    hexa_angle_ray_component: HexaAngelRayComponent,
    hexa_angle_ray_state: HexaAngelRayState,
):
    hexa_angle_ray_state, events = hexa_angle_ray_component.use(
        None, hexa_angle_ray_state
    )
    assert count_damage_skill(events) == 1

    for _ in range(10):
        hexa_angle_ray_state, events = hexa_angle_ray_component.stack(
            None, hexa_angle_ray_state
        )
        assert count_damage_skill(events) == 0

    hexa_angle_ray_state, events = hexa_angle_ray_component.stack(
        None, hexa_angle_ray_state
    )
    assert count_damage_skill(events) == 1

    hexa_angle_ray_state, events = hexa_angle_ray_component.stack(
        None, hexa_angle_ray_state
    )
    assert count_damage_skill(events) == 0

    for _ in range(7):
        hexa_angle_ray_state, events = hexa_angle_ray_component.stack(
            None, hexa_angle_ray_state
        )
        assert count_damage_skill(events) == 0


@pytest.fixture
def divine_minion_component():
    component = DivineMinion(
        id="test",
        name="periodic-damage-component",
        cooldown_duration=0,
        damage=10,
        hit=3,
        delay=30,
        periodic_interval=2000,
        periodic_damage=100,
        periodic_hit=100,
        lasting_duration=10000,
        mark_advantage={
            "damage": 10,
        },
    )
    return component


@pytest.fixture
def divine_minion_state(
    divine_minion_component: DivineMinion,
    dynamics: Dynamics,
) -> DivineMinionState:
    return DivineMinionState.model_validate(
        {
            **divine_minion_component.get_default_state(),
            "dynamics": dynamics,
            "divine_mark": DivineMark(),
        }
    )


def test_divine_mark(
    divine_minion_component: DivineMinion,
    divine_minion_state: DivineMinionState,
):
    divine_minion_state, events = divine_minion_component.use(None, divine_minion_state)
    divine_minion_state, events = divine_minion_component.elapse(
        300, divine_minion_state
    )
