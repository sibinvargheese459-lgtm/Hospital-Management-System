import mysql.connector
import pandas as pd

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="hospital_db"
)
print("MySQL connected successfully!")

# PATIENT DATA


patient_query = "SELECT * FROM patients"

patients = pd.read_sql(patient_query, connection)

print("\n===== PATIENT DATA =====")
print(patients)

# DOCTOR DATA

doctor_query = "SELECT * FROM doctors"

doctors = pd.read_sql(doctor_query, connection)

print("\n===== DOCTOR DATA =====")
print(doctors)

# ADMIN DATA

admin_query = "SELECT * FROM admins"

admins = pd.read_sql(admin_query, connection)

print("\n===== ADMIN DATA =====")
print(admins)
connection.close()

print("\nMySQL connection closed.")
