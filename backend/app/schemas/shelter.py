from pydantic import BaseModel, Field

class ShelterOut(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    max_capacity: int
    occupied_beds: int
    food_days: float
    medical_staff: int
    generator_online: bool
    status: str
    model_config = {"from_attributes": True}

class BroadcastRequest(BaseModel):
    targets: list[str] = Field(min_length=1)
    channels: list[str] = Field(min_length=1)
    message: str = Field(min_length=10, max_length=1000)

class BroadcastOut(BroadcastRequest):
    id: int
    status: str
    dispatched_at: str
