class float_range:
    def __init__(self, start: float, stop: float, step: float):
        self.start = start
        self.stop = stop
        self.step = step

    def __len__(self):
        return int((self.stop - self.start) / self.step) + 1

    def __iter__(self):
        eps = abs(self.step) * 1e-9
        x = self.start
        while x <= self.stop + eps:
            yield x
            x += self.step
