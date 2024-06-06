import time

import pytest
from loguru import logger

from simaple.core import JobType, Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.optimizer import LinkSkillTarget, StepwizeOptimizer
from simaple.system.link import LinkSkillset


@pytest.mark.parametrize(
    "maximum_cost, expected_reward_value",
    [
        (3, 21126700.36418906),
        (6, 24653420.52341694),
        (12, 29098017.779391848),
        (13, 29645888.4070373),
    ],
)
def test_optimizer(maximum_cost: int, expected_reward_value: float):
    optimization_target = LinkSkillTarget(
        Stat(
            INT=40000,
            LUK=5000,
            magic_attack=3000,
            critical_rate=80,
            critical_damage=100,
            damage_multiplier=300,
            ignored_defence=90,
            INT_static=10000,
        ),
        INTBasedDamageLogic(attack_range_constant=1.0, mastery=0.95),
        LinkSkillset.KMS(),
        preempted_jobs=[JobType.archmagefb],
    )
    optimizer = StepwizeOptimizer(optimization_target, maximum_cost, 1)
    output = optimizer.optimize()
    assert output.get_value() == pytest.approx(expected_reward_value)
