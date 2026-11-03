
import mysql.connector
from utils import (
    print_header, print_table, prompt_date, prompt_int,
    record_exists, run_write, pause
)

def doctor_dashboard(connection, doctor):
    while True:
        print_header(f"DOCTOR DASHBOARD - {doctor['name']}")
        print("1. My Appointments")
        print("2. Update Appointment Status")
        print("3. View Patient Details")
        print("4. Add Prescription")
        print("5. Add Medical Record")
        print("6. View Patient Medical History")
        print("7. Logout")

        choice = input("\nChoose an option: ").strip()

        try:
            if choice == "1":
                view_my_appointments(connection, doctor)
            elif choice == "2":
                update_appointment_status(connection, doctor)
            elif choice == "3":
                view_patient_details(connection, doctor)
            elif choice == "4":
                add_prescription(connection, doctor)
            elif choice == "5":
                add_medical_record(connection, doctor)
            elif choice == "6":
                view_patient_history(connection, doctor)
            elif choice == "7":
                print("\nLogging out...")
                break
            else:
                print("\nInvalid choice, try again.")
        except mysql.connector.Error as e:
            connection.rollback()
            print(f"\nA database error occurred, so that action was cancelled: {e}")
            pause()


def view_my_appointments(connection, doctor):
    print_header("MY APPOINTMENTS")
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """SELECT a.appointment_id,
                  p.name AS patient,
                  a.appointment_date,
                  a.appointment_time,
                  a.reason,
                  a.status
           FROM appointments a
                    JOIN patients p ON a.patient_id = p.patient_id
           WHERE a.doctor_id = %s
           ORDER BY a.appointment_date""",
        (doctor["doctor_id"],)
    )
    rows = cursor.fetchall()
    cursor.close()
    print_table(rows)
    pause()


def update_appointment_status(connection, doctor):
    view_my_appointments(connection, doctor)
    appt_id = prompt_int("Enter appointment_id to update (or leave blank to go back): ", allow_blank=True)
    if appt_id is None:
        return

    print("New status: 1) Completed  2) Cancelled  3) Scheduled")
    opt = input("Choose: ").strip()
    status_map = {"1": "Completed", "2": "Cancelled", "3": "Scheduled"}
    status = status_map.get(opt)
    if not status:
        print("Invalid option.")
        pause()
        return

    run_write(
        connection,
        "UPDATE appointments SET status = %s WHERE appointment_id = %s AND doctor_id = %s",
        (status, appt_id, doctor["doctor_id"]),
        success_msg="Status updated.",
        error_prefix="Could not update the appointment"
    )
    pause()


def view_patient_details(connection, doctor):
    print_header("VIEW PATIENT DETAILS")
    patient_id = prompt_int("Enter patient_id: ")

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    row = cursor.fetchone()
    cursor.close()

    if row:
        print_table([row])
    else:
        print("No such patient.")
    pause()


def add_prescription(connection, doctor):
    print_header("ADD PRESCRIPTION")
    patient_id = prompt_int("Patient ID: ")
    if not record_exists(connection, "patients", "patient_id", patient_id):
        print(f"\nNo patient found with ID {patient_id}.")
        pause()
        return

    appointment_id = prompt_int(
        "Related appointment_id (leave blank if none): ", allow_blank=True
    )
    if appointment_id is not None and not record_exists(
        connection, "appointments", "appointment_id", appointment_id
    ):
        print(f"\nNo appointment found with ID {appointment_id}. Leaving it blank.")
        appointment_id = None

    medicine = input("Medicine: ").strip()
    dosage = input("Dosage: ").strip()
    instructions = input("Instructions: ").strip()
    date_issued = prompt_date("Date issued (YYYY-MM-DD): ")

    run_write(
        connection,
        """INSERT INTO prescriptions
           (patient_id, doctor_id, appointment_id, medicine, dosage, instructions, date_issued)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (patient_id, doctor["doctor_id"], appointment_id, medicine, dosage, instructions, date_issued),
        success_msg="Prescription added successfully!",
        error_prefix="Could not add the prescription"
    )
    pause()


def add_medical_record(connection, doctor):
    print_header("ADD MEDICAL RECORD")
    patient_id = prompt_int("Patient ID: ")
    if not record_exists(connection, "patients", "patient_id", patient_id):
        print(f"\nNo patient found with ID {patient_id}.")
        pause()
        return

    diagnosis = input("Diagnosis: ").strip()
    treatment = input("Treatment: ").strip()
    notes = input("Notes: ").strip()
    record_date = prompt_date("Record date (YYYY-MM-DD): ")

    run_write(
        connection,
        """INSERT INTO medical_history
               (patient_id, doctor_id, diagnosis, treatment, notes, record_date)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (patient_id, doctor["doctor_id"], diagnosis, treatment, notes, record_date),
        success_msg="Medical record added successfully!",
        error_prefix="Could not add the medical record"
    )
    pause()


def view_patient_history(connection, doctor):
    print_header("PATIENT MEDICAL HISTORY")
    patient_id = prompt_int("Patient ID: ")

    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """SELECT m.record_id,
                  d.name AS doctor,
                  m.diagnosis,
                  m.treatment,
                  m.notes,
                  m.record_date
           FROM medical_history m
                    JOIN doctors d ON m.doctor_id = d.doctor_id
           WHERE m.patient_id = %s
           ORDER BY m.record_date DESC""",
        (patient_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    print_table(rows)
    pause()
