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
