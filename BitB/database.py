from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#if not database_exists(engine.url):
#    print('Database exists: False')
#    create_database(engine.url)
#print(f'Database exists: {database_exists(engine.url)}')


Base = declarative_base()

class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50),unique=True, index=True, nullable=False)
    airport = Column(String(4), default='CYVR')
    radius = Column(Integer, default=10)
    webcams = Column(Boolean, default=False)

SQLALCHEMY_DB_URI = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DB_URI, echo=True)
Base.metadata.create_all(engine)


session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
