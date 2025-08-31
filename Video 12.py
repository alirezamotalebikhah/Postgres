from sqlalchemy import create_engine, MetaData, Table, select, inspect

# Connect to the database
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()
inspector = inspect(engine)

# Define your 3 main tables
table_names = ['Customer', 'Product', 'OrderApp']

print("Database Tables and Contents:")
print("=" * 50)

with engine.connect() as connection:
    for table_name in table_names:
        print(f"\n--- TABLE: {table_name} ---")
        
        # Load each table
        table = Table(table_name, metadata, autoload_with=engine)
        
        # Get column names
        column_names = [col.name for col in table.columns]
        
        # Create select query with all columns explicitly like your example
        query = select(*[table.c[col] for col in column_names])
        result = connection.execute(query).fetchall()
        
        # Convert results to list of dictionaries exactly like your example
        result = [
            {column_names[i]: row[i] for i in range(len(column_names))}
            for row in result
        ]
        
        print(f"\n{table_name} Table:")
        for row in result:
            row_display = ", ".join([f"{key}: {value}" for key, value in row.items()])
            print(f"{row_display}")
        
        # Clear metadata to avoid conflicts with next table
        metadata.clear()

print("\n" + "=" * 50)
print("All tables displayed successfully!")