
def login(connection, role):

    table_id_column = {
        "patients": "patient_id",
        "doctors": "doctor_id",
        "admins": "admin_id",
    }[role]

    print(f"\n--- {role[:-1].capitalize()} Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    cursor = connection.cursor(dictionary=True)
    query = f"SELECT * FROM {role} WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    cursor.close()

    if user:
        print(f"\nLogin successful. Welcome, {user['name']}!")
        return user
    else:
        print("\nInvalid username or password.")
        return None


def register_patient(connection):

    print("\n--- New Patient Registration ---")
    name = input("Full name: ").strip()
    age = input("Age: ").strip()
    gender = input("Gender (Male/Female/Other): ").strip()
    phone = input("Phone: ").strip()
    email = input("Email: ").strip()
    address = input("Address: ").strip()
    blood_group = input("Blood group (e.g. O+): ").strip()
    username = input("Choose a username: ").strip()
    password = input("Choose a password: ").strip()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT patient_id FROM patients WHERE username = %s", (username,))
    if cursor.fetchone():
        print("That username is already taken. Please try logging in instead.")
        cursor.close()
        return None

    try:
        age_val = int(age) if age else None
    except ValueError:
        age_val = None

    cursor.execute(
        """INSERT INTO patients
           (username, password, name, age, gender, phone, email, address, blood_group)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (username, password, name, age_val, gender, phone, email, address, blood_group)
    )
    connection.commit()
    new_id = cursor.lastrowid
    cursor.close()

    print(f"\nRegistration successful! Your patient ID is {new_id}. You can now log in.")

    return {
        "patient_id": new_id,
        "username": username,
        "name": name,
        "age": age_val,
        "gender": gender,
        "phone": phone,
        "email": email,
        "address": address,
        "blood_group": blood_group,
    }