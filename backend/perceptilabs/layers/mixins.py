class MixinDeepLearning:
    @property
    def dropout_rate(self):
        return 1.0 - float(self.keep_prob)

