from sqlalchemy import create_engine, MetaData, Table, select
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')

# Load the Customer table
metadata = MetaData()
customer_table = Table('Customer', metadata, autoload_with=engine)
# Step 3: Run SELECT query and store results in a variable
with engine.connect() as connection:
    query = select(customer_table.c.Name)
    results = connection.execute(query).fetchall()
    results = [
        {"Name": row[0]}
        for row in results
    ]

# Print results
print("\nResults of SELECT query:")
for result in results:
    print(f" Name: {result['Name']}")
with engine.connect() as connection:
    query2 = select(customer_table.c.Name, customer_table.c.Surname)
    results2 = connection.execute(query2).fetchall()
    results2 = [
        {"Name" : row[0] , "Surname" : row[1]}
        for row in results2
    ]
print("\nResults of SELECT query2:")
for result in results2:
    print(f" esm: {result['Name']} , famil: {result['Surname']}")