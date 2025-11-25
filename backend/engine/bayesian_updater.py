class BayesianUpdater:
    def update(self, prior_prob, sharp_score):
        likelihood = sharp_score / 100
        posterior = (prior_prob * likelihood) / max(
            1e-9,
            (prior_prob * likelihood + (1 - prior_prob) * (1 - likelihood))
        )
        return float(posterior)
