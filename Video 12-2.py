from sqlalchemy import create_engine, MetaData, Table, select, func, case

# Connect to the database
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()

# Load Product table
product_table = Table('Product', metadata, autoload_with=engine)

with engine.connect() as connection:
    print("=== Original Product Table ===")
    # Show original table
    query = select(product_table.c.ProductId, product_table.c.Name, product_table.c.Price)
    result = connection.execute(query).fetchall()
    
    for row in result:
        print(f"ID: {row[0]}, Name: {row[1]}, Price: {row[2]}")
    
    print("\n=== GROUP BY Name - Count and Average Price ===")
    # Group by product name, count occurrences and calculate average price
    group_query = select(
        product_table.c.Name,
        func.count(product_table.c.ProductId).label('count'),
        func.avg(product_table.c.Price).label('avg_price'),
        func.min(product_table.c.Price).label('min_price'),
        func.max(product_table.c.Price).label('max_price')
    ).group_by(product_table.c.Name)
    
    group_result = connection.execute(group_query).fetchall()
    
    for row in group_result:
        print(f"Name: {row[0]}, Count: {row[1]}, Avg Price: ${row[2]:.2f}, Min: ${row[3]}, Max: ${row[4]}")
    
    print("\n=== GROUP BY Price Range - Count Products ===")
    # Group by price ranges
    price_range_query = select(
        case(
            (product_table.c.Price < 30, 'Low (< $30)'),
            (product_table.c.Price.between(30, 50), 'Medium ($30-$50)'),
            else_='High (> $50)'
        ).label('price_range'),
        func.count(product_table.c.ProductId).label('product_count'),
        func.avg(product_table.c.Price).label('avg_price')
    ).group_by(
        case(
            (product_table.c.Price < 30, 'Low (< $30)'),
            (product_table.c.Price.between(30, 50), 'Medium ($30-$50)'),
            else_='High (> $50)'
        )
    )
    
    price_range_result = connection.execute(price_range_query).fetchall()
    
    for row in price_range_result:
        print(f"Price Range: {row[0]}, Product Count: {row[1]}, Avg Price: ${row[2]:.2f}")
    
    print("\n=== Products with Duplicates (HAVING count > 1) ===")
    # Show only products that have duplicates using HAVING clause
    duplicates_query = select(
        product_table.c.Name,
        func.count(product_table.c.ProductId).label('count'),
        func.min(product_table.c.ProductId).label('first_id'),
        func.max(product_table.c.ProductId).label('last_id')
    ).group_by(product_table.c.Name).having(func.count(product_table.c.ProductId) > 1)
    
    duplicates_result = connection.execute(duplicates_query).fetchall()
    
    if duplicates_result:
        for row in duplicates_result:
            print(f"Duplicate Name: {row[0]}, Count: {row[1]}, ID Range: {row[2]}-{row[3]}")
    else:
        print("No duplicate products found.")