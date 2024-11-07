import mysql.connector
from tkinter import *
from tkinter import messagebox
from tkinter.simpledialog import askstring
from datetime import datetime

# Establish MySQL connection
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="dbms123",
        database="hospital"
    )

# Patient Login Function
def patient_login():
    def verify_patient_login():
        username = patient_username_entry.get()
        password = patient_password_entry.get()

        connection = create_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM LoginDetails WHERE Username = %s AND Password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        if result:
            patient_dashboard(username)
        else:
            messagebox.showerror("Login Error", "Invalid username or password.")
        
        cursor.close()
        connection.close()

    login_window = Toplevel()
    login_window.title("Patient Login")
    login_window.geometry("400x300")

    Label(login_window, text="Username").pack(pady=5)
    global patient_username_entry
    patient_username_entry = Entry(login_window)
    patient_username_entry.pack(pady=5)

    Label(login_window, text="Password").pack(pady=5)
    global patient_password_entry
    patient_password_entry = Entry(login_window, show="*")
    patient_password_entry.pack(pady=5)

    Button(login_window, text="Login", command=verify_patient_login, bg="green", fg="white").pack(pady=20)
    Button(login_window, text="Register New Patient", command=patient_register, bg="green", fg="white").pack()
    Button(login_window, text="Back", command=login_window.destroy, bg="green", fg="white").pack(pady=10)

# Patient Register Function
def patient_register():
    def register_new_patient():
        name = name_entry.get()
        age = age_entry.get()
        gender = gender_var.get()
        contact = contact_entry.get()

        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute("INSERT INTO Patients (Name, Age, Gender, ContactNumber) VALUES (%s, %s, %s, %s)",
                       (name, age, gender, contact))
        connection.commit()

        cursor.execute("SELECT PatientID FROM Patients WHERE Name = %s", (name,))
        patient_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO LoginDetails (Username, Password, PatientID) VALUES (%s, %s, %s)",
                       (username_entry.get(), password_entry.get(), patient_id))
        connection.commit()

        messagebox.showinfo("Registration Success", "Patient Registered Successfully.")
        
        cursor.close()
        connection.close()
    
    register_window = Toplevel()
    register_window.title("Patient Registration")
    register_window.geometry("500x700")
    Label(register_window, text="Username").pack(pady=5)
    username_entry = Entry(register_window)
    username_entry.pack(pady=5)

    Label(register_window, text="Password").pack(pady=5)
    password_entry = Entry(register_window, show="*")
    password_entry.pack(pady=5)

    Label(register_window, text="Name").pack(pady=5)
    name_entry = Entry(register_window)
    name_entry.pack(pady=5)

    Label(register_window, text="Age").pack(pady=5)
    age_entry = Entry(register_window)
    age_entry.pack(pady=5)

    Label(register_window, text="Gender").pack(pady=5)
    gender_var = StringVar()
    gender_menu = OptionMenu(register_window, gender_var, "Male", "Female", "Other")
    gender_menu.pack(pady=5)

    Label(register_window, text="Contact Number").pack(pady=5)
    contact_entry = Entry(register_window)
    contact_entry.pack(pady=5)

    Button(register_window, text="Register", command=register_new_patient, bg="green", fg="white").pack(pady=20)
    Button(register_window, text="Back", command=register_window.destroy, bg="green", fg="white").pack(pady=10)

# Patient Dashboard
def patient_dashboard(username):
    dashboard_window = Toplevel()
    dashboard_window.geometry("500x400")
    dashboard_window.title("Patient Dashboard")
    dashboard_window.config(bg="black")
    Label(dashboard_window, text=f"Welcome, {username}").pack(pady=20)

    Button(dashboard_window, text="Book Appointment", command=book_appointment, bg="green", fg="white").pack(pady=5)
    Button(dashboard_window, text="View Appointments", command=view_appointments, bg="green", fg="white").pack(pady=5)
    Button(dashboard_window, text="Update Patient Details", command=update_patient_details, bg="green", fg="white").pack(pady=5)
    Button(dashboard_window, text="Logout", command=dashboard_window.destroy, bg="green", fg="white").pack(pady=10)


