from typing import List, Dict, Any
from .models import Zone, Resources, Observation, Allocation, Action, Reward, StepResult

class DisasterEnv:
    """Disaster Response OpenEnv environment."""
    def __init__(self):
        self._observation: Observation = None
        self._max_steps = 5

    def reset(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Initializes the environment. Accepts optional config for task scenarios."""
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
        """Returns the current environment state."""
        if self._observation is None:
            raise ValueError("Environment not reset.")
        return self._observation.model_dump()

    def step(self, action: Action) -> Dict[str, Any]:
        """Processes allocations and returns step results."""
        if self._observation is None:
            raise ValueError("Environment not reset.")

        reward_value = 0.0
        info = {"logs": []}

        for alloc in action.allocations:
            zone = next((z for z in self._observation.zones if z.name == alloc.zone), None)
            if not zone:
                reward_value -= 1.0
                info["logs"].append(f"Penalty: Invalid zone {alloc.zone}")
                continue

        self._observation.time_remaining -= 1
        done = self._observation.time_remaining <= 0

        return {
            "observation": self._observation.model_dump(),
            "reward": reward_value,
            "done": done,
            "info": info
        }
