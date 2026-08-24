from pydantic import BaseModel, Field


# ========================================
# USER REGISTRATION
# ========================================

class UserCreate(BaseModel):

    username: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    phone_number: str = Field(
        ...,
        min_length=10,
        max_length=15
    )

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )


# ========================================
# USER LOGIN
# ========================================

class UserLogin(BaseModel):

    phone_number: str

    password: str


# ========================================
# USER RESPONSE
# ========================================

class UserResponse(BaseModel):

    id: int

    username: str

    phone_number: str

    class Config:
        from_attributes = True