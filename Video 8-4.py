from sqlalchemy import create_engine, MetaData, Table, select, join
from datetime import date
import time
import time
t0 = time.perf_counter()

# Connect to the database
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()
metadata.reflect(bind=engine)

# Load tables
customer_table = metadata.tables['Customer']
product_table = metadata.tables['Product']
order_app_table = metadata.tables['OrderApp']

# Step 1: INNER JOIN (Customer and OrderApp)
with engine.connect() as connection:
    inner_join_query = select(
        customer_table.c.CustomerId,
        customer_table.c.Name,
        order_app_table.c.OrderId,
        order_app_table.c.DateSent
    ).select_from(
        join(customer_table, order_app_table, customer_table.c.CustomerId == order_app_table.c.CustomerId)
    )
    inner_results = connection.execute(inner_join_query).fetchall()
    inner_results = [
        {"CustomerId": row[0], "Name": row[1], "OrderId": row[2], "DateSent": row[3]}
        for row in inner_results
    ]
    print(f"\nINNER JOIN Result (Customer and OrderApp) - {date.today()} {time.strftime('%I:%M %p CEST')}:")
    for result in inner_results:
        print(f"CustomerId: {result['CustomerId']}, Name: {result['Name']}, OrderId: {result['OrderId']}, DateSent: {result['DateSent']}")

# Step 2: LEFT OUTER JOIN (Customer and OrderApp)
with engine.connect() as connection:
    left_join_query = select(
        customer_table.c.CustomerId,
        customer_table.c.Name,
        order_app_table.c.OrderId,
        order_app_table.c.DateSent
    ).select_from(
        join(customer_table, order_app_table, customer_table.c.CustomerId == order_app_table.c.CustomerId, isouter=True)
    )
    left_results = connection.execute(left_join_query).fetchall()
    left_results = [
        {"CustomerId": row[0], "Name": row[1], "OrderId": row[2], "DateSent": row[3]}
        for row in left_results
    ]
    print(f"\nLEFT OUTER JOIN Result (Customer and OrderApp) - {date.today()} {time.strftime('%I:%M %p CEST')}:")
    for result in left_results:
        print(f"CustomerId: {result['CustomerId']}, Name: {result['Name']}, OrderId: {result['OrderId']}, DateSent: {result['DateSent']}")

# Step 3: RIGHT OUTER JOIN (Customer and OrderApp)
with engine.connect() as connection:
    right_join_query = select(
        customer_table.c.CustomerId,
        customer_table.c.Name,
        order_app_table.c.OrderId,
        order_app_table.c.DateSent
    ).select_from(
        join(customer_table, order_app_table, customer_table.c.CustomerId == order_app_table.c.CustomerId, isouter=True, full=False)
    ).select_from(
        order_app_table
    )  # Note: PostgreSQL doesn't support RIGHT JOIN directly, simulated with LEFT JOIN reversal
    right_results = connection.execute(right_join_query).fetchall()
    right_results = [
        {"CustomerId": row[0], "Name": row[1], "OrderId": row[2], "DateSent": row[3]}
        for row in right_results
    ]
    print(f"\nRIGHT OUTER JOIN Result (Customer and OrderApp) - {date.today()} {time.strftime('%I:%M %p CEST')}:")
    for result in right_results:
        print(f"CustomerId: {result['CustomerId']}, Name: {result['Name']}, OrderId: {result['OrderId']}, DateSent: {result['DateSent']}")

# Step 4: FULL OUTER JOIN (Customer and OrderApp)
with engine.connect() as connection:
    full_join_query = select(
        customer_table.c.CustomerId,
        customer_table.c.Name,
        order_app_table.c.OrderId,
        order_app_table.c.DateSent
    ).select_from(
        join(customer_table, order_app_table, customer_table.c.CustomerId == order_app_table.c.CustomerId, isouter=True, full=True)
    )
    full_results = connection.execute(full_join_query).fetchall()
    full_results = [
        {"CustomerId": row[0], "Name": row[1], "OrderId": row[2], "DateSent": row[3]}
        for row in full_results
    ]
    print(f"\nFULL OUTER JOIN Result (Customer and OrderApp) - {date.today()} {time.strftime('%I:%M %p CEST')}:")
    for result in full_results:
        print(f"CustomerId: {result['CustomerId']}, Name: {result['Name']}, OrderId: {result['OrderId']}, DateSent: {result['DateSent']}")
print(f"runtime:{time.perf_counter() - t0:.3f} seconds")