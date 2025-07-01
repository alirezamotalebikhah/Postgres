import psycopg2

try:
    connection = psycopg2.connect(
        user="myuser",
        password="mypassword",
        host="localhost",
        port="5432",
        database="mydatabase"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record)
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")