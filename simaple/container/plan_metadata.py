from typing import Any

import pydantic

from simaple.container.environment_provider import (
    EnvironmentProvider,
    ProviderConfinedSimulationEnvironment,
    get_environment_provider,
)
from simaple.container.simulation import SimulationContainer, SimulationEnvironment


class _ProviderMetadata(pydantic.BaseModel):
    name: str
    data: dict[str, Any]
    environment: ProviderConfinedSimulationEnvironment

    def get_environment_provider(self) -> EnvironmentProvider:
        return get_environment_provider(self.name, self.data)

    def get_simulation_environment(self) -> SimulationEnvironment:
        return self.get_environment_provider().get_simulation_environment(
            self.environment,
        )


class PlanMetadata(pydantic.BaseModel):
    author: str = ""
    provider: _ProviderMetadata | None = None
    environment: SimulationEnvironment | None = None

    def get_environment_provider_config(self) -> EnvironmentProvider:
        assert self.provider is not None
        return self.provider.get_environment_provider()

    def load_container(self) -> SimulationContainer:
        if self.environment is None:
            assert self.provider is not None
            environment = self.provider.get_simulation_environment()
        else:
            environment = self.environment

        return SimulationContainer(environment)
