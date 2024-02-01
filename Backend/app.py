from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from database import SessionLocal, engine
import models

class StickersBase(BaseModel):
    name: str
    href_link: str

class StickerModel(StickersBase):
    id: int
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#async def lifespan(app: FastAPI):
#    models.Base.metadata.create_all(engine)
    

app = FastAPI()
origins = [
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)
models.Base.metadata.create_all(engine)
