class MixinDeepLearning:
    @property
    def dropout_rate(self):
        return 1.0 - self.keep_prob

