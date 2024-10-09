from typing import Optional

import pydantic

from simaple.simulate.base import Entity


class Lasting(Entity):
    time_left: float
    assigned_duration: float = 0.0

    def enabled(self):
        return self.time_left > 0

    def elapse(self, time: float):
        self.time_left -= time

    def set_time_left(self, time: float):
        self.time_left = time
        self.assigned_duration = time

    def get_elapsed_time(self) -> float:
        return self.assigned_duration - self.time_left


class Cooldown(Entity):
    time_left: float

    @property
    def available(self):
        return self.time_left <= 0

    def elapse(self, time: float):
        self.time_left -= time

    def set_time_left(self, time: float):
        self.time_left = time

    def minimum_time_to_available(self) -> float:
        return max(0, self.time_left)

    def reduce_by_rate(self, rate: float):
        self.time_left *= 1 - rate

    def reduce_by_value(self, time: float):
        self.time_left -= time


class Consumable(Entity):
    """
    "Stackable" cooldown.

    쿨타임이 다 찼면 스택이 하나 쌓이고 다시 쿨타임이 도는 Entity.
    """

    maximum_stack: int
    stack: int
    cooldown_duration: float
    time_left: float

    @property
    def available(self):
        return self.stack > 0

    def elapse(self, time: float):
        self.time_left -= time
        while self.time_left <= 0:
            self.time_left += self.cooldown_duration
            self.stack = min(self.stack + 1, self.maximum_stack)

        if self.stack == self.maximum_stack:
            self.time_left = self.cooldown_duration

    def get_stack(self) -> int:
        return self.stack

    def consume(self):
        self.stack -= 1


class Cycle(Entity):
    tick: int
    period: int

    def step(self):
        self.tick += 1
        self.tick = self.tick % self.period

    def get_tick(self) -> int:
        return self.tick

    def clear(self):
        self.tick = 0


class Periodic(Entity):
    interval: float = pydantic.Field(gt=0)
    initial_counter: Optional[float] = pydantic.Field(gt=0, default=None)

    interval_counter: float = pydantic.Field(gt=0, default=999_999_999)
    time_left: float = 0.0
    count: int = 0

    def set_time_left_without_delay(self, time: float) -> int:
        """
        Implement 0-delay periodic behavior.
        since 0-delay behavior always emit signal immediately; you may handle
        returned event as periodic event.
        """

        self.time_left = time
        self.interval_counter = (
            self.interval
        )  # interval count = 0 is not allowed. emit event and increase interval counter.
        self.count = 1

        return 1

    def set_time_left(self, time: float) -> None:
        """
        Set left time, with initial counter value.
        If initial counter not specified, default initial counter is `interval`.
        given initial counter may larger than 0; if initial counter is 0, this raises error.
        To use behavior with 0-initial counter, use `set_time_left_without_delay` with proper method handling.
        """
        if time <= 0:
            raise ValueError("Given time may greater than 0")

        if self.initial_counter is not None and self.initial_counter <= 0:
            raise ValueError(
                "Initial counter may greater than 0. Maybe you intended `set_time_left_without_delay`?"
            )

        self.time_left = time
        self.interval_counter = (
            self.initial_counter if self.initial_counter is not None else self.interval
        )
        self.count = 0

    def set_interval_counter(self, counter: float):
        self.interval_counter = counter

    def enabled(self):
        return self.time_left > 0

    def elapse(self, time: float) -> int:
        """
        Wrapper for resolving method.
        """
        initial_count = self.count

        periodic_state = self.model_copy(deep=True)
        while time > 0:
            periodic_state, time = self.resolve_step(periodic_state, time)

        self.time_left = periodic_state.time_left
        self.interval = periodic_state.interval
        self.interval_counter = periodic_state.interval_counter
        self.count = periodic_state.count

        return periodic_state.count - initial_count

    @classmethod
    def resolve_step(cls, state: "Periodic", time: float) -> tuple["Periodic", float]:
        """Resolve given time with minimal time step.
        Returns: time left, changed entity state.
        """
        state = state.model_copy(deep=True)
        if state.time_left <= 0:
            return state, 0

        time_to_resolve = time

        _dynamic_interval_counter = state.interval_counter
        min_interval_for_next_change = min(
            _dynamic_interval_counter, state.time_left, time_to_resolve
        )

        time_to_resolve -= min_interval_for_next_change
        _dynamic_interval_counter -= min_interval_for_next_change
        state.time_left -= min_interval_for_next_change

        if state.time_left == 0:
            return state, 0

        if _dynamic_interval_counter == 0:
            _dynamic_interval_counter += state.interval
            state.count += 1

        if _dynamic_interval_counter == 0:
            if state.time_left > 0:
                raise ValueError("Unexpected error")

            _dynamic_interval_counter = state.interval

        state.interval_counter = _dynamic_interval_counter

        return state, time_to_resolve

    def disable(self):
        self.time_left = 0


class Schedule(Entity):
    scheduled_times: list[float]
    timer: float = 999_999_999
    index: int = 0

    def start(self):
        self.timer = 0
        self.index = len([time for time in self.scheduled_times if time <= 0])
        return 0, self.index

    def elapse(self, time: float):
        if self.timer > self.scheduled_times[-1]:
            return self.index, self.index

        self.timer += time
        prev_index = self.index
        self.index = len([time for time in self.scheduled_times if time <= self.timer])
        return prev_index, self.index


class Stack(Entity):
    """
    시간 의존성이 없는 스택.
    """

    stack: int = 0
    maximum_stack: int

    def reset(self, value: int = 0):
        self.stack = value

    def increase(self, value: int = 1):
        self.stack = min(self.maximum_stack, self.stack + value)

    def is_full(self) -> bool:
        return self.stack == self.maximum_stack

    def get_stack(self) -> int:
        return self.stack

    def decrease(self, value: int = 1):
        self.stack -= value


class Integer(Entity):
    value: int = 0

    def get_value(self) -> int:
        return self.value

    def set_value(self, value: int):
        self.value = value


class LastingStack(Entity):
    """A stack, which includes finite duration."""

    stack: int = 0
    maximum_stack: int
    duration: float
    time_left: float = 0

    def reset(self):
        self.stack = 0
        self.time_left = 0

    def enabled(self) -> bool:
        return self.time_left > 0

    def increase(self, value: int = 1):
        self.stack = min(self.maximum_stack, self.stack + value)
        self.time_left = self.duration

    def get_stack(self) -> int:
        return self.stack

    def decrease(self, value: int = 1):
        self.stack -= value

    def elapse(self, time: float):
        self.time_left -= time
        if self.time_left < 0:
            self.reset()

    def is_maximum(self) -> bool:
        return self.stack == self.maximum_stack

    def regulate(self, value: int) -> None:
        self.stack = min(value, self.stack)


class Keydown(Entity):
    interval: float
    interval_counter: float = 0.0
    time_left: float = -1

    @property
    def running(self) -> bool:
        return self.time_left > 0

    def get_next_delay(self) -> float:
        return min(self.interval_counter, self.time_left)

    def start(self, maximum_keydown_time: float, prepare_delay: float):
        self.interval_counter = prepare_delay
        self.time_left = maximum_keydown_time

    def stop(self):
        self.time_left = 0

    def resolving(self, time: float):
        resolving_time_left = self.time_left - max(0, self.interval_counter)
        self.time_left -= time
        self.interval_counter -= time

        # pylint:disable=chained-comparison
        while resolving_time_left >= 0 and self.interval_counter <= 0:
            yield
            self.interval_counter += self.interval
            resolving_time_left -= self.interval
