from typing import List, Literal
from pydantic import BaseModel, Field

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
