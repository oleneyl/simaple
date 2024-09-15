from pathlib import Path

import pytest

import simaple.simulate.component.skill  # noqa: F401
from simaple.container.simulation import (
    SimulationContainer,
    SimulationSetting,
    BaselineSimulationConfig,
)
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType
from simaple.simulate.policy.parser import parse_dsl_to_operations


@pytest.fixture(name="dsl_list")
def fixture_dsl_list() -> list[str]:
    with open(Path(__file__).parent / "archmage_tc_runtime.txt", encoding="utf-8") as f:
        dsl_list = [line.strip() for line in f.readlines()]

    return dsl_list


@pytest.fixture(name="dsl_test_setting")
def fixture_dsl_test_setting() -> BaselineSimulationConfig:
    cache_dir = str(Path(__file__).parent)

    return BaselineSimulationConfig(
        tier="Legendary",
        jobtype=JobType.archmagetc,
        job_category=JobCategory.magician,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        cache_root_dir=cache_dir,
        artifact_level=40,
    )


def test_dsl(dsl_list: list[str], dsl_test_setting: BaselineSimulationConfig) -> None:
    container = SimulationContainer(
        SimulationSetting(
            v_skill_level=30,
            v_improvements_level=60,
        ),
        dsl_test_setting,
    )

    engine = container.operation_engine()

    for dsl in dsl_list:
        operations = parse_dsl_to_operations(dsl)
        for op in operations:
            engine.exec(op)

    dpm = container.dpm_calculator().calculate_dpm(list(engine.simulation_entries()))
    print(f"{engine.get_current_viewer()('clock')} | {dpm:,} ")
    assert 10438982168263.46 == pytest.approx(dpm)