# Book Appointment Function (Patient)
def book_appointment():
    department_window = Toplevel()
    department_window.title("Select Department")

    Label(department_window, text="Select a Department:").pack(pady=10)

    connection = create_connection()  # Ensure connection is established
    cursor = connection.cursor()

    # Fetching departments
    cursor.execute("SELECT DepartmentID, DepartmentName FROM Departments")
    departments = cursor.fetchall()

    def show_doctors(department_id):
        # Ensure a new connection to fetch doctors
        connection = create_connection()  # Reconnect the database
        cursor = connection.cursor()

        # Close current department window
        department_window.destroy()

        doctor_window = Toplevel()
        doctor_window.title("Select Doctor")

        

        Label(doctor_window, text="Select a Doctor:").pack(pady=10)

        # Fetching doctors from the selected department
        cursor.execute("""
            SELECT DoctorID, Name 
            FROM Doctors 
            WHERE DepartmentID = %s
        """, (department_id,))
        doctors = cursor.fetchall()

        def select_date_time(doctor_id):
            # Close current doctor selection window
            doctor_window.destroy()

            date_time_window = Toplevel()
            date_time_window.title("Select Appointment Date and Time")

            Label(date_time_window, text="Enter Appointment Date (YYYY-MM-DD):").pack(pady=10)
            date_entry = Entry(date_time_window)
            date_entry.pack(pady=5)

            Label(date_time_window, text="Enter Appointment Time (HH:MM):").pack(pady=10)
            time_entry = Entry(date_time_window)
            time_entry.pack(pady=5)

            def confirm_appointment():
                appointment_date = date_entry.get()
                appointment_time = time_entry.get()

                try:
                    # Validating the date format
                    datetime.strptime(appointment_date, "%Y-%m-%d")
                    # Validating the time format
                    datetime.strptime(appointment_time, "%H:%M")

                    # Ensure connection and cursor for patient query
                    connection = create_connection()
                    cursor = connection.cursor()

                    # Fetch PatientID based on the logged-in patient username
                    cursor.execute("SELECT PatientID FROM LoginDetails WHERE Username = %s", (patient_username_entry.get(),))
                    patient_id = cursor.fetchone()[0]

                    # Insert the appointment into the database
                    cursor.execute("""
                        INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime) 
                        VALUES (%s, %s, %s, %s)
                    """, (patient_id, doctor_id, appointment_date, appointment_time))
                    connection.commit()

                    messagebox.showinfo("Success", "Appointment booked successfully.")
                    date_time_window.destroy()

                except ValueError:
                    messagebox.showerror("Invalid Date/Time", "Please enter a valid date (YYYY-MM-DD) and time (HH:MM).")
                finally:
                    # Close the cursor and connection
                    cursor.close()
                    connection.close()

            Button(date_time_window, text="Confirm Appointment", command=confirm_appointment, bg="green", fg="white").pack(pady=10)

        # Create buttons for each doctor
        for doctor in doctors:
            Button(doctor_window, text=doctor[1], command=lambda d=doctor[0]: select_date_time(d), bg="green", fg="white").pack(pady=5)

        cursor.close()
        connection.close()

    # Create buttons for each department
    department_window.geometry("900x1200")
    for department in departments:
        Button(department_window, text=department[1], command=lambda d=department[0]: show_doctors(d), bg="green", fg="white").pack(pady=5)
        
    cursor.close()
    Button(department_window, text="Back", command=department_window.destroy, bg="green", fg="white").pack(pady=10)

    connection.close()


