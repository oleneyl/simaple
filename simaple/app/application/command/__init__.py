import pydantic

from simaple.app.application.exception import (
    ApplicationError,
    UnknownSimulatorException,
)
from simaple.app.domain.simulator import Simulator
from simaple.app.domain.simulator_configuration import SimulatorConfiguration
from simaple.app.domain.uow import UnitOfWork
from simaple.simulate.base import Action, Checkpoint


def create_simulator(conf: SimulatorConfiguration, uow: UnitOfWork) -> str:
    simulator = Simulator.create_from_config(conf)
    uow.simulator_repository().add(simulator)

    return simulator.id


def play_operation(simulator_id: str, dsl: str, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    simulator.dispatch(dsl)
    uow.simulator_repository().update(simulator)


def rollback(simulator_id: str, target_index: int, uow: UnitOfWork) -> None:
    simulator = uow.simulator_repository().get(simulator_id)

    if simulator is None:
        raise UnknownSimulatorException()

    simulator.rollback(target_index)
    uow.simulator_repository().update(simulator)
