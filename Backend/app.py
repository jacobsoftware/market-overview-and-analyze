from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import asyncio
from datetime import date

from database import SessionLocal, engine
import models


class StickersBase(BaseModel):
    date_of_scrape: str
    name: str
    price: float
    market_listings: int
    sold_in_last_day: int
    capsule_name: str



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

    

app = FastAPI()
models.Base.metadata.create_all(engine)
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

@app.get('/')
def home():
    return {'Info':'Nothing is going here.'}

if __name__ == '__main__':
    def realease(db: db_dependency):
        data = {'date': str(date.today()), 'name': 'Sticker', 'price': 13.99, 'market_volume': 150,'sold_in_last_day':140}
        db_data = models.Katowice_2014(**data)
        db.add(db_data)
        db.commit
        db.refresh(db_data)
        print(db_data)
    realease()

