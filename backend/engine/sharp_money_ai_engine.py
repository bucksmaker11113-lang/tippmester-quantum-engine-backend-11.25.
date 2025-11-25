import numpy as np
from statistics import pstdev

class SharpMoneyAI:

    def analyze(
        self, 
        odds_history: list,
        market_odds: list,
        closing_odds: float,
        timeframe: float = 1.0
    ):

        if len(odds_history) < 3:
            return {"error": "not enough odds history"}

        open_odds = odds_history[0]
        current_odds = odds_history[-1]

        # 1) Movement magnitude & speed
        movement = open_odds - current_odds
        movement_velocity = abs(movement) / max(1, len(odds_history)) * timeframe

        # 2) Volatility
        volatility = pstdev(odds_history) if len(odds_history) > 5 else abs(movement)

        # 3) Market gap
        market_avg = float(np.mean(market_odds))
        market_gap = current_odds - market_avg

        # 4) Closing line drift
        closing_prob = 1 / closing_odds
        current_prob = 1 / current_odds
        closing_drift = closing_prob - current_prob

        # 5) Steam → sharp money
        steam_move = (
            abs(movement) > 0.15 and
            movement_velocity > 0.02 and
            abs(market_gap) > 0.05
        )

        # 6) Reverse steam
        reverse_steam = (
            abs(movement) > 0.12 and
            np.sign(movement) != np.sign(market_gap)
        )

        # 7) Limit bet indication
        limit_bet_signal = (
            abs(closing_drift) > 0.015 and
            movement_velocity > 0.03 and
            volatility < 0.12
        )

        # 8) Sharp consensus
        consensus_strength = float(np.mean([
            1 if abs(current_odds - x) < 0.05 else 0 for x in market_odds
        ]))

        # 9) Final weighted sharp score
        sharp_score = (
            abs(movement) * 25 +
            movement_velocity * 30 +
            abs(closing_drift) * 25 +
            abs(market_gap) * 10 +
            consensus_strength * 10
        )

        sharp_score = max(0, min(100, round(sharp_score, 2)))

        return {
            "sharp_score": sharp_score,
            "movement": float(movement),
            "movement_velocity": float(movement_velocity),
            "volatility": float(volatility),
            "market_gap": float(market_gap),
            "closing_drift": float(closing_drift),
            "steam_move": steam_move,
            "reverse_steam": reverse_steam,
            "limit_bet_signal": limit_bet_signal,
            "consensus_strength": consensus_strength,
        }
