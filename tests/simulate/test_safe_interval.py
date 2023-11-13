from simaple.core.base import ActionStat
from simaple.simulate.base import AddressedStore, ConcreteStore
from simaple.simulate.builder import ClientBuilder
from simaple.simulate.component.skill import AttackSkillComponent
from simaple.simulate.global_property import GlobalProperty


def test_scenario():
    store = AddressedStore(ConcreteStore())
    global_property = GlobalProperty(ActionStat())
    global_property.install_global_properties(store)

    attack_skill_1 = AttackSkillComponent(
        name="test-A", damage=300, hit=4, cooldown_duration=14.0, delay=0.0, id="test"
    )

    attack_skill_2 = AttackSkillComponent(
        name="test-B", damage=400, hit=6, cooldown_duration=10.0, delay=0.0, id="test"
    )

    client = (
        ClientBuilder(store)
        .add_component(attack_skill_1)
        .add_component(attack_skill_2)
        .build_client()
    )

    event = client.resolve(
        dict(
            name="test-B",
            method="elapse",
            payload=3.0,
        )
    )

    print(event)
