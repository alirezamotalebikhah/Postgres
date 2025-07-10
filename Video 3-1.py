from sqlalchemy import create_engine, MetaData , Table , select
from sqlalchemy.sql.expression import func


engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()
customer_table = Table('Customer' , metadata , autoload_with=engine)
with engine.connect() as connection:
    query_ends_with_a = select(customer_table.c.Name).where(customer_table.c.Name.like('%a'))
    result_end_with_a = connection.execute(query_ends_with_a).fetchall()
    result_end_with_a =[
        {"Name" : row[0]}
        for row in result_end_with_a
    ]
    query_contains_z = select(customer_table.c.Name.like('%z%'))
    result_contains_z = connection.execute(query_contains_z).fetchall()
    result_contains_z=[
        {"Name" : row[0]}
        for row in result_contains_z
    ]
    query_start_with_m = select(customer_table.c.Name).where(func.lower(customer_table.c.Name).like('m%'))
    result_start_with_m = connection.execute(query_start_with_m).fetchall()
    result_start_with_m =[
        {"Name":row[0]}
        for row in result_start_with_m
    ]
print("\nQuery1 : end with a")
for result in result_end_with_a:
    print(f"Name:{result['Name']}")
print("\nQuery2 : contains with z")
for result in result_contains_z:
    print(f"Name:{result['Name']}")
print("\nQuery3 : start with m")
for result in result_start_with_m:
    print(f"Name:{result['Name']}")
