
import mysql.connector
from database import get_connection
from auth import login, register_patient
from patient import patient_dashboard
from doctor import doctor_dashboard
from admin import admin_dashboard
from utils import print_header, pause


def main_menu():
    print_header("HOSPITAL MANAGEMENT SYSTEM")
    print("1. Patient Login")
    print("2. Doctor Login")
    print("3. Admin Login")
    print("4. New Patient? Register Here")
    print("5. Exit")
    return input("\nChoose an option: ").strip()


def main():
    connection = get_connection()
    print("MySQL connected successfully!\n")

    try:
        while True:
            choice = main_menu()
            try:
                if choice == "1":
                    patient = login(connection, "patients")
                    if patient:
                        patient_dashboard(connection, patient)

                elif choice == "2":
                    doctor = login(connection, "doctors")
                    if doctor:
                        doctor_dashboard(connection, doctor)

                elif choice == "3":
                    admin = login(connection, "admins")
                    if admin:
                        admin_dashboard(connection, admin)

                elif choice == "4":
                    register_patient(connection)
                    pause()

                elif choice == "5":
                    print("\nThank you for using the Hospital Management System. Goodbye!")
                    break

                else:
                    print("\nInvalid choice, please select 1-5.")

            except mysql.connector.Error as e:
                connection.rollback()
                print(f"\nA database error occurred: {e}")
                print("Returning to the main menu.")
                pause()

            except (KeyboardInterrupt, EOFError):
                print("\n\nInterrupted. Returning to the main menu...")
                pause()

    finally:
        connection.close()
        print("MySQL connection closed.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram closed.")
