# Disaster Response Environment (OpenEnv Spec)

This environment is designed for evaluating strategic resource allocation in disaster scenarios. It follows the OpenEnv specification for reinforcement learning environments.

## Core Concepts

The environment consists of several **Zones**, each with a population count and an **Urgency** level (0.0 to 1.0). The agent's goal is to allocate limited **Resources** (Ambulances and Food Kits) to these zones to reduce urgency and stabilize the situation within a fixed time limit.

## Methods

### `reset(config: dict) -> Observation`
Initializes the environment.
- **config**: Optional dictionary specifying `max_steps`, `resources` (dict), and `zones` (list of dicts).
- **Returns**: The initial `Observation` dictionary.

### `state() -> Observation`
Returns the current state without advancing time.
- **Returns**: Current `Observation`.

### `step(action: Action) -> StepResult`
Advances the simulation by one step.
- **action**: An `Action` object containing a list of `Allocation` requests.
- **Returns**: A dictionary containing:
    - `observation`: The new state.
    - `reward`: Floating point reward for the turn.
    - `done`: Boolean indicating if `time_remaining <= 0`.
    - `info`: Logs and metadata.

## Data Models (Pydantic)

### `Observation`
```python
class Observation(BaseModel):
    zones: List[Zone]
    resources: Resources
    time_remaining: int
```

### `Action`
```python
class Action(BaseModel):
    allocations: List[Allocation]
```

### `Allocation`
```python
class Allocation(BaseModel):
    resource: Literal["ambulance", "food_kits"]
    zone: str
    amount: int
```

## Reward & Penalties
- **Success Reward**: Proportional to `amount * impact * zone.urgency`.
- **Waste Penalty**: Charged when allocating more resources than available.
- **Inactivity Penalty**: Charged if no allocations are made.
- **Dynamic Degradation**: Zones become more urgent over time if left unaddressed.
