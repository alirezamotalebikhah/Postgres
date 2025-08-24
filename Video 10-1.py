from sqlalchemy import create_engine , MetaData , Table , Column , Integer , String , Date , ForeignKey , Index , insert , select
from sqlalchemy.engine import row
from sqlalchemy.orm import declarative_base , sessionmaker
from datetime import date
import time
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
Base = declarative_base()
class Customer(Base):
    __tablename__ = 'Customer'
    CustomerId = Column(Integer, primary_key = True , autoincrement = True)
    Name = Column(String(100) , nullable = False)

class Product(Base):
    __tablename__ = 'Product'
    ProductId = Column(Integer, primary_key = True , autoincrement = True)
    Name = Column(String(100) , nullable = False)
    Price = Column(Integer , nullable = False)
    __table_args__ = (
        Index('idx_price' , 'Price'),
    )


class OrderApp(Base):
    __tablename__ = 'OrderApp'
    OrderId = Column(Integer, primary_key = True , autoincrement = True)
    CustomerId = Column(Integer, ForeignKey('Customer.CustomerId') , nullable = False)
    ProductId = Column(Integer, ForeignKey('Product.ProductId') , nullable = False)
    DateSent= Column(Date, nullable = False)

Base.metadata.create_all(engine , checkfirst=True)
Session = sessionmaker(bind=engine)
session = Session()
metadata=MetaData()
metadata.reflect(bind=engine)
customer_table = metadata.tables['Customer']
product_table = metadata.tables['Product']
order_app_table = metadata.tables['OrderApp']
with engine.connect() as connection:
    if not connection.execute(select(customer_table)).fetchone():
        connection.execute(
            insert(customer_table).values([
                {"Name": "Ali"},
                {"Name": "Sara"},
                {"Name": "Reza"},
                {"Name": "Maryam"}
            ])
        )
        connection.commit()
    if not connection.execute(select(product_table)).fetchone():
        connection.execute(
            insert(product_table).values([
                {"Name": "Keyboard", "Price": 45},
                {"Name": "Laptop", "Price": 60},
                {"Name": "Speaker", "Price": 30},
                {"Name": "Headphones", "Price": 45},
                {"Name": "Laptop", "Price": 20}
            ])
        )
        connection.commit()
    if not connection.execute(select(order_app_table)).fetchone():
        connection.execute(
            insert(order_app_table).values([
                {"CustomerId": 1, "ProductId": 2, "DateSent": "2025-08-19"},
                {"CustomerId": 2, "ProductId": 3, "DateSent": "2025-08-19"},
                {"CustomerId": 3, "ProductId": 4, "DateSent": "2025-08-19"},
                {"CustomerId": 4, "ProductId": 5, "DateSent": "2025-08-19"},
                {"CustomerId": 1, "ProductId": 2, "DateSent": "2025-08-19"},
                {"CustomerId": 2, "ProductId": 3, "DateSent": "2025-08-19"},
                {"CustomerId": 3, "ProductId": 4, "DateSent": "2025-08-19"},
                {"CustomerId": 4, "ProductId": 5, "DateSent": "2025-08-19"}
            ])
        )
        connection.commit()
    print("Sample data loaded or already exists.")
with engine.connect() as connection:
    query = select(product_table.c.ProductId , product_table.c.Name , product_table.c.Price).where(
        product_table.c.Price > 40
    )
    results = connection.execute(query).fetchall()
    results = [
        {"ProductId":row[0] , "Name":row[1], "Price":row[2]}
        for row in results
    ]
    print(f"\nQuery Results with Index (as of {date.today()} {time.strftime('%I:%M %p CEST')}:")
    for result in results:
        print(f"ID: {result['ProductId']}, Name: {result['Name']}, Price: {result['Price']}")

# Cleanup session
session.close()