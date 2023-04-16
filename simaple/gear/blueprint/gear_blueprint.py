from abc import ABCMeta, abstractmethod
from typing import Annotated, List, Literal, Optional, Tuple

from pydantic import BaseModel, Extra, Field, conint, validator

from simaple.core import Stat
from simaple.gear.bonus_factory import BonusFactory, BonusType
from simaple.gear.gear import Gear, GearMeta
from simaple.gear.improvements.scroll import Scroll
from simaple.gear.improvements.spell_trace import SpellTrace
from simaple.gear.improvements.starforce import Starforce
from simaple.gear.potential import AdditionalPotential, Potential


class AbstractGearBlueprint(BaseModel, metaclass=ABCMeta):
    class Config:
        extra = Extra.forbid

    @abstractmethod
    def build(self) -> Gear:
        ...


class BonusSpec(BaseModel):
    bonus_type: BonusType
    grade: Optional[conint(ge=1, le=7)]
    rank: Optional[conint(ge=1, le=7)]

    @validator("rank")
    def rank_and_grade_may_not_given_together(cls, v, values, **kwargs):
        if "grade" in values and values["grade"] is not None:
            raise ValueError("grade and rank may not given together.")
        return v


def _get_bonus_from_spec(bonus_factory: BonusFactory, bonus_spec: BonusSpec):
    grade = bonus_spec.grade or 8 - bonus_spec.rank
    return bonus_factory.create(
        bonus_spec.bonus_type,
        grade,
    )


class GeneralizedGearBlueprint(AbstractGearBlueprint):
    meta: GearMeta
    spell_traces: List[SpellTrace] = Field(default_factory=list)
    scrolls: List[Scroll] = Field(default_factory=list)
    starforce: Starforce
    bonuses: List[BonusSpec] = Field(default_factory=list)
    potential: Potential = Field(default_factory=Potential)
    additional_potential: AdditionalPotential = Field(
        default_factory=AdditionalPotential
    )

    def build(self) -> Gear:
        gear_stat = self.meta.base_stat.copy()

        # Apply spell trace and scroll, starforce
        spell_trace_and_scoll_stat = sum(
            [
                spell_trace.calculate_improvement(self.meta)
                for spell_trace in self.spell_traces
            ],
            Stat(),
        ) + sum(
            [scroll.calculate_improvement(self.meta) for scroll in self.scrolls],
            Stat(),
        )
        gear_stat += spell_trace_and_scoll_stat
        gear_stat += self.starforce.calculate_improvement(self.meta, ref_stat=gear_stat)

        # Apply bonus
        bonus_factory = BonusFactory()
        bonuses = [_get_bonus_from_spec(bonus_factory, spec) for spec in self.bonuses]

        bonus_stat = sum(
            [bonus.calculate_improvement(self.meta) for bonus in bonuses],
            Stat(),
        )

        gear_stat += bonus_stat

        return Gear(
            meta=self.meta,
            stat=gear_stat,
            scroll_chance=self.meta.max_scroll_chance,
            potential=self.potential.copy(),
            additional_potential=self.additional_potential.copy(),
        )


class PracticalGearBlueprint(AbstractGearBlueprint):
    meta: GearMeta
    spell_trace: Optional[SpellTrace] = None
    scroll: Optional[Scroll] = None
    star: int = 0
    bonuses: List[BonusSpec] = Field(default_factory=list)
    potential: Potential = Field(default_factory=Potential)
    additional_potential: AdditionalPotential = Field(
        default_factory=AdditionalPotential
    )

    def build(self):
        generalized_gear_blueprint = self.translate_into_generalized_gear_blueprint()
        return generalized_gear_blueprint.build()

    def translate_into_generalized_gear_blueprint(
        self,
    ) -> GeneralizedGearBlueprint:

        spell_traces = []
        scrolls = []

        if self.spell_trace is not None:
            spell_traces = [
                self.spell_trace for i in range(self.meta.max_scroll_chance)
            ]
        elif self.scroll is not None:
            scrolls = [self.scroll for i in range(self.meta.max_scroll_chance)]

        starforce = Starforce(enhancement_type="Starforce", star=self.star)
        starforce.apply_star_cutoff(self.meta)

        return GeneralizedGearBlueprint(
            meta=self.meta,
            spell_traces=spell_traces,
            scrolls=scrolls,
            starforce=starforce,
            bonuses=self.bonuses,
            potential=self.potential,
            additional_potential=self.additional_potential,
        )
