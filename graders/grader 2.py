from typing import Dict, Any, List

class Grader:
    def __init__(self, max_attainable_reward: float = 100.0):
        self.max_attainable_reward = max_attainable_reward

    def evaluate(self, total_reward: float, final_observation: Dict[str, Any]) -> float:
        """
        Calculates a final score between 0.0 and 1.0 based on reward,
        resource management, and zone prioritization.
        """
        # 1. Normalize and clamp reward
        base_score = total_reward / self.max_attainable_reward
        
        # 2. Penalties
        penalties = 0.0
        
        # Penalty for ignoring high urgency zones
        # If any zone still has urgency > 0.7 at the end, apply a penalty
        high_urgency_count = sum(1 for z in final_observation["zones"] if z["urgency"] > 0.7)
        penalties += high_urgency_count * 0.1
        
        # Penalty for wasting resources
        # If resources are left over when zones are still urgent, it's inefficient
        total_remaining_urgency = sum(z["urgency"] for z in final_observation["zones"])
        if total_remaining_urgency > 0.1:
            remaining_ambulances = final_observation["resources"]["ambulances"]
            # Penalty for each unused ambulance if there was still work to do
            penalties += remaining_ambulances * 0.05
            
        # 3. Final calculation
        final_score = base_score - penalties
        
        # 4. Clamp between 0.0 and 1.0
        return max(0.0, min(1.0, final_score))

    def get_grade_report(self, total_reward: float, final_observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provides a detailed breakdown of the score.
        """
        score = self.evaluate(total_reward, final_observation)
        
        high_urgency_zones = [z["name"] for z in final_observation["zones"] if z["urgency"] > 0.7]
        remaining_res = final_observation["resources"]
        
        return {
            "score": round(score, 3),
            "total_reward": round(total_reward, 2),
            "high_urgency_penalty_applied": len(high_urgency_zones) > 0,
            "resource_waste_detected": (sum(z["urgency"] for z in final_observation["zones"]) > 0.1 
                                       and remaining_res["ambulances"] > 0),
            "passing": score >= 0.5
        }
