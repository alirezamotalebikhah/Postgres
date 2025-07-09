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
    query = select(customer_table.c.Name, customer_table.c.Surname)
    results = connection.execute(query).fetchall()
    results = [
        {"Name" : row[0] , "Surname" : row[1]}
        for row in results
    ]
print("\nResults of SELECT query:")
if any(row["Name"] in {"Sara" , "Reza"} for row in results):
    for result in results:
        print(f" esm: {result['Name']} , famil: {result['Surname']}")
target_names = {"Sara", "Reza"}

filtered_results = [
    result for result in results
    if result["Name"] in target_names
]

print("\nFAMILY of Sara and Reza:")
for result in filtered_results:
    print(f"famil: {result['Surname']}")
