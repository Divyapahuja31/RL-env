from typing import List, Literal
from pydantic import BaseModel, Field

class Zone(BaseModel):
    name: str = Field(..., description="Unique name of the disaster zone")
    people: int = Field(..., ge=0, description="Number of people in the zone")
    urgency: float = Field(..., ge=0.0, le=1.0, description="Urgency level between 0 and 1")
