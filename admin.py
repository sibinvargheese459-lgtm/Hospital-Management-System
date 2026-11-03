
import mysql.connector
from utils import (
    print_header, print_table, prompt_date, prompt_int, prompt_float,
    record_exists, run_write, pause
)


def admin_dashboard(connection, admin):
    while True:
        print_header(f"ADMIN DASHBOARD - {admin['name']}")
        print("1. Manage Patients")
        print("2. Manage Doctors")
        print("3. View All Appointments")
        print("4. Manage Billing")
        print("5. Reports")
        print("6. Logout")

        choice = input("\nChoose an option: ").strip()

        try:
            if choice == "1":
                manage_patients(connection)
            elif choice == "2":
                manage_doctors(connection)
            elif choice == "3":
                view_all_appointments(connection)
            elif choice == "4":
                manage_billing(connection)
            elif choice == "5":
                reports(connection)
            elif choice == "6":
                print("\nLogging out...")
                break
            else:
                print("\nInvalid choice, try again.")
        except mysql.connector.Error as e:
            connection.rollback()
            print(f"\nA database error occurred, so that action was cancelled: {e}")
            pause()


def manage_patients(connection):
    while True:
        print_header("MANAGE PATIENTS")
        print("1. View All Patients")
        print("2. Add Patient")
        print("3. Delete Patient")
        print("4. Back")
        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM patients")
            print_table(cursor.fetchall())
            cursor.close()
            pause()
        elif choice == "2":
            add_patient(connection)
        elif choice == "3":
            delete_record(connection, "patients", "patient_id")
        elif choice == "4":
            break
        else:
            print("\nInvalid choice, try again.")


def add_patient(connection):
    print_header("ADD PATIENT")
    name = input("Name: ").strip()
    age = prompt_int("Age (leave blank if unknown): ", allow_blank=True)
    gender = input("Gender: ").strip()
    phone = input("Phone: ").strip()
    email = input("Email: ").strip()
    address = input("Address: ").strip()
    blood_group = input("Blood group: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    run_write(
        connection,
        """INSERT INTO patients
           (username, password, name, age, gender, phone, email, address, blood_group)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (username, password, name, age, gender, phone, email, address, blood_group),
        success_msg="Patient added successfully!",
        error_prefix="Could not add the patient (that username may already be taken)"
    )
    pause()

# DOCTORS

def manage_doctors(connection):
    while True:
        print_header("MANAGE DOCTORS")
        print("1. View All Doctors")
        print("2. Add Doctor")
        print("3. Delete Doctor")
        print("4. Back")
        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM doctors")
            print_table(cursor.fetchall())
            cursor.close()
            pause()
        elif choice == "2":
            add_doctor(connection)
        elif choice == "3":
            delete_record(connection, "doctors", "doctor_id")
        elif choice == "4":
            break
        else:
            print("\nInvalid choice, try again.")


def add_doctor(connection):
    print_header("ADD DOCTOR")
    name = input("Name: ").strip()
    specialization = input("Specialization: ").strip()
    phone = input("Phone: ").strip()
    email = input("Email: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    run_write(
        connection,
        """INSERT INTO doctors (username, password, name, specialization, phone, email)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (username, password, name, specialization, phone, email),
        success_msg="Doctor added successfully!",
        error_prefix="Could not add the doctor (that username may already be taken)"
    )
    pause()



# SHARED DELETE HELPER
def delete_record(connection, table, id_column):
    record_id = prompt_int(f"Enter {id_column} to delete (or leave blank to go back): ", allow_blank=True)
    if record_id is None:
        return

    if not record_exists(connection, table, id_column, record_id):
        print(f"\nNo matching record found in {table}.")
        pause()
        return

    confirm = input(f"Type 'yes' to confirm deleting from {table}: ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        pause()
        return

    run_write(
        connection,
        f"DELETE FROM {table} WHERE {id_column} = %s",
        (record_id,),
        success_msg="Deleted successfully.",
        error_prefix="Could not delete this record"
    )
    pause()


# APPOINTMENTS
def view_all_appointments(connection):
    print_header("ALL APPOINTMENTS")
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """SELECT a.appointment_id,
                  p.name AS patient,
                  d.name AS doctor,
                  a.appointment_date,
                  a.appointment_time,
                  a.reason,
                  a.status
           FROM appointments a
                    JOIN patients p ON a.patient_id = p.patient_id
                    JOIN doctors d ON a.doctor_id = d.doctor_id
           ORDER BY a.appointment_date"""
    )
    rows = cursor.fetchall()
    cursor.close()
    print_table(rows)
    pause()


# BILLING
def manage_billing(connection):
    while True:
        print_header("MANAGE BILLING")
        print("1. View All Bills")
        print("2. Add Bill")
        print("3. Mark Bill as Paid")
        print("4. Back")
        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT b.bill_id,
                          p.name AS patient,
                          b.appointment_id,
                          b.amount,
                          b.status,
                          b.bill_date
                   FROM bills b
                            JOIN patients p ON b.patient_id = p.patient_id
                   ORDER BY b.bill_date DESC"""
            )
            print_table(cursor.fetchall())
            cursor.close()
            pause()
        elif choice == "2":
            add_bill(connection)
        elif choice == "3":
            mark_bill_paid(connection)
        elif choice == "4":
            break
        else:
            print("\nInvalid choice, try again.")


def add_bill(connection):
    print_header("ADD BILL")
    patient_id = prompt_int("Patient ID: ")
    if not record_exists(connection, "patients", "patient_id", patient_id):
        print(f"\nNo patient found with ID {patient_id}.")
        pause()
        return

    amount = prompt_float("Amount: ")

    appointment_id = prompt_int(
        "Related appointment_id (leave blank if none): ", allow_blank=True
    )
    if appointment_id is not None and not record_exists(
        connection, "appointments", "appointment_id", appointment_id
    ):
        print(f"\nNo appointment found with ID {appointment_id}. Leaving it blank.")
        appointment_id = None

    bill_date = prompt_date("Bill date (YYYY-MM-DD): ")

    run_write(
        connection,
        """INSERT INTO bills (patient_id, appointment_id, amount, status, bill_date)
           VALUES (%s, %s, %s, 'Unpaid', %s)""",
        (patient_id, appointment_id, amount, bill_date),
        success_msg="Bill added successfully!",
        error_prefix="Could not add the bill"
    )
    pause()


def mark_bill_paid(connection):
    bill_id = prompt_int("Enter bill_id to mark as paid (or leave blank to go back): ", allow_blank=True)
    if bill_id is None:
        return

    run_write(
        connection,
        "UPDATE bills SET status = 'Paid' WHERE bill_id = %s",
        (bill_id,),
        success_msg="Bill marked as paid.",
        error_prefix="Could not update the bill"
    )
    pause()


# REPORTS
def reports(connection):
    print_header("REPORTS")
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM patients")
    total_patients = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM doctors")
    total_doctors = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM appointments WHERE status = 'Scheduled'")
    scheduled = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM appointments WHERE status = 'Completed'")
    completed = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(amount),0) AS total FROM bills WHERE status = 'Unpaid'")
    unpaid_total = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(amount),0) AS total FROM bills WHERE status = 'Paid'")
    paid_total = cursor.fetchone()["total"]

    cursor.close()

    print(f"Total Patients            : {total_patients}")
    print(f"Total Doctors              : {total_doctors}")
    print(f"Scheduled Appointments     : {scheduled}")
    print(f"Completed Appointments     : {completed}")
    print(f"Total Revenue Collected    : {paid_total}")
    print(f"Total Outstanding (Unpaid) : {unpaid_total}")
    pause()
