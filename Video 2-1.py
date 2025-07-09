from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.sql import text

# Connect to the database
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')

# Load the Customer table
metadata = MetaData()
customer_table = Table('Customer', metadata, autoload_with=engine)

# Step 1: Add the Surname column if it doesn't exist
with engine.connect() as connection:
    if 'Surname' not in customer_table.c:
        connection.execute(
            text('ALTER TABLE "Customer" ADD COLUMN "Surname" VARCHAR(100) NOT NULL DEFAULT :default_value'),
            {"default_value": ""}
        )
        connection.commit()
        print("Surname column added to Customer table.")
    else:
        print("Surname column already exists.")

# Step 2: Populate or update the Customer table with sample data
with engine.connect() as connection:
    # Check if the table is empty
    result = connection.execute(customer_table.select().limit(1)).fetchone()
    if not result:
        sample_data = [
            {"Name": "Ali", "Surname": "Mohammadi"},
            {"Name": "Sara", "Surname": "Ahmadi"},
            {"Name": "Reza", "Surname": "Rezaei"},
            {"Name": "Maryam", "Surname": "Karimi"}
        ]
        connection.execute(customer_table.insert(), sample_data)
        connection.commit()
        print("Sample data added to Customer table.")
    else:
        # Update existing records with specific Surname values based on Name
        existing_customers = connection.execute(customer_table.select()).fetchall()
        surname_updates = {
            "Ali": "Mohammadi",
            "Sara": "Ahmadi",
            "Reza": "Rezaei",
            "Maryam": "Karimi"
        }
        for customer in existing_customers:
            customer_id = customer[0]  # CustomerId
            name = customer[1]  # Name
            new_surname = surname_updates.get(name, "Unknown")
            connection.execute(
                customer_table.update()
                .where(customer_table.c.CustomerId == customer_id)
                .values(Surname=new_surname)
            )
        connection.commit()
        print("Existing Customer records updated with specific Surnames.")

# Step 3: Run SELECT query and store results in a variable
with engine.connect() as connection:
    query = select(customer_table.c.CustomerId, customer_table.c.Name, customer_table.c.Surname)
    results = connection.execute(query).fetchall()
    results = [
        {"CustomerId": row[0], "Name": row[1], "Surname": row[2]}
        for row in results
    ]

# Print results
print("\nResults of SELECT query:")
for result in results:
    print(f"ID: {result['CustomerId']}, Name: {result['Name']}, Surname: {result['Surname']}")