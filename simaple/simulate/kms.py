from typing import Any, TypedDict

import simaple.simulate.component.skill  # noqa: F401
import simaple.simulate.component.specific  # noqa: F401
from simaple.core.base import ActionStat, Stat
from simaple.data.jobs.builtin import get_kms_skill_loader
from simaple.data.jobs.patch import (
    HexaSkillImprovementPatch,
    SkillImprovementPatch,
    VSkillImprovementPatch,
    get_hyper_skill_patch,
)
from simaple.data.patch import SkillLevelPatch
from simaple.simulate.base import AddressedStore, ConcreteStore
from simaple.simulate.builder import EngineBuilder
from simaple.simulate.component.base import Component
from simaple.simulate.component.view import (
    BuffParentView,
    InformationParentView,
    KeydownParentView,
    RunningParentView,
    ValidityParentView,
)
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.timer import clock_view, timer_delay_dispatcher
from simaple.spec.patch import ArithmeticPatch


def bare_store(action_stat: ActionStat) -> AddressedStore:
    store = AddressedStore(ConcreteStore())
    GlobalProperty(action_stat).install_global_properties(store)
    return store


class BuilderRequiredExtraVariables(TypedDict):
    character_level: int
    character_stat: Stat
    weapon_attack_power: int
    weapon_pure_attack_power: int
    action_stat: ActionStat
    combat_orders_level: int
    passive_skill_level: int


def _as_reference_variables(
    extra_variables: BuilderRequiredExtraVariables,
) -> dict[str, Any]:
    reference = {
        "character_level": extra_variables["character_level"],
        "weapon_attack_power": extra_variables["weapon_attack_power"],
        "weapon_pure_attack_power": extra_variables["weapon_pure_attack_power"],
        "combat_orders_level": extra_variables["combat_orders_level"],
        "passive_skill_level": extra_variables["passive_skill_level"],
    }
    reference.update(
        {
            f"character_stat.{k}": v
            for k, v in extra_variables["character_stat"].model_dump().items()
        }
    )
    reference.update(
        {
            f"action_stat.{k}": v
            for k, v in extra_variables["action_stat"].model_dump().items()
        }
    )

    return reference


def _exclude_hexa_skill(
    components: list[Component],
    hexa_replacements: dict[str, str],
    skill_levels: dict[str, int],
) -> list[Component]:
    _component_names = [component.name for component in components]
    components_to_exclude = []

    for low_tier, high_tier in hexa_replacements.items():
        assert low_tier in _component_names, f"{low_tier} is not in {_component_names}"
        assert (
            high_tier in _component_names
        ), f"{high_tier} is not in {_component_names}"

        if skill_levels.get(high_tier, 0) > 0:
            components_to_exclude.append(low_tier)

    components = [
        component
        for component in components
        if component.name not in components_to_exclude
    ]
    return components


def get_builder(
    groups: list[str],
    skill_levels: dict[str, int],
    v_improvements: dict[str, int],
    hexa_improvements: dict[str, int],
    hexa_replacements: dict[str, str],
    injected_values: BuilderRequiredExtraVariables,
) -> EngineBuilder:
    loader = get_kms_skill_loader()

    reference_variables = _as_reference_variables(injected_values)

    skill_improvements = sum(
        [
            loader.load_all(
                query={"group": group, "kind": "SkillImprovement"},
                patches=[
                    SkillLevelPatch(
                        combat_orders_level=injected_values["combat_orders_level"],
                        passive_skill_level=injected_values["passive_skill_level"],
                        default_skill_levels=skill_levels,
                    ),
                    ArithmeticPatch(variables=reference_variables),
                ],
            )
            for group in groups
        ],
        [],
    )

    component_sets = [
        loader.load_all(
            query={"group": group, "kind": "Component"},
            patches=[
                SkillLevelPatch(
                    combat_orders_level=injected_values["combat_orders_level"],
                    passive_skill_level=injected_values["passive_skill_level"],
                    default_skill_levels=skill_levels,
                ),
                ArithmeticPatch(variables=reference_variables),
                VSkillImprovementPatch(improvements=v_improvements),
                HexaSkillImprovementPatch(improvements=hexa_improvements),
                get_hyper_skill_patch(group),
                SkillImprovementPatch(improvements=skill_improvements),
            ],
        )
        for group in groups
    ]

    components: list[Component] = sum(component_sets, [])
    components = _exclude_hexa_skill(components, hexa_replacements, skill_levels)

    engine_builder = EngineBuilder(bare_store(injected_values["action_stat"]))
    engine_builder.add_view("clock", clock_view)

    for component in components:
        engine_builder.add_component(component)

    engine_builder.add_dispatcher(timer_delay_dispatcher)
    engine_builder.add_aggregation_view(InformationParentView, "info")
    engine_builder.add_aggregation_view(ValidityParentView, "validity")
    engine_builder.add_aggregation_view(BuffParentView, "buff")
    engine_builder.add_aggregation_view(RunningParentView, "running")
    engine_builder.add_aggregation_view(KeydownParentView, "keydown")

    return engine_builder
