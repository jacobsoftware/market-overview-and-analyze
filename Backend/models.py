from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float



class Stickers(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String)
    href_link = Column(String)

def create_stickers_model(name):
    tablename = name
    class_name = f'class{name}'
    Model = type(class_name,(Stickers,),{
        '__tablename__':tablename
    })



paris_2023 = create_stickers_model('Paris_2023')
rio_2022 = create_stickers_model('Rio_2022')
antwerp_2022 = create_stickers_model('Antwerp_2022')
stockholm_2021 = create_stickers_model('Stockholm_2021')
rmr_2020 = create_stickers_model('RMR_2020')
