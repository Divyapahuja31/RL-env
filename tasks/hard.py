from typing import Dict, Any

class HardTask:
    """
    Objective: Maximize total survival under limited resources and time.
    Success Criteria: Total urgency reduction >= 1.0 AND at least one zone urgency reaches 0.0.
    Initial State: 5 zones with varying urgency, very limited ambulances (3) and food kits (100).
    """
    def get_config(self) -> Dict[str, Any]:
        return {
            "max_steps": 4, # Tighter deadline
            "resources": {
                "ambulances": 3,
                "food_kits": 50 # Half the previous amount
            },
            "zones": [
                {"name": "Epicenter", "people": 1000, "urgency": 0.95},
                {"name": "Hospital District", "people": 800, "urgency": 0.85},
                {"name": "Industrial Zone", "people": 600, "urgency": 0.75},
                {"name": "West Side", "people": 500, "urgency": 0.65},
                {"name": "East Side", "people": 500, "urgency": 0.55},
                {"name": "Outskirts", "people": 200, "urgency": 0.45},
                {"name": "Remote", "people": 100, "urgency": 0.35}
            ]
        }

    def evaluate_success(self, initial_obs: Dict[str, Any], final_obs: Dict[str, Any]) -> bool:
        initial_urgency = sum(z["urgency"] for z in initial_obs["zones"])
        final_urgency = sum(z["urgency"] for z in final_obs["zones"])
        any_zero = any(z["urgency"] == 0.0 for z in final_obs["zones"])
        return (initial_urgency - final_urgency) >= 1.0 and any_zero
