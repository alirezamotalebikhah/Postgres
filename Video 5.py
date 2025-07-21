

from sqlalchemy import create_engine , MetaData , Table , select , delete
from sqlalchemy.engine import row

engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()
customer_table = Table('Customer', metadata,autoload_with=engine)
with engine.connect() as connection:
    connection.execute(customer_table.delete().where(customer_table.c.Name == 'Ali')
                       )
    connection.commit()
    print("User with Name 'Ali' was deleted")
    query = select(customer_table.c.CustomerId , customer_table.c.Name , customer_table.c.Surname).order_by(customer_table.c.CustomerId.asc())
    result = connection.execute(query).fetchall()
    result=[
        {"CustomerID":row[0], "Name":row[1], "Surname":row[2]}
        for row in result
    ]
    print("\n Table after Delet")
    for result in result:
        print(f"ID: {result['CustomerID']} , Name: {result['Name']} , Surname: {result['Surname']}")
with engine.connect() as connection:
    new_data = {"Name":"Ali","Surname":"Mohammadi"}
    connection.execute(customer_table.insert() , [new_data])
    connection.commit()
    print("User with Name 'Ali' was inserted")
    query = select(customer_table.c.CustomerId , customer_table.c.Name , customer_table.c.Surname).order_by(customer_table.c.CustomerId.asc())
    result = connection.execute(query).fetchall()
    result=[
        {"CustomerID":row[0] , "Name":row[1] , "Surname":row[2]}
        for row in result
    ]
    print("\n Table after Insert")
    for result in result:
        print(f"ID:{result['CustomerID']} , Name:{result['Name']} , Surname: {result['Surname']}")