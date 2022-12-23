import pytest

from simaple.core import Stat
from simaple.simulate.component.specific.adele import AdeleBlossomComponent, OrderState
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="blossom")
def fixture_blossom(
    adele_store,
):
    component = AdeleBlossomComponent(
        name="test-blossom",
        delay=420,
        damage=650,
        hit_per_sword=8,
        cooldown=20_000,
        exceeded_stat=Stat(final_damage_multiplier=-25),
    )
    return component.compile(adele_store)


def test_blossom_order_1pair(adele_store, blossom):
    adele_store.set_state(
        ".오더.order_state",
        OrderState(interval=1020, running_swords=[(0, 40000)]),
    )

    events = blossom.use(None)
    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    assert len(dealing_event) == 2


def test_blossom_order_3pair(adele_store, blossom):
    adele_store.set_state(
        ".오더.order_state",
        OrderState(interval=1020, running_swords=[(0, 40000), (0, 40000), (0, 40000)]),
    )

    events = blossom.use(None)
    dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

    assert len(dealing_event) == 6
