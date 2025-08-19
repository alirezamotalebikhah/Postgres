from sqlalchemy import create_engine, MetaData, Table, inspect, select, insert
from sqlalchemy.exc import IntegrityError

# Connect to the database
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()
metadata.reflect(bind=engine)

# Load tables
order_app_table = metadata.tables['OrderApp']

# Step 1: Check Foreign Keys using inspection
inspector = inspect(engine)
fk_constraints = inspector.get_foreign_keys('OrderApp')

print("Foreign Key Constraints in OrderApp:")
for fk in fk_constraints:
    print(f"Constraint Name: {fk['name']}, Referenced Table: {fk['referred_table']}, Columns: {fk['constrained_columns']} -> {fk['referred_columns']}")

# Step 2: Test Foreign Key enforcement with invalid data
with engine.connect() as connection:
    try:
        invalid_order = {"CustomerId": 999, "ProductId": 999, "DateSent": "2025-08-19"}
        connection.execute(order_app_table.insert(), [invalid_order])
        connection.commit()
        print("Invalid data inserted (Foreign Keys not enforced).")
    except IntegrityError as e:
        connection.rollback()
        print(f"Insertion failed with error: {e}. Foreign Keys are enforced.")
    except Exception as e:
        connection.rollback()
        print(f"Unexpected error: {e}")

# Step 3: Display current OrderApp table
with engine.connect() as connection:
    query = select(order_app_table.c.OrderId, order_app_table.c.CustomerId, order_app_table.c.ProductId, order_app_table.c.DateSent)
    results = connection.execute(query).fetchall()
    results = [
        {"OrderId": row[0], "CustomerId": row[1], "ProductId": row[2], "DateSent": row[3]}
        for row in results
    ]

    print("\nCurrent OrderApp Table:")
    for result in results:
        print(f"OrderId: {result['OrderId']}, CustomerId: {result['CustomerId']}, ProductId: {result['ProductId']}, DateSent: {result['DateSent']}")