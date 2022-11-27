import json

from simaple.core import Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.job.builtin.interpreter import get_static_propery
from simaple.metric.metric import RegressionMetric


def test_metric():
    static_property = get_static_propery(
        "archmagefb",
        combat_orders_level=1,
        passive_skill_level=0,
        character_level=260,
    )

    metric = RegressionMetric(
        static_property,
        INTBasedDamageLogic(attack_range_constant=1.2, mastery=0.95),
    )
    reference_list = [
        "./tests/metric/refs/Epic.json",
        "./tests/metric/refs/EpicUnique.json",
        "./tests/metric/refs/Unique.json",
        "./tests/metric/refs/Legendary18.json",
        "./tests/metric/refs/LegendaryHalf.json",
        "./tests/metric/refs/Legendary.json",
    ]

    for reference_file in reference_list:
        with open(reference_file, encoding="utf-8") as f:
            stat = Stat.parse_obj(json.load(f))

        metric.add_reference(stat)

    with open(reference_list[-1], encoding="utf-8") as f:
        target = Stat.parse_obj(json.load(f))

    result = metric.evaluate(target)
    print(result)
