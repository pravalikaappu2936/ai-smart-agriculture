from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):

    username: str

    phone_number: str = Field(
        ...,
        min_length=10,
        max_length=15
    )

    password: str


class UserLogin(BaseModel):

    phone_number: str

    password: str


class UserResponse(BaseModel):

    id: int
    username: str
    phone_number: str

    model_config = ConfigDict(
        from_attributes=True
    )

