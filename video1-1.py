from sqlalchemy import create_engine, Column, Integer, Date, String, ForeignKey, Table, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import ForeignKeyConstraint

engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')

Base = declarative_base()

class OrderApp(Base):
    __tablename__ = 'OrderApp'
    OrderId = Column(Integer, primary_key=True, autoincrement=True)
    CustomerId = Column(Integer, nullable=False)
    ProductId = Column(Integer, nullable=False)
    DateSent = Column(Date, nullable=False)

class Product(Base):
    __tablename__ = 'Product'
    ProductId = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100), nullable=False)
    Price = Column(Integer, nullable=False)

class Customer(Base):
    __tablename__ = 'Customer'
    CustomerId = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100), nullable=False)

Base.metadata.create_all(engine)

metadata = MetaData()
metadata.reflect(bind=engine)
order_app_table = metadata.tables['OrderApp']

order_app_table.append_constraint(ForeignKeyConstraint(['CustomerId'], ['Customer.CustomerId'], name='fk_customer', deferrable=True, initially='DEFERRED'))
order_app_table.append_constraint(ForeignKeyConstraint(['ProductId'], ['Product.ProductId'], name='fk_product', deferrable=True, initially='DEFERRED'))

with engine.connect() as connection:
    order_app_table.create(connection, checkfirst=True)
    connection.commit()

Session = sessionmaker(bind=engine)
session = Session()
print("Tables and relations created successfully.")
session.close()