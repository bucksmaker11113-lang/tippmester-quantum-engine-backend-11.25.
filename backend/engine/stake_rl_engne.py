class StakeRLEngine:
    def recommend(self, edge):
        if edge < 0:
            return 0.5
        if edge < 2:
            return 1
        if edge < 5:
            return 2
        return 3
