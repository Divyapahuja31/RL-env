from typing import Dict, Any

class Grader:
    def __init__(self, max_attainable_reward: float = 100.0):
        self.max_attainable_reward = max_attainable_reward

    def evaluate(self, total_reward: float, final_observation: Dict[str, Any]) -> float:
        """Calculates a final score between 0.0 and 1.0."""
        base_score = total_reward / self.max_attainable_reward
        return max(0.0, min(1.0, base_score))