# View Appointments Function (Patient)
def view_appointments():
    # Implementation as per previous code provided for viewing appointments.
    appointments_window = Toplevel()
    appointments_window.title("View Appointments")

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT PatientID FROM LoginDetails WHERE Username = %s", (patient_username_entry.get(),))
    patient_id = cursor.fetchone()[0]

    cursor.execute("""
        SELECT Appointments.AppointmentID, Doctors.Name, Appointments.AppointmentDate 
        FROM Appointments
        JOIN Doctors ON Appointments.DoctorID = Doctors.DoctorID
        WHERE Appointments.PatientID = %s
    """, (patient_id,))
    appointments = cursor.fetchall()

    for appointment in appointments:
        Label(appointments_window, text=f"ID: {appointment[0]}, Doctor: {appointment[1]}, Date: {appointment[2]}").pack(pady=5)

    Button(appointments_window, text="Back", command=appointments_window.destroy, bg="green", fg="white").pack(pady=10)

    cursor.close()
    connection.close()

def doctor_login():
    def verify_doctor_login():
        username = doctor_username_entry.get()  # Getting the entered username
        password = doctor_password_entry.get()  # Getting the entered password

        connection = create_connection()
        cursor = connection.cursor()

        # Fetch the DoctorID based on both Username and Password
        query = """
            SELECT DoctorID 
            FROM doctorlogindetails 
            WHERE Username = %s AND Password = %s
        """
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        if result:
            doctor_id = result[0]
            messagebox.showinfo("Success", "Doctor login successful.")
            doctor_dashboard(doctor_id)  # Redirect to doctor dashboard
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

        cursor.close()
        connection.close()

    login_window = Toplevel()
    login_window.title("Doctor Login")
    login_window.geometry("400x300")

    Label(login_window, text="Username").pack(pady=5)
    global doctor_username_entry
    doctor_username_entry = Entry(login_window)
    doctor_username_entry.pack(pady=5)

    Label(login_window, text="Password").pack(pady=5)
    global doctor_password_entry
    doctor_password_entry = Entry(login_window, show="*")
    doctor_password_entry.pack(pady=5)

    Button(login_window, text="Login", command=verify_doctor_login, bg="green", fg="white").pack(pady=20)
    Button(login_window, text="Back", command=login_window.destroy, bg="green", fg="white").pack(pady=10)

# Doctor Dashboard
def doctor_dashboard(doctor_id):
    dashboard_window = Toplevel()
    dashboard_window.geometry("400x300")
    dashboard_window.title("Doctor Dashboard")

    Label(dashboard_window, text=f"Welcome, Doctor").pack(pady=20)

    Button(dashboard_window, text="View Patient List", command=view_patients, bg="green", fg="white").pack(pady=5)
    Button(dashboard_window, text="Delete Patient Record", command=delete_patient_record, bg="green", fg="white").pack(pady=5)
    Button(dashboard_window, text="Logout", command=dashboard_window.destroy, bg="green", fg="white").pack(pady=10)


# View Patients Function (Doctor)
def view_patients():
    patients_window = Toplevel()
    patients_window.title("Patient List")

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT PatientID, Name, Age, Gender, ContactNumber FROM Patients")
    patients = cursor.fetchall()

    for patient in patients:
        Label(patients_window, text=f"ID: {patient[0]}, Name: {patient[1]}, Age: {patient[2]}, Gender: {patient[3]}, Contact: {patient[4]}").pack(pady=5)

    Button(patients_window, text="Back", command=patients_window.destroy, bg="green", fg="white").pack(pady=10)

    cursor.close()
    connection.close()
