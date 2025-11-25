class FusionEngine:
    def fuse(self, sharp_score, model_prob, bayes_adj, edge_value):
        return float(
            sharp_score * 0.35 +
            model_prob * 0.25 +
            bayes_adj * 0.20 +
            edge_value * 0.20
        )
