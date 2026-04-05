from typing import Dict, Any

class EasyTask:
    """
    Objective: Allocate ambulances to the highest urgency zone.
    Success Criteria: Urgency of 'Danger Zone' reduced by at least 0.5.
    Initial State: 2 zones, one with extreme urgency (0.95).
    """
    def get_config(self) -> Dict[str, Any]:
        return {
            "max_steps": 3,
            "resources": {
                "ambulances": 5,
                "food_kits": 0
            },
            "zones": [
                {"name": "Danger Zone", "people": 100, "urgency": 0.95},
                {"name": "Safe Zone", "people": 500, "urgency": 0.1}
            ]
        }

    def evaluate_success(self, final_obs: Dict[str, Any]) -> bool:
        danger_zone = next(z for z in final_obs["zones"] if z["name"] == "Danger Zone")
        return danger_zone["urgency"] <= 0.45
