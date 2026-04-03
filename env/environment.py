from typing import List, Dict, Any
from .models import Zone, Resources, Observation, Allocation, Action, Reward, StepResult

class DisasterEnv:
    """Disaster Response OpenEnv environment."""
    def __init__(self):
        self._observation: Observation = None
        self._max_steps = 5
