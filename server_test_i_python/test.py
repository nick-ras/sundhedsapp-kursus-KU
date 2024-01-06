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

    # Close the database connection
    if cnx.is_connected():
        print("Connection to MySQL database successful")

        # Create a cursor object to interact with the database
        cursor = cnx.cursor()

        # SQL statement to create the DCRUsers table
        create_table_sql = """
        SELECT * FROM DCRUsers;
				"""

        # Execute the SQL statement to create the table
        temp = cursor.execute(create_table_sql)
        rows = cursor.fetchall()

        # Print the retrieved data
        for row in rows:
            print(row)
        # Commit the changes to the database
        cnx.commit()

        # Close the cursor and database connection
        cursor.close()

    # Close the database connection
    cnx.close()

except mysql.connector.Error as err:
    # Handle any errors that occurred during the connection attempt
    print(f"Error: {err}")
