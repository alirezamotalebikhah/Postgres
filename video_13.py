from sqlalchemy import create_engine, Column, Integer, String, Sequence, text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

user_id_seq = Sequence('user_id_seq', start=1000, increment=5)
order_id_seq = Sequence('order_id_seq', start=5000, increment=1)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, user_id_seq, primary_key=True, server_default=user_id_seq.next_value())
    name = Column(String(50))
    email = Column(String(100))

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, order_id_seq, primary_key=True, server_default=order_id_seq.next_value())
    user_id = Column(Integer)
    product_name = Column(String(100))
    amount = Column(Integer)

engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase', echo=True)

print("Creating sequences and tables...")
with engine.connect() as conn:
    conn.execute(text("DROP SEQUENCE IF EXISTS user_id_seq CASCADE"))
    conn.execute(text("DROP SEQUENCE IF EXISTS order_id_seq CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS orders CASCADE"))
    conn.commit()

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

print("\nCreating users with sequence-generated IDs:")
users_data = [
    ('Alice Johnson', 'alice@company.com'),
    ('Bob Smith', 'bob@company.com'),
    ('Carol Williams', 'carol@company.com'),
    ('David Brown', 'david@company.com')
]

users = []
for name, email in users_data:
    user = User(name=name, email=email)
    session.add(user)
    session.flush()
    users.append(user)
    print(f"  Created user: {user.name} with ID: {user.id}")

print("\nCreating orders with sequence-generated IDs:")
orders_data = [
    (users[0].id, 'Laptop Pro', 1299),
    (users[0].id, 'Wireless Mouse', 45),
    (users[1].id, 'Mechanical Keyboard', 120),
    (users[2].id, 'Monitor 27inch', 350),
    (users[2].id, 'USB-C Hub', 89),
    (users[3].id, 'Webcam HD', 75)
]

orders = []
for user_id, product_name, amount in orders_data:
    order = Order(user_id=user_id, product_name=product_name, amount=amount)
    session.add(order)
    session.flush()
    orders.append(order)
    print(f"  Created order: {order.product_name} for user {order.user_id} with Order ID: {order.id}")

session.commit()

print("\n" + "="*50)
print("FINAL DATABASE CONTENT:")
print("="*50)

print("\nUsers in database:")
for user in session.query(User).all():
    print(f"  ID: {user.id:4d} | Name: {user.name:15s} | Email: {user.email}")

print("\nOrders in database:")
for order in session.query(Order).all():
    print(f"  Order ID: {order.id:4d} | User ID: {order.user_id:4d} | Product: {order.product_name:20s} | Amount: ${order.amount}")

print("\nSequence Information:")
user_seq_val = session.execute(text("SELECT currval('user_id_seq')")).scalar()
order_seq_val = session.execute(text("SELECT currval('order_id_seq')")).scalar()
print(f"  Current user_id_seq value: {user_seq_val}")
print(f"  Current order_id_seq value: {order_seq_val}")

print(f"\n  Next user_id_seq value will be: {user_seq_val + 5}")
print(f"  Next order_id_seq value will be: {order_seq_val + 1}")

print("\nSequence Details:")
seq_info = session.execute(text("""
    SELECT sequence_name, start_value, increment
    FROM information_schema.sequences 
    WHERE sequence_name IN ('user_id_seq', 'order_id_seq')
    ORDER BY sequence_name
""")).fetchall()

for seq in seq_info:
    print(f"  {seq[0]}: start={seq[1]}, increment={seq[2]}")

print(f"\nDemonstrating nextval() function:")
next_user_id = session.execute(text("SELECT nextval('user_id_seq')")).scalar()
next_order_id = session.execute(text("SELECT nextval('order_id_seq')")).scalar()
print(f"  Next user ID from sequence: {next_user_id}")
print(f"  Next order ID from sequence: {next_order_id}")

session.rollback()

session.close()
print("\nDatabase connection closed.")