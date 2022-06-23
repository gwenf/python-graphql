import email
from typing import List

from fastapi import FastAPI
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
import strawberry
from strawberry.fastapi import GraphQLRouter

from db.db_setup import get_db
from db.models.user import User as UserModel
from db.models.company import Company as CompanyModel
from db.pydantic_schemas.user import User, UserCreate
from db.pydantic_schemas.company import Company

app = FastAPI()


@app.get("/ping")
async def root():
    return {"message": "pong"}


#####
# Rest API
#####


@app.get("/users", response_model=List[User])
async def get_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@app.post("/users", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Email is already registered"
        )

    db_user = UserModel(
        email=user.email, role=user.role, company=user.company_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{id}", response_model=User)
async def get_user(user_id, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    return user


@app.get("/users/{id}/company", response_model=Company)
async def get_users_company(company_id, db: Session = Depends(get_db)):
    company = (
        db.query(CompanyModel)
        .filter(CompanyModel.user.id == company_id)
        .first()
    )
    return company


#####
# Graphql API
#####


@strawberry.type
class User:
    email: str
    role: str


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"


schema = strawberry.Schema(Query)

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")
