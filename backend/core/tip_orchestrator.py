from backend.engine.sharp_money_ai_engine import SharpMoneyAI
from backend.engine.fusion_engine import FusionEngine
from backend.engine.bayesian_updater import BayesianUpdater
from backend.engine.edge_evaluator import EdgeEvaluator
from backend.engine.stake_rl_engine import StakeRLEngine
from backend.engine.stake_kelly_engine import KellyEngine

class TipOrchestrator:
    def __init__(self):
        self.sharp = SharpMoneyAI()
        self.fusion = FusionEngine()
        self.bayes = BayesianUpdater()
        self.edge_eval = EdgeEvaluator()
        self.rl_stake = StakeRLEngine()
        self.kelly = KellyEngine()

    def generate_tip(self, odds_history, market_odds, closing_odds, offered_odds):
        sharp = self.sharp.analyze(odds_history, market_odds, closing_odds)

        model_prob = 0.58  # helyettesíthető ML modellel
        bayes_adj = self.bayes.update(model_prob, sharp["sharp_score"])
        edge = self.edge_eval.evaluate(bayes_adj, offered_odds)
        final_score = self.fusion.fuse(sharp["sharp_score"], model_prob, bayes_adj, edge)
        stake_rl = self.rl_stake.recommend(edge)
        stake_kelly = self.kelly.kelly(bayes_adj, offered_odds)

        return {
            "sharp": sharp,
            "bayesian_probability": bayes_adj,
            "edge": edge,
            "final_score": final_score,
            "stake_rl": stake_rl,
            "stake_kelly_percent": stake_kelly,
        }
