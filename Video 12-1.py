from sqlalchemy import create_engine, MetaData, Table, select, text

# Connect to the database
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()

# Load Product table
product_table = Table('Product', metadata, autoload_with=engine)

with engine.connect() as connection:
    # First, show current Product table
    query = select(product_table.c.ProductId, product_table.c.Name, product_table.c.Price)
    result = connection.execute(query).fetchall()
    result = [
        {"ProductId": row[0], "Name": row[1], "Price": row[2]}
        for row in result
    ]
    
    print("Product Table Before Adding Duplicates:")
    for row in result:
        print(f"ID: {row['ProductId']}, Name: {row['Name']}, Price: {row['Price']}")
    
    # Create duplicates from existing products (take first few products and duplicate them)
    if result:
        duplicate_products = []
        for i in range(min(2, len(result))):  # Duplicate first 2 products
            duplicate_products.append({
                "Name": result[i]["Name"],
                "Price": result[i]["Price"]
            })
        
        # Fix sequence value to avoid primary key conflicts
        max_id_query = select(product_table.c.ProductId).order_by(product_table.c.ProductId.desc()).limit(1)
        max_id_result = connection.execute(max_id_query).fetchone()
        if max_id_result:
            max_id = max_id_result[0]
            # Reset the sequence to the correct value
            connection.execute(text(f"SELECT setval('\"Product_ProductId_seq\"', {max_id})"))
        
        connection.execute(product_table.insert().values(duplicate_products))
        connection.commit()
        print(f"\nDuplicated {len(duplicate_products)} existing products.")
    
    # Show Product table after adding duplicates
    query = select(product_table.c.ProductId, product_table.c.Name, product_table.c.Price)
    result = connection.execute(query).fetchall()
    result = [
        {"ProductId": row[0], "Name": row[1], "Price": row[2]}
        for row in result
    ]
    
    print("\nProduct Table After Adding Duplicates:")
    for row in result:
        print(f"ID: {row['ProductId']}, Name: {row['Name']}, Price: {row['Price']}")