from typing import List, Literal, Annotated
from pydantic import BaseModel, Field, RootModel

class Zone(BaseModel):
    name: str = Field(..., description="Unique name of the disaster zone")
    people: int = Field(..., ge=0, description="Number of people in the zone")
    urgency: float = Field(..., ge=0.0, le=1.0, description="Urgency level between 0 and 1")

class Resources(BaseModel):
    ambulances: int = Field(..., ge=0, description="Available ambulances")
    food_kits: int = Field(..., ge=0, description="Available food kits")

class Observation(BaseModel):
    zones: List[Zone] = Field(..., description="List of all zones and their current state")
    resources: Resources = Field(..., description="Remaining resources available for allocation")
    time_remaining: int = Field(..., ge=0, description="Time steps remaining in the simulation")

class Allocation(BaseModel):
    resource: Literal["ambulance", "food_kits"] = Field(..., description="Type of resource to allocate")
    zone: str = Field(..., description="Target zone name for the allocation")
    amount: int = Field(..., gt=0, description="Amount of resource to allocate")

class Action(BaseModel):
    allocations: List[Allocation] = Field(..., description="List of resource allocations to perform this step")

class Reward(BaseModel):
    value: float = Field(..., description="Numerical reward value for the current step performance")
