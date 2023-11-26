import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType
from simaple.simulate.report.base import Report, ReportEventHandler

setting = SimulationSetting(
    tier="Legendary",
    jobtype=JobType.archmagefb,
    job_category=JobCategory.magician,
    level=270,
    passive_skill_level=0,
    combat_orders_level=1,
    v_skill_level=30,
    v_improvements_level=60,
)


def test_actor():
    container = SimulationContainer()
    container.config.from_dict(setting.model_dump())

    report = Report()
    engine = container.operation_engine()
    engine.add_callback(ReportEventHandler(report))

    policy = container.engine_configuration().get_default_policy()

    while engine.get_current_viewer()("clock") < 50_000:
        engine.exec_policy(policy, early_stop=50_000)

    print(
        f"{engine.get_current_viewer()('clock')} | {container.dpm_calculator().calculate_dpm(report):,} "
    )


if __name__ == "__main__":
    test_actor()
