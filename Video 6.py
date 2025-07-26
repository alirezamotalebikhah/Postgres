from sqlalchemy import create_engine , MetaData , Table , select , delete
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
metadata=MetaData()
product_table=Table('Product',metadata,autoload_with=engine)
with engine.connect() as connection:
    connection.execute(product_table.delete().where(product_table.c.Name.like('%N%')))
    connection.commit()
    query=select(product_table.c.ProductId,product_table.c.Name,product_table.c.Price)
    result=connection.execute(query).fetchall()
    result = [
        {"ProductId": row[0], "Name": row[1], "Price": row[2]}
        for row in result
    ]
    print("\n Table after Delet")
    for result in result:
        print(f"ID: {result['ProductId']} , Name: {result['Name']} , Price: {result['Price']}")


