import json

import pydantic
import yaml

from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.plan_metadata import PlanMetadata
from simaple.container.simulation import OperationEngine
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.simulate.report.base import DamageLog
from simaple.simulate.report.dpm import DamageCalculator
from simaple.simulate.report.feature import MaximumDealingIntervalFeature
from simaple.wasm.base import (
    pyodide_reveal_base_model,
    pyodide_reveal_base_model_list,
    return_js_object_from_pydantic_list,
    return_js_object_from_pydantic_object,
    wrap_response_by_handling_exception,
)
from simaple.wasm.examples import get_example_plan
from simaple.wasm.models.simulation import (
    DamageRecord,
    OperationLogResponse,
    PlayLogResponse,
    _Report,
)


def _extract_engine_history_as_response(
    engine: OperationEngine,
    damage_calculator: DamageCalculator,
) -> list[OperationLogResponse]:
    responses: list[OperationLogResponse] = []

    for idx, operation_log in enumerate(engine.operation_logs()):
        playlog_responses = []

        for playlog in operation_log.playlogs:
            viewer = engine.get_viewer(playlog)
            entry = engine.get_simulation_entry(playlog)
            damage_logs: list[DamageLog] = entry.damage_logs

            damages = [
                DamageRecord(
                    name=damage_log.name,
                    damage=damage_calculator.get_damage(damage_log),
                    hit=damage_log.hit,
                )
                for damage_log in damage_logs
            ]
            damage = damage_calculator.calculate_damage(entry)

            playlog_responses.append(
                PlayLogResponse(
                    events=playlog.events,
                    validity_view={v.name: v for v in viewer("validity")},
                    running_view={v.name: v for v in viewer("running")},
                    buff_view=viewer("buff"),
                    clock=playlog.clock,
                    report=_Report(time_series=[entry]),
                    delay=playlog.get_delay_left(),
                    action=playlog.action,
                    checkpoint=playlog.checkpoint,
                    total_damage=damage,
                    damage_records=damages,
                )
            )

        responses.append(
            OperationLogResponse(
                index=idx,
                logs=playlog_responses,
                hash=operation_log.hash,
                previous_hash=operation_log.previous_hash,
                command=operation_log.command,
                description=operation_log.description,
            )
        )

    return responses


@wrap_response_by_handling_exception
@return_js_object_from_pydantic_list
def runPlan(
    plan: str,
) -> list[OperationLogResponse]:
    """
    plan을 받아서 environment 필드를 참조해 계산을 수행합니다. environment 필드가 비어있다면, 오류를 발생시킵니다.
    """
    plan_metadata_dict, commands = parse_simaple_runtime(plan.strip())

    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)
    if plan_metadata.environment is None or plan_metadata.environment == {}:
        raise ValueError("Environment field is not provided")

    simulation_container = plan_metadata.load_container()
    engine = simulation_container.operation_engine()

    for command in commands:
        engine.exec(command)

    return _extract_engine_history_as_response(
        engine, simulation_container.damage_calculator()
    )


def hasEnvironment(plan: str) -> bool:
    """plan이 environment 필드를 가지고 있는지 확인합니다."""
    plan_metadata_dict, _ = parse_simaple_runtime(plan.strip())
    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)

    return plan_metadata.environment is not None and plan_metadata.environment != {}


def provideEnvironmentAugmentedPlan(plan: str) -> str:
    """plan을 받아서 environment 필드를 새로 쓴 plan을 반환합니다."""
    metadata_dict, _ = parse_simaple_runtime(plan.strip())
    metadata = PlanMetadata.model_validate(metadata_dict)

    if metadata.provider is None:
        raise ValueError("Character provider is not provided")

    simulation_environment = metadata.provider.get_simulation_environment()
    metadata.environment = simulation_environment
    _, original_operations = (
        plan.split("\n---")[0],
        "\n---".join(plan.split("\n---")[1:]),
    )

    augmented_metadata = yaml.safe_dump(
        json.loads(metadata.model_dump_json()), indent=2
    )
    return f"---\n{augmented_metadata}\n---\n{original_operations}"


class MaximumDealingIntervalResult(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    damage: float
    start: int
    end: int


@return_js_object_from_pydantic_object
def computeMaximumDealingInterval(
    plan: str,
    interval: int,
) -> MaximumDealingIntervalResult:
    """
    interval as ms.
    """
    plan_metadata_dict, commands = parse_simaple_runtime(plan.strip())

    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)
    if plan_metadata.environment is None or plan_metadata.environment == {}:
        raise ValueError("Environment field is not provided")

    simulation_container = plan_metadata.load_container()
    engine = simulation_container.operation_engine()

    for command in commands:
        engine.exec(command)

    report = list(engine.simulation_entries())

    damage, _start, _end = MaximumDealingIntervalFeature(
        interval=interval
    ).find_maximum_dealing_interval(report, simulation_container.damage_calculator())
    return MaximumDealingIntervalResult(damage=damage, start=_start, end=_end)


def getInitialPlanFromBaseline(
    environment_provider: BaselineEnvironmentProvider,
) -> str:
    """
    baseline environment provider를 받아서 example plan을 생성합니다.
    """
    environment_provider = pyodide_reveal_base_model(
        environment_provider, BaselineEnvironmentProvider
    )
    base_plan = get_example_plan(environment_provider.jobtype)
    metadata_dict, _ = parse_simaple_runtime(base_plan.strip())

    metadata_dict["provider"] = {
        "name": environment_provider.get_name(),
        "data": environment_provider.model_dump(),
    }
    metadata = PlanMetadata.model_validate(metadata_dict)

    _, original_operations = (
        base_plan.split("\n---")[0],
        "\n---".join(base_plan.split("\n---")[1:]),
    )

    augmented_metadata = yaml.safe_dump(
        json.loads(metadata.model_dump_json()), indent=2
    )
    return f"---\n{augmented_metadata}\n---\n{original_operations}"


@wrap_response_by_handling_exception
@return_js_object_from_pydantic_list
def runPlanWithHint(
    previous_plan: str, previous_history: list[OperationLogResponse], plan: str
) -> list[OperationLogResponse]:
    previous_history = pyodide_reveal_base_model_list(
        previous_history, OperationLogResponse
    )
    previous_plan_metadata_dict, previous_commands = parse_simaple_runtime(
        previous_plan.strip()
    )
    plan_metadata_dict, commands = parse_simaple_runtime(plan.strip())
    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)

    simulation_container = plan_metadata.load_container()

    engine = simulation_container.operation_engine()

    if plan_metadata_dict != previous_plan_metadata_dict:
        for command in commands:
            engine.exec(command)

        return _extract_engine_history_as_response(
            engine, simulation_container.damage_calculator()
        )

    # Since first operation in history is always "init", we skip this for retrieval;
    history_for_matching = previous_history[1:]

    cache_count: int = 0

    for idx, command in enumerate(commands):
        if len(previous_commands) <= idx or len(history_for_matching) <= idx:
            break

        previous_command = previous_commands[idx]
        previous_operation_log = history_for_matching[idx]
        if previous_command != previous_operation_log.command:
            break

        if command == previous_command:
            cache_count += 1
            continue
        break

    engine.reload(
        [
            operation_log_response.restore_operation_log()
            for operation_log_response in previous_history[: cache_count + 1]
        ]
    )

    for command in commands[cache_count:]:
        engine.exec(command)

    new_operation_logs = _extract_engine_history_as_response(
        engine, simulation_container.damage_calculator()
    )

    return new_operation_logs
