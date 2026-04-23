from dataclasses import dataclass
import numpy as np

type Array = np.ndarray

@dataclass
class FmtArray:
    _array: Array

    def __format__(self, spec: str) -> str:
        return np.array2string(self._array, formatter={
            "float_kind": lambda x: format(x, spec)
        })