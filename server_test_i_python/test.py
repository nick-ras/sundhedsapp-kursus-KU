import mysql.connector
from os import environ as env

try:
    # Define the database connection parameters
    cnx = mysql.connector.connect(
        user=env.get("USERNAME"),
        password=env.get("PASSWORD"),
        host="cloud-kursus.mysql.database.azure.com",
        port=3306,
        database=env.get("DATABASE"),
        ssl_disabled=True
    )

    # If the connection is successful, print a success message
    if cnx.is_connected():
        print("Connection to MySQL database successful")

    # Close the database connection
    cnx.close()

except mysql.connector.Error as err:
    # Handle any errors that occurred during the connection attempt
    print(f"Error: {err}")
