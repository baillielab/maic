class Transformer:
    def transform(self, initial, mean) -> float:
        pass

class Scaler:
    def scale(self, score, stddev) -> float:
        pass

class Corrector:
    @property
    def transformer(self) -> Transformer:
        pass

    @property
    def scaler(self) -> Scaler:
        pass

    @property
    def name(self) -> str:
        pass