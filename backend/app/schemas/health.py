from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    application: str
    environment: str
    database: str
    hindsight: str
