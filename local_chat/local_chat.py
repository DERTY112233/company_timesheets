import streamlit as st
import mariadb
import os
from io import BytesIO
import base64
from datetime import datetime

# Database connection setup
def init_db():
    conn = mariadb.connect(
        user="root",  # Your MariaDB user
        password="",  # Your MariaDB password
        host="localhost",  # Your MariaDB host
        port=3306,  # MariaDB port
        database="chat_db"  # Your MariaDB database
    )
    return conn

# Create tables if not exist
def create_tables():
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50),
            message TEXT,
            file_name VARCHAR(255),
            file_data LONGBLOB,
            file_type VARCHAR(20),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Insert a message with optional attachment
def insert_message(username, message, file_name=None, file_data=None, file_type=None):
    conn = init_db()
    cursor = conn.cursor()
    if file_name:
        cursor.execute("INSERT INTO messages (username, message, file_name, file_data, file_type) VALUES (?, ?, ?, ?, ?)",
                       (username, message, file_name, file_data, file_type))
    else:
        cursor.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, message))
    conn.commit()
    conn.close()

# Fetch all messages
def fetch_messages():
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, message, file_name, file_data, file_type, timestamp FROM messages ORDER BY timestamp")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Function to download file as a Streamlit download link
def download_file(file_name, file_data, file_type):
    b64 = base64.b64encode(file_data).decode()  # Convert binary to base64 for Streamlit download
    href = f'<a href="data:{file_type};base64,{b64}" download="{file_name}">Download {file_name}</a>'
    return href

# Streamlit layout and chat functionality
def main():
    st.title("Company Chat Server")

    create_tables()  # Initialize database and tables

    # User input for chat message
    username = st.text_input("Enter your username:")
    message = st.text_area("Enter your message:")

    # File uploader
    uploaded_file = st.file_uploader("Attach a file (PNG, JPEG, PDF, MP4)", type=["png", "jpeg", "pdf", "mp4"])

    # Send button
    if st.button("Send"):
        if username and message:
            file_name, file_data, file_type = None, None, None
            if uploaded_file:
                file_name = uploaded_file.name
                file_data = uploaded_file.read()
                file_type = uploaded_file.type
            insert_message(username, message, file_name, file_data, file_type)
            st.success("Message sent successfully!")
        else:
            st.error("Username and message cannot be empty!")

    st.markdown("---")

    # Display chat history in real-time
    st.subheader("Chat Room")
    messages = fetch_messages()
    for msg in messages:
        username, message, file_name, file_data, file_type, timestamp = msg
        st.write(f"**{username}** ({timestamp.strftime('%Y-%m-%d %H:%M:%S')}): {message}")
        if file_name:
            st.markdown(download_file(file_name, file_data, file_type), unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()

