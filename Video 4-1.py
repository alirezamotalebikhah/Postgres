from sqlalchemy import create_engine, Column, Integer, Date, String, ForeignKey, Table, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import ForeignKeyConstraint
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata = MetaData()
product_table = Table ('Product' , metadata,autoload_with=engine)
with engine.connect() as connection:
    sample_data =[
        {'ProductId': '1' , 'Name' : 'Book' , 'Price':'35'},
        {'ProductId': '2' , 'Name' : 'Notebook' , 'Price':'35'},
        {'ProductId': '3' , 'Name' : 'phone' , 'Price':'35'},
    ]
    connection.execute(product_table.insert(), sample_data)
    connection.commit()
    print("sample data inserted")

