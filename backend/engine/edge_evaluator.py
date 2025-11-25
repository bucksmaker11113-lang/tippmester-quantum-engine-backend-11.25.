class EdgeEvaluator:
    def evaluate(self, prob, odds):
        fair = 1 / odds
        edge = (prob - fair) * 100
        return round(edge, 2)
