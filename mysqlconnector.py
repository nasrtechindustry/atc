import mysql.connector

# Define your database connection parameters
db_config = {
    'host': 'localhost',  # or '127.0.0.1'
    'user': 'root',       # or another MySQL user
    'password': 'YourPassword',  # Your MySQL root password
    'database': 'community'  # The database you want to connect to (optional for first connection)
}

# Establish the connection
try:
    connection = mysql.connector.connect(**db_config)

    if connection.is_connected():
        print("Successfully connected to the database")

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Your SQL query goes here
    cursor.execute("SELECT DATABASE();")  # Fetch the current database name
    db_name = cursor.fetchone()
    print(f"You're connected to database: {db_name[0]}")

    # Don't forget to close the cursor and connection after the operations
    cursor.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if connection.is_connected():
        connection.close()
        print("Connection closed.")
