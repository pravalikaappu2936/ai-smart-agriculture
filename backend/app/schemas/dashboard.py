from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_users: int
    total_predictions: int