
import mysql.connector
from utils import (
    print_header, print_table, prompt_date, prompt_time, prompt_int,
    record_exists, run_write, pause
)


def patient_dashboard(connection, patient):
    while True:
        print_header(f"PATIENT DASHBOARD - {patient['name']}")
        print("1. My Record")
        print("2. Book Appointment")
        print("3. My Appointments")
        print("4. Cancel Appointment")
        print("5. My Prescriptions")
        print("6. My Medical History")
        print("7. My Bills")
        print("8. Logout")

        choice = input("\nChoose an option: ").strip()

        try:
            if choice == "1":
                view_my_record(connection, patient)
            elif choice == "2":
                book_appointment(connection, patient)
            elif choice == "3":
                view_my_appointments(connection, patient)
            elif choice == "4":
                cancel_appointment(connection, patient)
            elif choice == "5":
                view_my_prescriptions(connection, patient)
            elif choice == "6":
                view_my_medical_history(connection, patient)
            elif choice == "7":
                view_my_bills(connection, patient)
            elif choice == "8":
                print("\nLogging out...")
                break
            else:
                print("\nInvalid choice, try again.")
        except mysql.connector.Error as e:
            connection.rollback()
            print(f"\nA database error occurred, so that action was cancelled: {e}")
            pause()


def view_my_record(connection, patient):
    print_header("MY RECORD")
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient["patient_id"],))
    row = cursor.fetchone()
    cursor.close()
    print_table([row] if row else [])
    pause()


def book_appointment(connection, patient):
    print_header("BOOK APPOINTMENT")
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT doctor_id, name, specialization FROM doctors")
    doctors = cursor.fetchall()
    cursor.close()

    if not doctors:
        print("There are no doctors registered yet. Please try again later.")
        pause()
        return

    print_table(doctors, columns=["doctor_id", "name", "specialization"])

    doctor_id = prompt_int("\nEnter doctor_id to book with: ")
    if not record_exists(connection, "doctors", "doctor_id", doctor_id):
        print(f"\nNo doctor found with ID {doctor_id}. Please pick one from the list above.")
        pause()
        return

    date = prompt_date()
    time = prompt_time()
    reason = input("Reason for visit: ").strip()

    run_write(
        connection,
        """INSERT INTO appointments (patient_id, doctor_id, appointment_date,
                                     appointment_time, reason, status)
           VALUES (%s, %s, %s, %s, %s, 'Scheduled')""",
        (patient["patient_id"], doctor_id, date, time, reason),
        success_msg="Appointment booked successfully!",
        error_prefix="Could not book the appointment"
    )
    pause()


def view_my_appointments(connection, patient):
    print_header("MY APPOINTMENTS")
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """SELECT a.appointment_id,
                  d.name AS doctor,
                  a.appointment_date,
                  a.appointment_time,
                  a.reason,
                  a.status
           FROM appointments a
                    JOIN doctors d ON a.doctor_id = d.doctor_id
           WHERE a.patient_id = %s
           ORDER BY a.appointment_date""",
        (patient["patient_id"],)
    )
    rows = cursor.fetchall()
    cursor.close()
    print_table(rows)
    pause()


def cancel_appointment(connection, patient):
    view_my_appointments(connection, patient)
    appt_id = prompt_int("Enter appointment_id to cancel (or leave blank to go back): ", allow_blank=True)
    if appt_id is None:
        return

    run_write(
        connection,
        "UPDATE appointments SET status = 'Cancelled' WHERE appointment_id = %s AND patient_id = %s",
        (appt_id, patient["patient_id"]),
        success_msg="Appointment cancelled.",
        error_prefix="Could not cancel the appointment"
    )
    pause()


def view_my_prescriptions(connection, patient):
    print_header("MY PRESCRIPTIONS")
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """SELECT p.prescription_id,
                  d.name AS doctor,
                  p.medicine,
                  p.dosage,
                  p.instructions,
                  p.date_issued
           FROM prescriptions p
                    JOIN doctors d ON p.doctor_id = d.doctor_id
           WHERE p.patient_id = %s
           ORDER BY p.date_issued DESC""",
        (patient["patient_id"],)
    )
    rows = cursor.fetchall()
    cursor.close()
    print_table(rows)
    pause()


def view_my_medical_history(connection, patient):
    print_header("MY MEDICAL HISTORY")
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
        (patient["patient_id"],)
    )
    rows = cursor.fetchall()
    cursor.close()
    print_table(rows)
    pause()


def view_my_bills(connection, patient):
    print_header("MY BILLS")
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """SELECT bill_id, appointment_id, amount, status, bill_date
           FROM bills
           WHERE patient_id = %s
           ORDER BY bill_date DESC""",
        (patient["patient_id"],)
    )
    rows = cursor.fetchall()
    cursor.close()
    print_table(rows)
    pause()
