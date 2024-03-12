from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float, JSON, Table, MetaData, Date



class Stickers(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True,autoincrement=True)   
    date_of_scrape = Column(Date)
    name = Column(String)
    price = Column(Float)
    market_listings = Column(Integer)
    sold_in_last_day = Column(Integer)
    capsule_name = Column(String)

class Capsules(Base):
    __tablename__ = 'Steam_market_capsules'

    id = Column(Integer, primary_key=True,autoincrement=True)   
    date_of_scrape = Column(Date)
    name = Column(String)
    price = Column(Float)
    market_listings = Column(Integer)
    sold_in_last_day = Column(Integer)

class StickersHref(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String)
    link = Column(String)  

def create_table_model(name,data_class):
    tablename = name
    class_name = f'Class{name}'
    Model = type(class_name,(data_class,),{
        '__tablename__':tablename
        
    })
    return Model


Paris_2023 = create_table_model('Steam_market_Paris_2023',Stickers)
Rio_2022 = create_table_model('Steam_market_Rio_2022',Stickers)
Antwerp_2022 = create_table_model('Steam_market_Antwerp_2022',Stickers)
Stockholm_2021 = create_table_model('Steam_market_Stockholm_2021',Stickers)
Rmr_2020 = create_table_model('Steam_market_RMR_2020',Stickers)
if __name__ == '__main__':
    pass