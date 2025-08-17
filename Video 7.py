from sqlalchemy import create_engine, MetaData, Table, select
import random
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()
product_table = Table('Product', metadata, autoload_with=engine)

with engine.connect() as connection:
    query = select(product_table.c.ProductId, product_table.c.Name, product_table.c.Price)
    results = connection.execute(query).fetchall()
    results = [
        {"ProductId": row[0], "Name": row[1], "Price": row[2]}
        for row in results
    ]
    print("\nCurrent Product Table:")
    for result in results:
        print(f"ID: {result['ProductId']}, Name: {result['Name']}, Price: {result['Price']}")
