from typing import Dict, Any

class Grader:
    def __init__(self, max_attainable_reward: float = 100.0):
        self.max_attainable_reward = max_attainable_reward

    def evaluate(self, total_reward: float, final_observation: Dict[str, Any]) -> float:
        """Calculates a final score between 0.0 and 1.0."""
        base_score = total_reward / self.max_attainable_reward

        # Penalties
        penalties = 0.0

        # Penalty for ignoring high urgency zones
        high_urgency_count = sum(1 for z in final_observation["zones"] if z["urgency"] > 0.7)
        penalties += high_urgency_count * 0.1

        # Penalty for wasting resources
        total_remaining_urgency = sum(z["urgency"] for z in final_observation["zones"])
        if total_remaining_urgency > 0.1:
            remaining_ambulances = final_observation["resources"]["ambulances"]
            penalties += remaining_ambulances * 0.05

        final_score = base_score - penalties
        return max(0.0, min(1.0, final_score))
