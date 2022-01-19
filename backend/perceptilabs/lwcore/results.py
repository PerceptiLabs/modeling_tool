class LayerResults:
    def __init__(self, sample, out_shape, variables, columns, code_error, instantiation_error, strategy_error, trained):
        self.sample = sample
        self.out_shape = out_shape
        self.variables = variables
        self.columns = columns
        self.code_error = code_error
        self.instantiation_error = instantiation_error
        self.strategy_error = strategy_error
        self.trained = trained

    @property
    def has_errors(self):
        return bool(self.code_error or self.instantiation_error or self.strategy_error)

    @property
    def errors(self):
        for error_type in ['code_error', 'instantiation_error', 'strategy_error']:
            value = getattr(self, error_type)
            if value is not None:
                yield (error_type, value)

    def __eq__(self, other):
        if (
                self.out_shape != other.out_shape or
                self.columns != other.columns or
                self.trained != other.trained or
                self.code_error != other.code_error or
                self.instantiation_error != other.instantiation_error or
                self.strategy_error != other.strategy_error
        ):
            return False
        
        if self.sample.keys() != other.sample.keys():
            return False

        for key in self.sample.keys():
            if (self.sample[key] != other.sample[key]).any():
                return False
            
        return True
