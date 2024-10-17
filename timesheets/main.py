import streamlit as st
import pandas as pd
from datetime import datetime
import mariadb
import bcrypt
compname = "your company name here"

compname = "company name here"

# Function to create a database connection
def create_connection():
    return mariadb.connect(
        user="root",
        password="",
        host="127.0.0.1",
        port=3306,
        database="timesheets"
    )

# Hash the password using bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Verify a hashed password
def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# Sign up functionality: insert new user into the database
def signup_user(username, password):
    conn = create_connection()
    cur = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        st.success(f"User {username} registered successfully!")
    except mariadb.Error as e:
        st.error(f"Error creating user: {e}")
    cur.close()
    conn.close()

# Login functionality: check user credentials
def login_user(username, password):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user and check_password(password, user[0]):
        return True
    return False

# Function to insert timesheet data into MariaDB
def insert_data_into_db(date, username, project, hours_worked, task_description):
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO timesheet (date, username, project, hours_worked, task_description) VALUES (?, ?, ?, ?, ?)",
            (date, username, project, hours_worked, task_description)
        )
        conn.commit()
        cur.close()
        conn.close()
        st.success("Timesheet entry added to the database successfully!")
    except mariadb.Error as e:
        st.error(f"Error inserting data into MariaDB: {e}")

# Function to update timesheet data in MariaDB
def update_timesheet_entry(timesheet_id, date, project, hours_worked, task_description):
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE timesheet SET date = ?, project = ?, hours_worked = ?, task_description = ? WHERE id = ?",
            (date, project, hours_worked, task_description, timesheet_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        st.success("Timesheet updated successfully!")
    except mariadb.Error as e:
        st.error(f"Error updating timesheet: {e}")

# Function to load timesheet data from the database for the logged-in user
def load_timesheet_data(username):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, date, project, hours_worked, task_description FROM timesheet WHERE username = ?", (username,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(data, columns=["ID", "Date", "Project", "Hours Worked", "Task Description"])

# Set the title of the app
st.title(f"{compname} Timesheet Tracker")

# Manage authentication state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# Set up session state variables for the form fields
if "date" not in st.session_state:
    st.session_state.date = datetime.today()

if "project" not in st.session_state:
    st.session_state.project = ""

if "hours_worked" not in st.session_state:
    st.session_state.hours_worked = 0.0

if "task_description" not in st.session_state:
    st.session_state.task_description = ""

# Define the signup page
def signup():
    st.subheader("Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        if username and password:
            signup_user(username, password)

# Define the login page
def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            st.experimental_rerun()  # Force rerun the app to show the timesheet page
        else:
            st.error("Invalid username or password")

# Define the main timesheet page
def timesheet_page():
    st.subheader(f"Welcome {st.session_state.username}")
    
    # Timesheet form for creating a new entry
    with st.form("Timesheet Entry Form"):
        st.session_state.date = st.date_input("Date", value=st.session_state.date)
        st.session_state.project = st.text_input("Project", value=st.session_state.project)
        st.session_state.hours_worked = st.number_input("Hours Worked", min_value=0.0, step=0.5, value=float(st.session_state.hours_worked))
        st.session_state.task_description = st.text_area("Task Description", value=st.session_state.task_description)
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        # Insert the timesheet entry into the database
        insert_data_into_db(st.session_state.date, st.session_state.username, st.session_state.project, st.session_state.hours_worked, st.session_state.task_description)
        
        # Reset the fields (except the username) after successful submission
        st.session_state.date = datetime.today()
        st.session_state.project = ""
        st.session_state.hours_worked = 0.0
        st.session_state.task_description = ""

    # Load existing timesheets for the logged-in user
    st.subheader("Your Timesheets")
    timesheet_data = load_timesheet_data(st.session_state.username)

    if not timesheet_data.empty:
        # Use Streamlit's data editor for inline editing of timesheet data
        edited_timesheets = st.data_editor(timesheet_data, use_container_width=True, num_rows="dynamic")

        # When the submit button for edits is pressed, save changes back to the database
        if st.button("Save Changes"):
            for index, row in edited_timesheets.iterrows():
                original_row = timesheet_data.iloc[index]
                if not row.equals(original_row):
                    # Update only the changed records
                    update_timesheet_entry(row["ID"], row["Date"], row["Project"], row["Hours Worked"], row["Task Description"])
            st.experimental_rerun()  # Refresh to show updated data
    else:
        st.write("No timesheets available to edit. Start Working 😁 👍")

# Main logic
if not st.session_state.logged_in:
    st.sidebar.title("Authentication")
    auth_option = st.sidebar.radio("Select Option", ("Login", "Sign Up"))
    if auth_option == "Login":
        login()
    elif auth_option == "Sign Up":
        signup()
else:
    timesheet_page()

# Logout button
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logged out successfully!")
        st.experimental_rerun()  # Force rerun after logout

