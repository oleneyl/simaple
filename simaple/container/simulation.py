from abc import ABCMeta, abstractmethod
from typing import cast

import pydantic

from simaple.core import ExtendedStat, JobType
from simaple.data.jobs import get_skill_profile
from simaple.data.jobs.builtin import get_builtin_strategy, get_damage_logic
from simaple.simulate.base import SimulationRuntime
from simaple.simulate.engine import OperationEngine
from simaple.simulate.kms import get_builder
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage


def add_extended_stats(*action_stats):
    return sum(action_stats, ExtendedStat())


class CharacterDependentSimulationConfig(pydantic.BaseModel):
    passive_skill_level: int
    combat_orders_level: int
    weapon_pure_attack_power: int

    jobtype: JobType
    level: int

    def damage_logic(self):
        return get_damage_logic(self.jobtype, self.combat_orders_level)


class CharacterProvider(pydantic.BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def character(self) -> ExtendedStat: ...

    @abstractmethod
    def get_character_dependent_simulation_config(
        self,
    ) -> CharacterDependentSimulationConfig: ...

    @classmethod
    def get_name(cls):
        return cls.__name__


class SimulationSetting(pydantic.BaseModel):
    use_doping: bool = True

    armor: int = 300
    mob_level: int = 265
    force_advantage: float = 1.0

    v_skill_level: int = 30
    hexa_skill_level: int = 1
    hexa_mastery_level: int = 1
    v_improvements_level: int = 60
    hexa_improvements_level: int = 0

    weapon_attack_power: int = 0


class SimulationContainer:
    def __init__(
        self, setting: SimulationSetting, character_provider: CharacterProvider
    ) -> None:
        self.setting = setting
        self.character_provider = character_provider

    def config(self) -> CharacterProvider:
        return self.character_provider

    def skill_profile(self):
        config = self.config()
        return get_skill_profile(
            config.get_character_dependent_simulation_config().jobtype
        )

    def builtin_strategy(self):
        return get_builtin_strategy(
            self.character_provider.get_character_dependent_simulation_config().jobtype
        )

    def level_advantage(self):
        config = self.setting
        return LevelAdvantage().get_advantage(
            config.mob_level,
            self.character_provider.get_character_dependent_simulation_config().level,
        )

    def damage_calculator(self) -> DamageCalculator:
        config = self.setting

        character = self.character_provider.character()
        damage_logic = (
            self.character_provider.get_character_dependent_simulation_config().damage_logic()
        )
        level_advantage = self.level_advantage()

        return DamageCalculator(
            character_spec=character.stat,
            damage_logic=damage_logic,
            armor=config.armor,
            level_advantage=level_advantage,
            force_advantage=config.force_advantage,
        )

    def builder(self):
        skill_profile = self.skill_profile()
        config = self.setting
        character = self.character_provider.character()
        character_dependent_simulation_setting = (
            self.character_provider.get_character_dependent_simulation_config()
        )

        return get_builder(
            skill_profile.get_groups(),
            skill_profile.get_skill_levels(
                config.v_skill_level,
                config.hexa_skill_level,
                config.hexa_mastery_level,
            ),
            skill_profile.get_filled_v_improvements(config.v_improvements_level),
            skill_profile.get_filled_hexa_improvements(config.hexa_improvements_level),
            skill_profile.get_skill_replacements(),
            {
                "character_stat": character.stat,
                "character_level": character_dependent_simulation_setting.level,
                "weapon_attack_power": config.weapon_attack_power,
                "weapon_pure_attack_power": character_dependent_simulation_setting.weapon_pure_attack_power,
                "action_stat": character.action_stat,
                "passive_skill_level": character_dependent_simulation_setting.passive_skill_level,
                "combat_orders_level": character_dependent_simulation_setting.combat_orders_level,
            },
        )

    def simulation_runtime(self) -> SimulationRuntime:
        builder = self.builder()
        return cast(SimulationRuntime, builder.build_simulation_runtime())

    def operation_engine(self) -> OperationEngine:
        builder = self.builder()
        return cast(OperationEngine, builder.build_operation_engine())
