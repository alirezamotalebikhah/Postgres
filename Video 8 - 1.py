from sqlalchemy import select , create_engine, MetaData, Table, Column,String, Integer, Date, ForeignKey
from sqlalchemy.orm import declarative_base

# Connect to the database
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')

# Define declarative base
Base = declarative_base()

# Define models with Foreign Keys
class OrderApp(Base):
    __tablename__ = 'OrderApp'
    OrderId = Column(Integer, primary_key=True, autoincrement=True)
    CustomerId = Column(Integer, ForeignKey('Customer.CustomerId'), nullable=False)
    ProductId = Column(Integer, ForeignKey('Product.ProductId'), nullable=False)
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

# Recreate tables with relations
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Display result
metadata = MetaData()
metadata.reflect(bind=engine)
order_app_table = metadata.tables['OrderApp']

with engine.connect() as connection:
    query = select(order_app_table.c.OrderId, order_app_table.c.CustomerId, order_app_table.c.ProductId, order_app_table.c.DateSent)
    results = connection.execute(query).fetchall()
    results = [
        {"OrderId": row[0], "CustomerId": row[1], "ProductId": row[2], "DateSent": row[3]}
        for row in results
    ]

    print("\nCurrent OrderApp Table (after recreate):")
    for result in results:
        print(f"OrderId: {result['OrderId']}, CustomerId: {result['CustomerId']}, ProductId: {result['ProductId']}, DateSent: {result['DateSent']}")

# Test Foreign Key enforcement
with engine.connect() as connection:
    try:
        invalid_order = {"CustomerId": 999, "ProductId": 999, "DateSent": "2025-08-19"}
        connection.execute(order_app_table.insert(), [invalid_order])
        connection.commit()
        print("Invalid data inserted (Foreign Keys not enforced).")
    except Exception as e:
        connection.rollback()
        print(f"Insertion failed with error: {e}. Foreign Keys are enforced.")