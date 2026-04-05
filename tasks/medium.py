from typing import Dict, Any

class MediumTask:
    """
    Objective: Distribute food efficiently across multiple zones.
    Success Criteria: Total urgency reduction >= 0.3 across all zones using food kits.
    Initial State: 3 zones with moderate urgency, plenty of food kits but no ambulances.
    """
    def get_config(self) -> Dict[str, Any]:
        return {
            "max_steps": 5,
            "resources": {
                "ambulances": 0,
                "food_kits": 200
            },
            "zones": [
                {"name": "Town A", "people": 300, "urgency": 0.5},
                {"name": "Town B", "people": 300, "urgency": 0.5},
                {"name": "Town C", "people": 300, "urgency": 0.5}
            ]
        }

    def evaluate_success(self, initial_obs: Dict[str, Any], final_obs: Dict[str, Any]) -> bool:
        initial_urgency = sum(z["urgency"] for z in initial_obs["zones"])
        final_urgency = sum(z["urgency"] for z in final_obs["zones"])
        return (initial_urgency - final_urgency) >= 0.3
