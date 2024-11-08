import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to the User database
def connect_user_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="your_mariadb_username",
            password="your_mariadb_password",
            database="users_etc"
        )
        return conn
    except Error as e:
        st.error(f"Error connecting to MariaDB User database: {e}")
        return None

# Connect to the Manager database
def connect_manager_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="your_mariadb_username",
            password="your_mariadb_password",
            database="management_etc"
        )
        return conn
    except Error as e:
        st.error(f"Error connecting to MariaDB Manager database: {e}")
        return None

# Initialize the databases if tables don't exist
def initialize_databases():
    with connect_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users_etc (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(64),
                full_name VARCHAR(100),
                first_name VARCHAR(50),
                second_name VARCHAR(50),
                last_name VARCHAR(50),
                department VARCHAR(100),
                company VARCHAR(100),
                company_address VARCHAR(255),
                date_started DATE,
                leave_taken INT DEFAULT 0,
                reasons_leave TEXT
            )
        ''')
        conn.commit()
    
    with connect_manager_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS management_etc (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(64),
                full_name VARCHAR(100),
                company_name VARCHAR(100),
                company_address VARCHAR(255),
                users_registered INT DEFAULT 0
            )
        ''')
        conn.commit()

# Function to sign up a new manager
def signup_manager(username, password, full_name, company_name, company_address):
    conn = connect_manager_db()
    if conn:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        try:
            cursor.execute(
                "INSERT INTO management_etc (username, password, full_name, company_name, company_address) VALUES (%s, %s, %s, %s, %s)",
                (username, hashed_password, full_name, company_name, company_address)
            )
            conn.commit()
            st.success("Manager signed up successfully!")
        except Error as e:
            st.error(f"Error signing up manager: {e}")
        finally:
            conn.close()

# Function to sign in as a user or manager
def login(username, password, is_manager=False):
    conn = connect_manager_db() if is_manager else connect_user_db()
    if conn:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        table = "management_etc" if is_manager else "users_etc"
        try:
            cursor.execute(f"SELECT * FROM {table} WHERE username=%s AND password=%s", (username, hashed_password))
            user = cursor.fetchone()
            if user:
                st.success("Login successful!")
                return user
            else:
                st.error("Invalid username or password.")
                return None
        except Error as e:
            st.error(f"Error during login: {e}")
        finally:
            conn.close()

# Main application logic
def main():
    if 'show_signup' not in st.session_state:
        st.session_state['show_signup'] = False

    # Sidebar options
    st.sidebar.title("Account")
    if st.sidebar.button("Sign Up as Manager"):
        st.session_state['show_signup'] = True
    if st.sidebar.button("Login"):
        st.session_state['show_signup'] = False

    # Show Signup or Login Form
    if st.session_state['show_signup']:
        st.sidebar.subheader("Sign Up as Manager")
        username_signup = st.sidebar.text_input("Username", key="signup_username")
        password_signup = st.sidebar.text_input("Password", type="password", key="signup_password")
        full_name_signup = st.sidebar.text_input("Full Name", key="signup_full_name")
        company_name_signup = st.sidebar.text_input("Company Name", key="signup_company_name")
        company_address_signup = st.sidebar.text_input("Company Address", key="signup_company_address")

        if st.sidebar.button("Submit Sign-Up"):
            if username_signup and password_signup:
                signup_manager(username_signup, password_signup, full_name_signup, company_name_signup, company_address_signup)
                st.session_state['show_signup'] = False
            else:
                st.error("Please fill in all fields.")

    else:
        st.sidebar.subheader("Login")
        role = st.sidebar.radio("Role", ["Manager", "User"], key="role_select")
        username_login = st.sidebar.text_input("Username", key="login_username")
        password_login = st.sidebar.text_input("Password", type="password", key="login_password")

        if st.sidebar.button("Login"):
            is_manager = role == "Manager"
            user = login(username_login, password_login, is_manager)
            if user:
                if is_manager:
                    st.write("Manager dashboard here.")
                else:
                    st.write("User dashboard here.")

# Initialize the databases and run main
initialize_databases()
main()
