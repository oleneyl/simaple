from typing import List, Tuple

from pydantic import BaseModel, Field

from simaple.core.base import ActionStat, Stat
from simaple.core.jobtype import JobType


def empty_options():
    return [Stat() for v in range(5)]


def empty_action_stats():
    return [ActionStat() for v in range(5)]


class UnionBlock(BaseModel):
    job: JobType
    options: List[Stat] = Field(default_factory=empty_options)
    action_stat_options: List[ActionStat] = Field(default_factory=empty_action_stats)

    def get_stat(self, size: int) -> Stat:
        if size == 0:
            return Stat()
        return self.options[size - 1].copy()

    def get_action_stat(self, size: int) -> ActionStat:
        if self.action_stat_options is None or size == 0:
            return ActionStat()

        return self.action_stat_options[size - 1].copy()


def get_all_blocks():
    UNION_STAT_VALUE_REFERENCE = [10, 20, 40, 80, 100]

    return [
        UnionBlock(
            job=JobType.hero,
            options=[Stat(STR_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.darkknight, options=[Stat() for v in range(5)]
        ),  # HP% 2,3,4,5,6  TODO
        UnionBlock(
            job=JobType.paladin,
            options=[Stat(STR_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.bishop,
            options=[Stat(INT_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.archmagefb, options=[Stat() for v in UNION_STAT_VALUE_REFERENCE]
        ),  # MP% 2,3,4,5,6  TODO
        UnionBlock(
            job=JobType.archmagetc,
            options=[Stat(INT_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.nightlord,
            options=[Stat(critical_rate=v) for v in (1, 2, 3, 4, 5)],
        ),
        UnionBlock(
            job=JobType.shadower,
            options=[Stat(LUK_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.dualblade,
            options=[Stat(LUK_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.bowmaster,
            options=[Stat(DEX_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.sniper, options=[Stat(critical_rate=v) for v in (1, 2, 3, 4, 5)]
        ),
        UnionBlock(
            job=JobType.pathfinder,
            options=[Stat(DEX_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.corsair,
            action_stat_options=[
                ActionStat(summon_duration=v) for v in (4, 6, 8, 10, 12)
            ],
        ),
        UnionBlock(
            job=JobType.buccaneer,
            options=[Stat(STR_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.cannoneer,
            options=[Stat(STR_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.soulmaster,
            options=[Stat(MHP=v) for v in (250, 500, 10000, 2000, 2500)],
        ),  # static MHP. TODO
        UnionBlock(
            job=JobType.flamewizard,
            options=[Stat(INT_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.windbreaker,
            options=[Stat(DEX_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.nightwalker,
            options=[Stat(LUK_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.striker,
            options=[Stat(STR_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.mihile,
            options=[Stat(MHP=v) for v in (250, 500, 10000, 2000, 2500)],
        ),  # static MHP. TODO
        UnionBlock(job=JobType.demonavenger),  # immunity.
        UnionBlock(
            job=JobType.demonslayer,
            options=[Stat(boss_damage_multiplier=v) for v in (1, 2, 3, 5, 6)],
        ),
        UnionBlock(
            job=JobType.battlemage,
            options=[Stat(INT_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.wildhunter,
            options=[Stat(damage_multiplier=v * 0.2) for v in (4, 8, 12, 16, 20)],
        ),
        UnionBlock(
            job=JobType.mechanic,
            action_stat_options=[
                ActionStat(buff_duration=v) for v in (5, 10, 15, 20, 25)
            ],
        ),
        UnionBlock(
            job=JobType.zenon,
            options=[
                Stat(LUK_static=v / 2, STR_static=v / 2, DEX_static=v / 2)
                for v in UNION_STAT_VALUE_REFERENCE
            ],
        ),
        UnionBlock(job=JobType.evan),  # MP heal
        UnionBlock(
            job=JobType.luminous,
            options=[Stat(INT_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.mercedes,
            action_stat_options=[
                ActionStat(cooltime_reduce_rate=v) for v in (2, 3, 4, 5, 6)
            ],
        ),
        UnionBlock(job=JobType.phantom),  # meso incr %
        UnionBlock(
            job=JobType.eunwol,
            options=[Stat(critical_damage=v) for v in (1, 2, 3, 5, 6)],
        ),
        UnionBlock(job=JobType.aran),  # HP heal
        UnionBlock(
            job=JobType.kaiser,
            options=[Stat(STR_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.kain,
            options=[Stat(DEX_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.cadena,
            options=[Stat(LUK_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.angelicbuster,
            options=[Stat(DEX_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.adele,
            options=[Stat(STR_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.illium,
            options=[Stat(INT_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.ark,
            options=[Stat(STR_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.lara,
            options=[Stat(INT_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.hoyoung,
            options=[Stat(LUK_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(job=JobType.zero),  # exp +
        UnionBlock(
            job=JobType.kinesis,
            options=[Stat(INT_static=v) for v in UNION_STAT_VALUE_REFERENCE],
        ),
        UnionBlock(
            job=JobType.virtual_maplestory_m,
            options=[Stat(magic_attack=v, attack_power=v) for v in (5, 10, 15, 20, 20)],
        ),
        UnionBlock(
            job=JobType.blaster,
            options=[Stat(ignored_defence=v) for v in (1, 2, 3, 5, 6)],
        ),
    ]


def get_empty_block_sizes():
    return list(range(len(get_all_blocks())))


def get_union_occupation_values():
    return [
        [(Stat(boss_damage_multiplier=v), ActionStat()) for v in range(41)],
        [(Stat(ignored_defence=v), ActionStat()) for v in range(41)],
        [(Stat(critical_damage=v), ActionStat()) for v in range(41)],
        [(Stat(critical_rate=v), ActionStat()) for v in range(41)],
        [(Stat(), ActionStat(buff_duration=v)) for v in range(41)],
    ]


UNION_LENGTH = len(get_all_blocks())
UNION_OCCUPATION_LENGTH = len(get_union_occupation_values())


class UnionBlockstat(BaseModel):
    block_size: List[int] = Field(default_factory=get_empty_block_sizes)
    blocks: List[UnionBlock] = Field(default_factory=get_all_blocks)

    @classmethod
    def create_with_some_large_blocks(
        cls, large_block_jobs: List[JobType], default_size: int = 4, large_size: int = 5
    ):
        blocks = get_all_blocks()
        size = [
            (default_size if block.job in large_block_jobs else large_size)
            for block in blocks
        ]
        return UnionBlockstat(blocks=blocks, block_size=size)

    @classmethod
    def get_length(cls):
        return UNION_LENGTH

    def get_index(self, jobtype: JobType):
        for idx, block in enumerate(self.blocks):
            if block.job == jobtype:
                return idx

        raise KeyError

    def get_stat(self, mask: List[int]) -> Stat:
        stat = Stat()
        for enabled, block, size in zip(mask, self.blocks, self.block_size):
            if enabled:
                stat += block.get_stat(size)

        return stat

    def get_action_stat(self, mask: List[int]) -> ActionStat:
        stat = ActionStat()
        for enabled, block, size in zip(mask, self.blocks, self.block_size):
            if enabled:
                stat += block.get_action_stat(size)

        return stat


class UnionOccupationStat(BaseModel):
    occupation_state: List[int]
    occupation_value: List[List[Tuple[Stat, ActionStat]]] = Field(
        default_factory=get_union_occupation_values
    )

    @classmethod
    def length(cls):
        return UNION_OCCUPATION_LENGTH

    def get_stat(self) -> Stat:
        return sum(
            [
                value[occupation][0]
                for value, occupation in zip(
                    self.occupation_value, self.occupation_state
                )
            ],
            Stat(),
        )

    def get_action_stat(self) -> ActionStat:
        return sum(
            [
                value[occupation][1]
                for value, occupation in zip(
                    self.occupation_value, self.occupation_state
                )
            ],
            ActionStat(),
        )
