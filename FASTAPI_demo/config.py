from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_url="postgresql://postgres:Sakshika2002@@localhost:5432/fastapiDemo"
engine=create_engine(db_url)
session=sessionmaker(autoflush=False,autocommit=False,bind=engine)