from sqlalchemy import create_engine, MetaData, Table, select

# Connect to the database
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')

# Load the Product table
metadata = MetaData()
product_table = Table('Product', metadata, autoload_with=engine)

# Step 1: Query 1 - Display full table sorted ascending by Price
with engine.connect() as connection:
    query_1 = select(product_table.c.ProductId, product_table.c.Name, product_table.c.Price).order_by(product_table.c.Price.asc())
    results_1 = connection.execute(query_1).fetchall()
    results_1 = [
        {"ProductId": row[0], "Name": row[1], "Price": row[2]}
        for row in results_1
    ]

    print("\nQuery 1: Full table sorted ascending by Price:")
    for result in results_1:
        print(f"ID: {result['ProductId']}, Name: {result['Name']}, Price: {result['Price']}")

# Step 2: Query 2 - Display top 2 records sorted ascending by Name
with engine.connect() as connection:
    query_2 = select(product_table.c.ProductId, product_table.c.Name, product_table.c.Price).order_by(product_table.c.Name.asc()).limit(2)
    results_2 = connection.execute(query_2).fetchall()
    results_2 = [
        {"ProductId": row[0], "Name": row[1], "Price": row[2]}
        for row in results_2
    ]

    print("\nQuery 2: Top 2 records sorted ascending by Name:")
    for result in results_2:
        print(f"ID: {result['ProductId']}, Name: {result['Name']}, Price: {result['Price']}")

# Step 3: Query 3 - Update Price for Notebook to 40 and phone to 50, then display updated table
with engine.connect() as connection:
    # Update Price values
    connection.execute(
        product_table.update()
        .where(product_table.c.Name == 'Notebook')
        .values(Price=40)
    )
    connection.execute(
        product_table.update()
        .where(product_table.c.Name == 'phone')
        .values(Price=50)
    )
    connection.commit()

    # Display updated table
    query_3 = select(product_table.c.ProductId, product_table.c.Name, product_table.c.Price).order_by(product_table.c.Price.asc())
    results_3 = connection.execute(query_3).fetchall()
    results_3 = [
        {"ProductId": row[0], "Name": row[1], "Price": row[2]}
        for row in results_3
    ]

    print("\nQuery 3: Updated table sorted ascending by Price:")
    for result in results_3:
        print(f"ID: {result['ProductId']}, Name: {result['Name']}, Price: {result['Price']}")