import mysql.connector

try:
    # Define the database connection parameters
    cnx = mysql.connector.connect(
        user="cloud",
        password="{your_password}",
        host="cloud-kursus.mysql.database.azure.com",
        port=3306,
        database="{your_database}",
        ssl_ca="{ca-cert filename}",
        ssl_disabled=False
    )

    # If the connection is successful, print a success message
    if cnx.is_connected():
        print("Connection to MySQL database successful")

    # Close the database connection
    cnx.close()

except mysql.connector.Error as err:
    # Handle any errors that occurred during the connection attempt
    print(f"Error: {err}")
