from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

from config import dbengine

Base=declarative_base()

class User(Base):
	__tablename__='users'
	id=Column(Integer,primary_key=True)
	name=Column(String,unique=True)
	password=Column(String)
	creator=Column(Integer,nullable=True)

class Item(Base):
	__tablename__='items'
	id=Column(Integer,primary_key=True)
	name=Column(String)
	price=Column(Integer)

class Sale(Base):
	__tablename__='sales'
	id=Column(Integer,primary_key=True)
	user_id=Column(Integer,ForeignKey('users.id'))
	item_id=Column(Integer,ForeignKey('items.id'))
	amount=Column(Integer)
	time=Column(DateTime, default=func.now())
	user=relationship('User')
	item=relationship('Item')

class Pay(Base):
	__tablename__='pays'
	id=Column(Integer,primary_key=True)
	user_id=Column(Integer,ForeignKey('users.id'))
	amount=Column(Integer)
	time=Column(DateTime, default=func.now())
	user=relationship('User')

__engine=create_engine(dbengine)
Base.metadata.create_all(__engine)
Session=sessionmaker(bind=__engine)
