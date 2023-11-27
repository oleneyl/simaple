from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Generator

from simaple.simulate.base import (
    Action,
    AddressedStore,
    Checkpoint,
    Event,
    EventCallback,
    EventHandler,
    RouterDispatcher,
    ViewerType,
    ViewSet,
    play,
)
from simaple.simulate.policy.base import (
    Operation,
    OperationLog,
    PlayLog,
    PolicyType,
    SimulationHistory,
    _BehaviorGenerator,
)
from simaple.simulate.policy.dsl import DSLError, OperandDSLParser
from simaple.simulate.report.base import Report
from simaple.simulate.reserved_names import Tag


class SimulationEngine(metaclass=ABCMeta):
    @abstractmethod
    def add_callback(self, handler: EventHandler) -> None:
        """Simulation Engine may ensure that given engine triggers registered callbacks."""


class MonotonicEngine(SimulationEngine):
    def __init__(
        self, store: AddressedStore, router: RouterDispatcher, viewset: ViewSet
    ):
        self._router: RouterDispatcher = router
        self._store = store
        self._viewset = viewset
        self._previous_callbacks: list[EventCallback] = []
        self._callbacks: list[EventHandler] = []

    def add_callback(self, handler: EventHandler) -> None:
        self._callbacks.append(handler)

    def get_viewer(self) -> ViewerType:
        return self._show

    def resolve(self, action: Action) -> list[Event]:
        return self._router(action, self._store)

    def play(self, action: Action) -> list[Event]:
        self._store, events = play(self._store, action, self._router)

        for event in events:
            for handler in self._callbacks:
                handler(event, self.get_viewer(), events)

        return events

    def save(self) -> Checkpoint:
        return Checkpoint.create(self._store)

    def load(self, ckpt: Checkpoint) -> None:
        self._store = ckpt.restore()

    def _show(self, view_name: str):
        return self._viewset.show(view_name, self._store)


class OperationEngine(SimulationEngine):
    def __init__(
        self,
        router: RouterDispatcher,
        store: AddressedStore,
        viewset: ViewSet,
        handlers: dict[str, Callable[[Operation], _BehaviorGenerator]],
    ):
        self._router = router
        self._viewset = viewset
        self._handlers = handlers

        self._buffered_events: list[Event] = []

        self._history = SimulationHistory(store)
        self._parser = OperandDSLParser()
        self._callbacks: list[EventHandler] = []

    def inspect(self, log: OperationLog) -> list[tuple[PlayLog, ViewerType]]:
        return [
            (playlog, self._viewset.get_viewer(playlog.checkpoint))
            for playlog in log.playlogs
        ]

    def add_callback(self, handler: EventHandler) -> None:
        self._callbacks.append(handler)

    def save_history(self) -> dict[str, Any]:
        return self._history.save()

    def operation_logs(self) -> Generator[OperationLog, None, None]:
        for operation_log in self._history:
            yield operation_log

    def length(self) -> int:
        return len(self._history)

    def history(self) -> SimulationHistory:
        """This returns "Shallow Copy" of SimulationHistory.
        Be cautious not to modify the returned SimulationHistory.
        Use this only for read.
        """
        return self._history.shallow_copy()

    def load_history(self, saved_history: dict[str, Any]) -> None:
        self._history.load(saved_history)

    def _exec(self, op: Operation, early_stop: int = -1) -> None:
        playlogs: list[PlayLog] = []
        store = self._history.current_ckpt().restore()

        for behavior in self._get_behavior_gen(op):
            if 0 < early_stop <= self._viewset.show("clock", store):
                break

            action = behavior(self._buffered_events)
            if action is None:
                break

            store, self._buffered_events = play(store, action, self._router)

            playlogs.append(
                PlayLog(
                    clock=self._viewset.show("clock", store),
                    action=action,
                    events=self._buffered_events,
                    checkpoint=Checkpoint(store_ckpt=store.save()),
                )
            )

            for event in self._buffered_events:
                for handler in self._callbacks:
                    handler(
                        event,
                        self._viewset.get_viewer(playlogs[-1].checkpoint),
                        self._buffered_events,
                    )

        self._history.commit(
            op,
            playlogs,
        )

    def _get_behavior_gen(self, op: Operation) -> _BehaviorGenerator:
        return self._handlers[op.command](op)

    def exec_policy(self, policy: PolicyType, early_stop: int = -1) -> None:
        operations = policy(self._context)
        for op in operations:
            self._exec(op, early_stop=early_stop)

    @property
    def _context(self):
        return (self.get_current_viewer(), self._buffered_events)

    def get_current_viewer(self) -> ViewerType:
        ckpt = self._history.current_ckpt()
        return self._viewset.get_viewer(ckpt)

    def get_report(self, playlog: PlayLog) -> Report:
        viewer = self._viewset.get_viewer(playlog.checkpoint)
        report = Report()
        buff = viewer("buff")
        for event in playlog.events:
            if event["tag"] == Tag.DAMAGE:
                report.add(0, event, buff)

        return report

    def rollback(self, idx: int):
        self._history.discard_after(idx)

    def exec_dsl(self, txt: str):
        ops = self._parser(txt)
        for op in ops:
            self._exec(op)

    def REPL(self):
        while True:
            txt = input(">> ")
            if txt == "exit":
                break

            if txt == "valid":
                print("-- valid skills --")
                for validity in self.get_current_viewer()("validity"):
                    if validity.valid:
                        print(f"{validity.name}")
            elif txt == "running":
                for running in self.get_current_viewer()("running"):
                    if running.time_left > 0:
                        print(f"{running.name} | {running.time_left}")
            else:
                try:
                    self.exec_dsl(txt)
                except DSLError as e:
                    print("Invalid DSL - try again")
                    print(f"Error Mesage: {e}")


def get_report(playlog: PlayLog, viewer: ViewerType) -> Report:
    report = Report()
    buff = viewer("buff")
    for event in playlog.events:
        if event["tag"] == Tag.DAMAGE:
            report.add(0, event, buff)

    return report
