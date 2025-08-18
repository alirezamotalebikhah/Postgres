from sqlalchemy import create_engine, MetaData, Table, select , insert
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
product_names = ["Laptop", "Headphones", "Mouse", "Keyboard", "Monitor", "Tablet", "Speaker", "Charger"]
price_range = [20, 30, 45, 60, 75, 100, 150, 200]

with engine.connect() as connection:
    with connection.begin():
        max_id_query = select(product_table.c.ProductId).order_by(product_table.c.ProductId.desc()).limit(1)
        max_id_result = connection.execute(max_id_query).fetchone()

        max_id = 0
        if max_id_result and max_id_result[0] is not None:
            max_id = int(max_id_result[0])

        for i in range(4):
            new_id = max_id + i + 1
            new_product = {
                "ProductId": new_id,
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
