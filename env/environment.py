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
            raise ValueError("Environment not reset.")

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

        # Penalize no action
        if not action.allocations:
            reward_value -= 2.0
            info["logs"].append("Penalty: No action taken.")

        # Track resource usage to penalize waste
        used_ambulances = 0
        used_food = 0

        for alloc in action.allocations:
            zone = next((z for z in self._observation.zones if z.name == alloc.zone), None)
            
            # Penalize allocating to non-existent zone or over-allocating
            if not zone:
                reward_value -= 1.0
                info["logs"].append(f"Penalty: Invalid zone {alloc.zone}")
                continue

            if alloc.resource == "ambulance":
                amount = min(alloc.amount, self._observation.resources.ambulances - used_ambulances)
                if amount < alloc.amount:
                    reward_value -= (alloc.amount - amount) * 0.5 # Waste penalty
                    info["logs"].append(f"Waste: Over-allocated ambulances to {zone.name}")
                
                if amount > 0:
                    used_ambulances += amount
                    # Reward scaled by urgency: higher urgency = higher reward
                    impact = amount * 0.2 * zone.urgency
                    zone.urgency = max(0.0, zone.urgency - impact)
                    reward_value += (impact * 100.0) 
                    info["logs"].append(f"Success: Allocated {amount} ambulances to {zone.name}")

            elif alloc.resource == "food_kits":
                amount = min(alloc.amount, self._observation.resources.food_kits - used_food)
                if amount < alloc.amount:
                    reward_value -= (alloc.amount - amount) * 0.1 # Waste penalty
                    info["logs"].append(f"Waste: Over-allocated food kits to {zone.name}")
                
                if amount > 0:
                    used_food += amount
                    # Food helps survival, less impact on urgency than ambulances but still positive
                    impact = amount * 0.01 * zone.urgency
                    zone.urgency = max(0.0, zone.urgency - impact)
                    reward_value += (impact * 50.0)
                    info["logs"].append(f"Success: Allocated {amount} food kits to {zone.name}")

        # Finalize resource reduction
        self._observation.resources.ambulances -= used_ambulances
        self._observation.resources.food_kits -= used_food

        # --- Dynamic Urgency Degradation ---
        # In a real disaster, things get worse if not addressed.
        for zone in self._observation.zones:
            if zone.urgency > 0 and zone.urgency < 1.0:
                # Small base increase + dynamic increase based on existing urgency
                degradation = 0.01 + (zone.urgency * 0.02)
                
                # If ambulances were sent to this zone this turn, mitigate degradation
                zone_allocs = [a for a in action.allocations if a.zone == zone.name]
                if any(a.resource == "ambulance" for a in zone_allocs):
                    degradation *= 0.1 # Medical presence significantly slows down worsening
                
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
