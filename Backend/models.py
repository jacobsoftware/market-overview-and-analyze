from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float, JSON, Table, MetaData



class Stickers(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True,autoincrement=True)   
    date = Column(String)
    name = Column(String)
    price = Column(Float)
    market_volume = Column(Integer)
    sold_in_last_day = Column(Integer)

class StickersHref(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String)
    link = Column(String)  

def create_stickers_model(name,data_class):
    tablename = name
    class_name = f'Class{name}'
    Model = type(class_name,(data_class,),{
        '__tablename__':tablename
        
    })
    return Model


Paris_2023 = create_stickers_model('Paris_2023',Stickers)
Rio_2022 = create_stickers_model('Rio_2022',Stickers)
Antwerp_2022 = create_stickers_model('Antwerp_2022',Stickers)
Stockholm_2021 = create_stickers_model('Stockholm_2021',Stickers)
Rmr_2020 = create_stickers_model('RMR_2020',Stickers)

if __name__ == '__main__':
    pass