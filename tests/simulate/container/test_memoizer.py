import os
import tempfile

from simaple.container.environment_provider import (
    BaselineEnvironmentProvider,
    ProviderConfinedSimulationEnvironment,
)
from simaple.container.memoizer import InMemoryMemoizer, PersistentStorageMemoizer
from simaple.core import JobType
from simaple.core.job_category import JobCategory


def test_inmemory_memoizer():
    saved_memos = {}
    memoizer = InMemoryMemoizer(saved_memos)

    confined_environment = ProviderConfinedSimulationEnvironment()
    environment_provider = BaselineEnvironmentProvider(
        union_block_count=10,
        tier="Legendary",
        jobtype=JobType.archmagefb,
        job_category=JobCategory.magician,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        artifact_level=40,
    )
    second_environment_provider = BaselineEnvironmentProvider(
        union_block_count=10 + 1,
        tier="Legendary",
        jobtype=JobType.archmagefb,
        job_category=JobCategory.magician,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        artifact_level=40,
    )

    _, hit = memoizer.get_memo(confined_environment, environment_provider)
    assert not hit

    _, hit = memoizer.get_memo(confined_environment, environment_provider)
    assert hit

    _, hit = memoizer.get_memo(confined_environment, second_environment_provider)
    assert not hit

    exported_memos = memoizer.export()
    new_memoizer = InMemoryMemoizer(exported_memos)
    _, hit = new_memoizer.get_memo(confined_environment, environment_provider)
    assert hit

    _, hit = new_memoizer.get_memo(confined_environment, second_environment_provider)
    assert hit


def test_storage_memoizer():
    with tempfile.TemporaryDirectory() as temp_dir:
        memoizer = PersistentStorageMemoizer(os.path.join(temp_dir, "memo.json"))

        setting = ProviderConfinedSimulationEnvironment()
        environment_provider = BaselineEnvironmentProvider(
            union_block_count=10,
            tier="Legendary",
            jobtype=JobType.archmagefb,
            job_category=JobCategory.magician,
            level=270,
            passive_skill_level=0,
            combat_orders_level=1,
            artifact_level=40,
        )
        second_environment_provider = BaselineEnvironmentProvider(
            union_block_count=10 + 1,
            tier="Legendary",
            jobtype=JobType.archmagefb,
            job_category=JobCategory.magician,
            level=270,
            passive_skill_level=0,
            combat_orders_level=1,
            artifact_level=40,
        )

        _, hit = memoizer.get_memo(setting, environment_provider)
        assert not hit

        _, hit = memoizer.get_memo(setting, environment_provider)
        assert hit

        _, hit = memoizer.get_memo(setting, second_environment_provider)
        assert not hit

        _, hit = memoizer.get_memo(setting, environment_provider)
        assert hit

        _, hit = memoizer.get_memo(setting, second_environment_provider)
        assert hit
