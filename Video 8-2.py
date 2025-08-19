from sqlalchemy import create_engine, MetaData, Table, select
from datetime import date
import time

# Connect to the database
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()
metadata.reflect(bind=engine)

# Load tables
customer_table = metadata.tables['Customer']
product_table = metadata.tables['Product']

# Step 1: Display Customer table
with engine.connect() as connection:
    query = select(customer_table.c.CustomerId, customer_table.c.Name)
    results = connection.execute(query).fetchall()
    results = [
        {"CustomerId": row[0], "Name": row[1]}
        for row in results
    ]
    print(f"\nUpdated Customer Table (as of {date.today()} {time.strftime('%I:%M %p CEST')}:")
    for result in results:
        print(f"ID: {result['CustomerId']}, Name: {result['Name']}")

# Step 2: Display Product table
with engine.connect() as connection:
    query = select(product_table.c.ProductId, product_table.c.Name, product_table.c.Price)
    results = connection.execute(query).fetchall()
    results = [
        {"ProductId": row[0], "Name": row[1], "Price": row[2]}
        for row in results
    ]
    print(f"\nUpdated Product Table (as of {date.today()} {time.strftime('%I:%M %p CEST')}:")
    for result in results:
        print(f"ID: {result['ProductId']}, Name: {result['Name']}, Price: {result['Price']}")