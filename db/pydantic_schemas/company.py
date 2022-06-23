from pydantic import BaseModel


class Company(BaseModel):
    name: str
    website: str

    class Config:
        orm_mode = True
