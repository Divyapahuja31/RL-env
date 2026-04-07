# Disaster Response Environment (OpenEnv Spec)

The following methods are implemented to comply with the OpenEnv specification.

## Methods

### `reset(config: dict) -> EnvironmentState`
Initializes the environment state based on the provided configuration dictionary.
- **config**: Dictionary containing `map_size`, `num_agents`, `num_victims`, `num_resources`, and `max_steps`.
- **Returns**: The initial `EnvironmentState`.

### `state() -> EnvironmentState`
Returns the current state of the environment without advancing the simulation.
- **Returns**: Current `EnvironmentState`.

### `step(actions: List[Action]) -> StepResult`
Processes a list of actions (one for each agent) and advances the environment by one time step.
- **actions**: A list of `Action` objects.
- **Returns**: A `StepResult` containing the updated `state`, the `reward` for the step, and the `done` flag.

## Data Models (Pydantic)

### `EnvironmentState`
```python
class EnvironmentState(BaseModel):
    step_count: int
    max_steps: int
    agents: List[Agent]
    victims: List[Victim]
    resources: List[Resource]
    map_size: int
```

### `Action`
```python
class Action(BaseModel):
    agent_id: str
    action_type: Literal["move", "pickup", "dropoff", "treat"]
    target_id: Optional[str] = None
    direction: Optional[Literal["up", "down", "left", "right"]] = None
```
