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