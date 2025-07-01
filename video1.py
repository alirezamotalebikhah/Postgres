from sqlalchemy import create_engine , Column , Integer , Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
Base = declarative_base()
class OrderApp(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    CustomerID = Column(Integer , nullable=False)
    ProductID = Column(Integer , nullable=False)
    DateSent = Column(Date, nullable=False)
Base.metadata.create_all(engine)

#Test
Session = sessionmaker(bind=engine)
session = Session()
print("Table order app create")
session.close()