class float_range:
    def __init__(self, start: float, stop: float, step: float):
        self.start = start
        self.stop = stop
        self.step = step

    def __len__(self):
        return int((self.stop - self.start) / self.step) + 1

    def __iter__(self):
        x = self.start
        while x < self.stop:
            yield x
            x += self.step