# Update Patient Details Function
def update_patient_details():
    update_window = Toplevel()
    update_window.title("Update Patient Details")
    update_window.geometry("900x1100")
    Label(update_window, text="New Name").pack(pady=5)
    new_name_entry = Entry(update_window)
    new_name_entry.pack(pady=5)

    Label(update_window, text="New Contact Number").pack(pady=5)
    new_contact_entry = Entry(update_window)
    new_contact_entry.pack(pady=5)

    Label(update_window, text="New Age").pack(pady=5)
    new_age_entry = Entry(update_window)
    new_age_entry.pack(pady=5)

    Label(update_window, text="New Gender").pack(pady=5)
    gender_var = StringVar()
    gender_menu = OptionMenu(update_window, gender_var, "Male", "Female", "Other")
    gender_menu.pack(pady=5)

    def save_changes():
        new_name = new_name_entry.get()
        new_contact = new_contact_entry.get()
        new_age = new_age_entry.get()
        new_gender = gender_var.get()

        # Check if fields are empty
        if not new_name or not new_contact or not new_age or not new_gender:
            messagebox.showerror("Input Error", "All fields must be filled out.")
            return

        # Validate age to be a number
        try:
            new_age = int(new_age)
        except ValueError:
            messagebox.showerror("Input Error", "Age must be a valid number.")
            return

        connection = create_connection()
        cursor = connection.cursor()

        patient_username = patient_username_entry.get()

        try:
            cursor.execute("SELECT PatientID FROM LoginDetails WHERE Username = %s", (patient_username,))
            result = cursor.fetchone()

            if result:
                patient_id = result[0]

                cursor.execute("""
                    UPDATE Patients 
                    SET Name = %s, ContactNumber = %s, Age = %s, Gender = %s 
                    WHERE PatientID = %s
                """, (new_name, new_contact, new_age, new_gender, patient_id))
                connection.commit()

                messagebox.showinfo("Update Successful", "Patient details updated successfully.")
                
                # Optionally clear the fields
                new_name_entry.delete(0, END)
                new_contact_entry.delete(0, END)
                new_age_entry.delete(0, END)
                gender_var.set('')

            else:
                messagebox.showerror("Error", "Patient not found.")

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error updating patient details: {e}")
        finally:
            cursor.close()
            connection.close()


    Button(update_window, text="Save Changes", command=save_changes, bg="green", fg="white").pack(pady=10)
    Button(update_window, text="Back", command=update_window.destroy, bg="green", fg="white").pack(pady=10)

# Delete Patient Record Function (Doctor)
def delete_patient_record():
    delete_window = Toplevel()
    delete_window.title("Delete Patient Record")

    Label(delete_window, text="Enter Patient ID to delete:").pack(pady=5)
    patient_id_entry = Entry(delete_window)
    patient_id_entry.pack(pady=5)

    def delete_patient():
        patient_id = patient_id_entry.get()

        if not patient_id:
            messagebox.showerror("Input Error", "Please enter a Patient ID.")
            return

        connection = create_connection()
        cursor = connection.cursor()

        try:
            # Delete associated appointments for the patient
            cursor.execute("DELETE FROM Appointments WHERE PatientID = %s", (patient_id,))
            connection.commit()

            # Delete the corresponding login record from the LoginDetails table
            cursor.execute("DELETE FROM LoginDetails WHERE PatientID = %s", (patient_id,))
            connection.commit()

            # Finally, delete the patient record from the Patients table
            cursor.execute("DELETE FROM Patients WHERE PatientID = %s", (patient_id,))
            connection.commit()

            messagebox.showinfo("Success", "Patient record, associated appointments, and login details deleted successfully.")
        
        except mysql.connector.Error as e:
            if e.errno == 1451:  # Foreign key constraint violation error
                messagebox.showerror("Error", "Cannot delete this patient. There are related records.")
            else:
                messagebox.showerror("Error", f"Error deleting patient record: {e}")
        
        finally:
            cursor.close()
            connection.close()

        delete_window.destroy()

    Button(delete_window, text="Delete", command=delete_patient, bg="green", fg="white").pack(pady=10)
    Button(delete_window, text="Back", command=delete_window.destroy, bg="green", fg="white").pack(pady=10)

# Main Menu
def main_menu():
    root = Tk()
    root.title("Hospital Management System")
    root.geometry("500x400")
     # Set the background color for the window
    root.config(bg="black")

    # Create green buttons with white text
    patient_button = Button(root, text="Patient Login", command=patient_login, bg="green", fg="white")
    patient_button.pack(pady=10)
    
    doctor_button = Button(root, text="Doctor Login", command=doctor_login, bg="green", fg="white")
    doctor_button.pack(pady=10)

     # Create a close button to exit the application
    close_button = Button(root, text="Close", command=root.quit, bg="red", fg="white")
    close_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
