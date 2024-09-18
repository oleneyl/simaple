import hashlib
import json
import os
from abc import ABC, abstractmethod

from simaple.container.character_provider import (
    CharacterDependentEnvironmentForCharacterProvider,
    CharacterProvider,
    SimulationEnvironmentForCharacterProvider,
    serialize_character_provider,
)
from simaple.container.simulation import SimulationEnvironment
from simaple.core import ExtendedStat


class CachedCharacterProvider(CharacterProvider):
    cached_character: ExtendedStat
    cached_simulation_config: CharacterDependentEnvironmentForCharacterProvider

    def character(self) -> ExtendedStat:
        return self.cached_character

    def get_character_dependent_simulation_config(
        self,
    ) -> CharacterDependentEnvironmentForCharacterProvider:
        return self.cached_simulation_config


class CharacterProviderCache(ABC):
    @abstractmethod
    def get(
        self,
        environment: SimulationEnvironmentForCharacterProvider,
        character_provider: CharacterProvider,
    ) -> tuple[CharacterProvider, bool]:
        pass

    def get_simulation_environment(
        self,
        environment: SimulationEnvironmentForCharacterProvider,
        character_provider: CharacterProvider,
    ) -> SimulationEnvironment:
        as_cached_character_provider, _ = self.get(environment, character_provider)

        return as_cached_character_provider.get_simulation_environment(
            environment,
        )

    def _compute_cache_key(
        self,
        environment: SimulationEnvironmentForCharacterProvider,
        character_provider: CharacterProvider,
    ) -> str:
        obj = {
            "setting": environment.model_dump_json(),
            "provider": serialize_character_provider(character_provider),
        }
        serialized_query = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)

        hash = hashlib.sha256()
        hash.update(serialized_query.encode())
        digest = hash.hexdigest()

        return f"{character_provider.get_name()}.{digest}"

    def _deserialize_output(self, value: str) -> CachedCharacterProvider:
        cached_provider = CachedCharacterProvider.model_validate_json(value)

        return cached_provider

    def _serialize_output(self, value: CachedCharacterProvider) -> str:
        return value.model_dump_json(indent=2)


class InMemoryCache(CharacterProviderCache):
    def __init__(self, saved_cache: dict[str, str] | None = None) -> None:
        if saved_cache is None:
            saved_cache = {}

        self.cache = saved_cache

    def get(
        self,
        environment: SimulationEnvironmentForCharacterProvider,
        character_provider: CharacterProvider,
    ) -> tuple[CharacterProvider, bool]:
        cache_key = self._compute_cache_key(environment, character_provider)

        if cache_key in self.cache:
            return self._deserialize_output(self.cache[cache_key]), True

        output = CachedCharacterProvider(
            cached_character=character_provider.character(),
            cached_simulation_config=character_provider.get_character_dependent_simulation_config(),
        )
        self.cache[cache_key] = self._serialize_output(output)
        return output, False

    def export(self) -> dict[str, str]:
        return self.cache


class PersistentStorageCache(CharacterProviderCache):
    def __init__(self, path: str = ".simaple.cache") -> None:
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({}, f)

    def get(
        self,
        environment: SimulationEnvironmentForCharacterProvider,
        character_provider: CharacterProvider,
    ) -> tuple[CharacterProvider, bool]:
        cache_key = self._compute_cache_key(environment, character_provider)

        with open(self.path, "r") as f:
            cache = json.load(f)

        if cache_key in cache:
            return self._deserialize_output(cache[cache_key]), True

        output = CachedCharacterProvider(
            cached_character=character_provider.character(),
            cached_simulation_config=character_provider.get_character_dependent_simulation_config(),
        )
        cache[cache_key] = self._serialize_output(output)

        with open(self.path, "w") as f:
            json.dump(cache, f, indent=2)

        return output, False
