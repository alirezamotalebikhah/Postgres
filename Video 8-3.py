from sqlalchemy import create_engine, MetaData, Table, insert, select
from datetime import date
import time

# Connect to the database
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()
metadata.reflect(bind=engine)

# Load tables
order_app_table = metadata.tables['OrderApp']

# Step 1: Add sample data to OrderApp
with engine.connect() as connection:
    sample_orders = [
        {"CustomerId": 1, "ProductId": 2, "DateSent": "2025-08-19"},  # Ali buys Keyboard
        {"CustomerId": 2, "ProductId": 3, "DateSent": "2025-08-19"},  # Sara buys Laptop
        {"CustomerId": 3, "ProductId": 4, "DateSent": "2025-08-19"},  # Reza buys Speaker
        {"CustomerId": 4, "ProductId": 5, "DateSent": "2025-08-19"},  # Maryam buys Headphones
    ]
    connection.execute(
        insert(order_app_table).values(sample_orders)
    )
    connection.commit()
    print("Sample orders added to OrderApp table.")

# Step 2: Display OrderApp table
with engine.connect() as connection:
    query = select(order_app_table.c.OrderId, order_app_table.c.CustomerId, order_app_table.c.ProductId, order_app_table.c.DateSent)
    results = connection.execute(query).fetchall()
    results = [
        {"OrderId": row[0], "CustomerId": row[1], "ProductId": row[2], "DateSent": row[3]}
        for row in results
    ]
    print(f"\nUpdated OrderApp Table (as of {date.today()} {time.strftime('%I:%M %p CEST')}:")
    for result in results:
        print(f"ID: {result['OrderId']}, CustomerId: {result['CustomerId']}, ProductId: {result['ProductId']}, DateSent: {result['DateSent']}")