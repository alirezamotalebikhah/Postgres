from sqlalchemy import create_engine, MetaData, Table, insert, select
import random

engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()
product_table = Table('Product', metadata, autoload_with=engine)

product_names = ["Laptop", "Headphones", "Mouse", "Keyboard", "Monitor", "Tablet", "Speaker", "Charger"]
price_range = [20, 30, 45, 60, 75, 100, 150, 200]

with engine.connect() as connection:
    with connection.begin():
        new_product = {
            "ProductId": 2,
            "Name": random.choice(product_names),
            "Price": random.choice(price_range)
        }
        insert_query = insert(product_table).values(new_product)
        connection.execute(insert_query)

    query = select(product_table.c.ProductId, product_table.c.Name, product_table.c.Price)
    results = connection.execute(query).fetchall()
    results = [
        {"ProductId": row[0], "Name": row[1], "Price": row[2]}
        for row in results
    ]
    print("\nUpdated Product Table:")
    for result in results:
        print(f"ID: {result['ProductId']}, Name: {result['Name']}, Price: {result['Price']}")