class KellyEngine:
    def kelly(self, prob, odds):
        b = odds - 1
        k = (prob * (b + 1) - 1) / b
        return max(0, round(k * 100, 2))
