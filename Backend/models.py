from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float, JSON, Table, MetaData, Date



class StickersSteam(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True,autoincrement=True)   
    date_of_scrape = Column(Date)
    name = Column(String)
    price = Column(Float)
    market_listings = Column(Integer)
    sold_in_last_day = Column(Integer)
    capsule_name = Column(String)

class StickersBuff(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True,autoincrement=True)   
    date_of_scrape = Column(Date)
    name = Column(String)
    price = Column(Float)
    market_listings = Column(Integer)


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


Paris_2023 = create_table_model('Steam_market_Paris_2023',StickersSteam)
Rio_2022 = create_table_model('Steam_market_Rio_2022',StickersSteam)
Antwerp_2022 = create_table_model('Steam_market_Antwerp_2022',StickersSteam)
Stockholm_2021 = create_table_model('Steam_market_Stockholm_2021',StickersSteam)
Rmr_2020 = create_table_model('Steam_market_RMR_2020',StickersSteam)

Paris_2023_Buff = create_table_model('Buff_market_Paris_2023',StickersBuff)
Rio_2022_Buff = create_table_model('Buff_market_Rio_2022',StickersBuff)
Antwerp_2022_Buff = create_table_model('Buff_market_Antwerp_2022',StickersBuff)
Stockholm_2021_Buff = create_table_model('Buff_market_Stockholm_2021',StickersBuff)
Rmr_2020_Buff = create_table_model('Buff_market_RMR_2020',StickersBuff)

if __name__ == '__main__':
    pass