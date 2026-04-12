from typing import List, Dict, Any
from .models import Zone, Resources, Observation, Allocation, Action, Reward, StepResult

class DisasterEnv:
    def __init__(self):
        self._observation: Observation = None
        self._max_steps = 5

    def reset(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Initializes the environment with deterministic values.
        If config is provided, it uses the config values.
        """
        if config:
            zones = [Zone(**z) for z in config.get("zones", [])]
            resources = Resources(**config.get("resources", {}))
            self._max_steps = config.get("max_steps", 5)
        else:
            zones = [
                Zone(name="Metropolis", people=1000, urgency=0.9),
                Zone(name="Suburbia", people=500, urgency=0.4),
                Zone(name="Rural", people=200, urgency=0.2)
            ]
            resources = Resources(ambulances=10, food_kits=100)
            self._max_steps = 5
        
        self._observation = Observation(
            zones=zones,
            resources=resources,
            time_remaining=self._max_steps
        )
        return self._observation.model_dump()

    def state(self) -> Dict[str, Any]:
        if self._observation is None:
            raise ValueError("Environment not reset.")
        return self._observation.model_dump()

    def step(self, action: Any) -> Dict[str, Any]:
        """
        Processes allocations and returns the step results.
        Supports both Action Pydantic model and plain dict input.
        """
        if self._observation is None:
            raise ValueError("Environment not reset. Call reset() before step().")

        if self._observation.time_remaining <= 0:
            return {
                "observation": self._observation.model_dump(),
                "reward": 0.0,
                "done": True,
                "info": {"error": "Episode already finished."}
            }

        # Ensure action is converted to Action Pydantic model
        if isinstance(action, dict):
            try:
                action = Action(**action)
            except Exception as e:
                # Return penalty result on invalid input to prevent crashing
                return {
                    "observation": self._observation.model_dump(),
                    "reward": -5.0,
                    "done": False,
                    "info": {"error": f"Invalid action format: {str(e)}"}
                }

        reward_value = 0.0
        info = {"logs": []}

        # Penalize empty actions (inaction cost)
        if not action.allocations:
            reward_value -= 2.0
            info["logs"].append("Penalty: No allocations provided this step.")

        # Track resource usage to penalize waste/over-allocation
        used_ambulances = 0
        used_food = 0

        for alloc in action.allocations:
            zone = next((z for z in self._observation.zones if z.name == alloc.zone), None)
            
            # Penalize allocating to non-existent zone
            if not zone:
                reward_value -= 1.0
                info["logs"].append(f"Penalty: Non-existent zone '{alloc.zone}'")
                continue

            # Ensure amount is non-negative and integer
            requested_amount = max(0, int(alloc.amount))

            if alloc.resource == "ambulance":
                available = self._observation.resources.ambulances - used_ambulances
                amount = min(requested_amount, available)
                
                if requested_amount > available:
                    reward_value -= (requested_amount - available) * 0.5 # Over-allocation penalty
                    info["logs"].append(f"Waste: Requested {requested_amount} ambulances but only {available} available for {zone.name}")
                
                if amount > 0:
                    used_ambulances += amount
                    # Reward scaled by urgency: higher urgency = higher reward
                    # Impact: 1 ambulance reduces urgency by 20% of its current value
                    impact = amount * 0.2 * zone.urgency
                    zone.urgency = max(0.0, zone.urgency - impact)
                    reward_value += (impact * 100.0) 
                    info["logs"].append(f"Success: Deployed {amount} ambulances to {zone.name}")

            elif alloc.resource == "food_kits":
                available = self._observation.resources.food_kits - used_food
                amount = min(requested_amount, available)
                
                if requested_amount > available:
                    reward_value -= (requested_amount - available) * 0.1 # Over-allocation penalty
                    info["logs"].append(f"Waste: Requested {requested_amount} food kits but only {available} available for {zone.name}")
                
                if amount > 0:
                    used_food += amount
                    # Food reduces urgency slightly (1% per kit)
                    impact = amount * 0.01 * zone.urgency
                    zone.urgency = max(0.0, zone.urgency - impact)
                    reward_value += (impact * 50.0)
                    info["logs"].append(f"Success: Delivered {amount} food kits to {zone.name}")

        # Finalize resource reduction
        self._observation.resources.ambulances = max(0, self._observation.resources.ambulances - used_ambulances)
        self._observation.resources.food_kits = max(0, self._observation.resources.food_kits - used_food)

        # --- Dynamic Urgency Degradation ---
        # Disaster effects worsen over time if not stabilized
        for zone in self._observation.zones:
            if 0 < zone.urgency < 1.0:
                # Base growth + acceleration based on current urgency
                degradation = 0.01 + (zone.urgency * 0.02)
                
                # Check if this zone received medical help this turn
                medical_help = any(a.resource == "ambulance" and a.zone == zone.name for a in action.allocations)
                if medical_help:
                    degradation *= 0.1 # Medical presence slows crisis progression
                
                zone.urgency = min(1.0, zone.urgency + degradation)

        # Decrease time
        self._observation.time_remaining -= 1
        done = self._observation.time_remaining <= 0

        return {
            "observation": self._observation.model_dump(),
            "reward": round(reward_value, 2),
            "done": done,
            "info": info
        }
