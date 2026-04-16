from typing import cast, Callable
from collections.abc import Iterable

type Predicate[T] = Callable[[T], bool]

def partition[T](pred: Predicate[T], xs: Iterable[T]) -> tuple[Iterable[T], Iterable[T]]:
    trues: list[T] = []
    falses: list[T] = []
    for x in xs:
        if pred(x):
            trues.append(x)
        else:
            falses.append(x)
    return falses, trues

def unzip2[T, U](xs: Iterable[tuple[T, U]]) -> tuple[list[T], list[U]]:
    ts: list[T] = []
    us: list[U] = []
    for t, u in xs:
        ts.append(t)
        us.append(u)
    return ts, us

class float_range:
    def __init__(self, start: float, stop: float, step: float):
        self.start = start
        self.stop = stop
        self.step = step

    def __len__(self):
        return int((self.stop - self.start) / self.step)

    def __iter__(self):
        x = self.start
        while x < self.stop:
            yield x
            x += self.step