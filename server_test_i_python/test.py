import mysql.connector
from os import environ as env

try:
		# Define the database connection parameters
		cnx = mysql.connector.connect(
				user=env.get("USERNAME"),
				password="Valdemar20-",#env.get("PASSWORD"),
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
				
				# create_table_sql = """
				# INSERT INTO DCRTable (Graph_id, Simulation_id, Process_instance_name, Description) VALUES ("test", "test", "test", "test");
				# """
				# cursor.execute(create_table_sql)
				
				cnx.commit()
				temp = "USE `cloud-kursus`;"
				cursor.execute(temp)


				select_statement = """
				SELECT * FROM DCRTable;
				"""

				cursor.execute(select_statement)
				rows = cursor.fetchall()
				print("now dcr table")
				for row in rows:
						print(row)
				select_statement2 = """
				SELECT * FROM DCRUsers;
				"""
				cursor.execute(select_statement2)
				rows = cursor.fetchall()
				
				print("now users table")
				for row in rows:
						print(row)
				cursor.close()

		cnx.close()

except mysql.connector.Error as err:
		print(f"Error: {err}")





