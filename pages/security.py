import streamlit as st
import pymysql
import re
import pandas as pd
import time
import base64
def img_to_base64(image_data):
    return base64.b64encode(image_data).decode()

def initialize_database():
    try:
        mysql_config = st.secrets["mysql"]
        host = mysql_config["host"]
        user = mysql_config["user"]
        password = mysql_config["password"]
        port = mysql_config["port"]
        db = "Chickpea"

        mydb = pymysql.connect(host=host,user=user,password=password,port=port,ssl={"ssl_disabled": True})
        mycursor = mydb.cursor()

        mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
        mydb.commit()
        mycursor.execute(f"USE {db}")

        query1 = """
        CREATE TABLE IF NOT EXISTS Authentication (
            SNo INT AUTO_INCREMENT PRIMARY KEY,
            Username VARCHAR(20) NOT NULL UNIQUE,
            Password VARCHAR(255) NOT NULL
        )
        """
        mycursor.execute(query1)
        mydb.commit()

        query2 = """
        CREATE TABLE IF NOT EXISTS Identity (
            Username VARCHAR(20) PRIMARY KEY,
            FirstName VARCHAR(30) NOT NULL,
            LastName VARCHAR(30),
            Email VARCHAR(255) NOT NULL UNIQUE,
            FOREIGN KEY (Username) REFERENCES Authentication(Username)
        )
        """
        mycursor.execute(query2)
        mydb.commit()

        query3 = """
        CREATE TABLE IF NOT EXISTS History (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Username VARCHAR(20) NOT NULL,
            tid VARCHAR(20),
            mtid VARCHAR(255),
            locid VARCHAR(20),
            mlocid VARCHAR(255),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Username) REFERENCES Authentication(Username)
        )
        """
        mycursor.execute(query3)
        mydb.commit()

        query4 = """
        CREATE TABLE IF NOT EXISTS Visitor (
            Visitor_number INT AUTO_INCREMENT PRIMARY KEY,
            Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        mycursor.execute(query4)
        mydb.commit()
        st.success(f"Database '{db}' and tables created successfully.")
        return mydb, mycursor

    except pymysql.Error as e:
        st.error(f"Error: {e}")
        return None, None

# Function to check if a user exists in the Authentication table
def check_user(username, password):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Authentication WHERE Username = %s AND Password = %s", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Function to add a new user to the Authentication and Identity tables
def add_user(username, password, first_name, last_name, email):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Authentication (Username, Password) VALUES (%s, %s)", (username, password))
        cursor.execute("INSERT INTO Identity (Username, FirstName, LastName, Email) VALUES (%s, %s, %s, %s)", (username, first_name, last_name, email))
        conn.commit()
        conn.close()
        return True
    except pymysql.Error as e:
        st.error(f"Error: {e}")
        conn.close()
        return False

# Function to validate email
def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def validate_username_length(username):
    return 1 <= len(username) <= 20

# Function to validate username
def validate_username(username):
    pattern = r"^[a-zA-Z0-9!@#$%^&*_+\-\/?]{1,20}$"
    return re.match(pattern, username) is not None

# Function to validate password length
def validate_password(password):
    return len(password) >= 8

def validate_password_max(password):
    return len(password) <= 20

# Function to connect to the database
def connect_to_db():
    mysql_config = st.secrets["mysql"]
    return pymysql.connect(host=mysql_config["host"],user=mysql_config["user"],password=mysql_config["password"],port=mysql_config["port"],database="Chickpea",ssl={"ssl_disabled": True})

def basic_stats():
    conn3 = connect_to_db()
    cursor3 = conn3.cursor()
    cursor3.execute("SELECT COUNT(*) FROM Authentication")
    total_members = cursor3.fetchone()[0]
    #st.sidebar.subheader(f"Total Members : {total_members}")    #change

    cursor3.execute("SELECT COUNT(*) FROM History")
    total_searches = cursor3.fetchone()[0]
    #st.sidebar.subheader(f"Total Searches : {total_searches}")  #change

    conn3.commit()
    conn3.close()
    return total_members, total_searches

def update_visitor_count():
    conn4 = connect_to_db()
    cursor4 = conn4.cursor()
    if st.session_state.get("first_access",False):
        if st.session_state.current_page !="HOME":
            query = "INSERT INTO Visitor (Timestamp) VALUES (NOW())"
            cursor4.execute(query)
            conn4.commit()
            st.session_state.first_access = False

    query = "SELECT COUNT(*) FROM Visitor"
    cursor4.execute(query)
    result = cursor4.fetchone()
    conn4.close()
    return result[0]

# Streamlit app
def security_login():
    st.title("Login and Registration")

    # Initialize database and tables
    if "db_initialized" not in st.session_state:
        st.session_state.mydb, st.session_state.mycursor = initialize_database()
        if st.session_state.mydb and st.session_state.mycursor:
            st.session_state.db_initialized = True

    # Initialize session state for authentication
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        choice = st.radio("Choose an option", ["Login", "Register"])

        if choice == "Login":
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                if check_user(username, password):
                    st.session_state['authenticated'] = True
                    st.success("Logged in successfully!")
                    st.title(f"Welcome user")
                    conn = connect_to_db()
                    cursor = conn.cursor()
                    #main part to confirm
                    query5 = "SELECT FirstName FROM Identity WHERE Username = %s"
                    cursor.execute(query5, (username,))
                    user_info = cursor.fetchone()
                    if user_info:
                        st.title(f"Hello {user_info[0]}!")
                    else:
                        st.title("User information not found.")
                    query6 = "SELECT LastName FROM Identity WHERE Username = %s"
                    cursor.execute(query6, (username,))
                    user_info = cursor.fetchone()
                    if user_info:
                        st.title(f"Hello {user_info[0]}!")
                    else:
                        st.title("User information not found.")
                    query7 = "SELECT Email FROM Identity WHERE Username = %s"
                    cursor.execute(query7, (username,))
                    user_info = cursor.fetchone()
                    if user_info:
                        st.title(f"Hello {user_info[0]}!")
                    else:
                        st.title("User information not found.")
                else:
                    st.error("Invalid username or password")

        elif choice == "Register":
            st.subheader("Register")
            username = st.text_input("Username (max 20 chars, allowed: a-z, A-Z, 0-9, !@#$%^&*_+-/?)")
            password = st.text_input("Password (min 8 chars)", type="password")
            first_name = st.text_input("First Name (max 30 chars)")
            last_name = st.text_input("Last Name (max 30 chars, optional)", "")
            email = st.text_input("Email")

            if st.button("Register"):
                if not validate_username_length(username):
                    st.error("Username must be between 1 and 20 characters long.")
                elif not validate_password_max(password):
                    st.error("Password must be less than 20 characters long.")
                elif not validate_username(username):
                    st.error("Invalid username. Only a-z, A-Z, 0-9, and !@#$%^&*_+-/? are allowed.")
                elif not validate_email(email):
                    st.error("Invalid email. Must contain @ and .com.")
                elif not validate_password(password):
                    st.error("Password must be at least 8 characters long.")
                else:
                    if add_user(username, password, first_name, last_name, email):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username or email already exists.")

    else:
        st.subheader("Search Page")
        st.write("Welcome to the Search Page!")
    return


def login_interface():
    col1, col2, col3 = st.columns([1,3,1])
    con=col2.container(border=True)
    with con:
            c1,c2,c3=st.columns(3)
            with c2:
                st.markdown("<h1 style='text-align: center;'>Login</h1>", unsafe_allow_html=True)

            col2, col3 = st.columns(2,gap="small", vertical_alignment="center")
            with col2:
                st.markdown("<h3 style='text-align: center;'>Enter Username</h3>", unsafe_allow_html=True)
            with col3:
                username = st.text_input("Username", key="login_username", label_visibility="collapsed")
        
            col2, col3 = st.columns(2,gap="small", vertical_alignment="center")
            with col2:
                st.markdown("<h3 style='text-align: center;'>Enter Password</h3>", unsafe_allow_html=True)
            with col3:
                password = st.text_input("Password", key="login_password", type="password", label_visibility="collapsed")
        
            col2, col3, col4= st.columns([1, 2, 1,],gap="small", vertical_alignment="center")
            c1,c2,c3=st.columns([1,99,1],gap="small", vertical_alignment="center")
            with col3:
                if st.button("Continue", use_container_width=True):
                    st.success("Checking credentials")
                    if check_user(username, password):
                        st.success("Logged in successfully!")
                        c2.write("By clicking Confirm you agree to the Code of Conduct. utilize the true potential of this amazing Explorer")
                        st.session_state["logged_in"] = True
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username
                        #st.session_state['expander_state'] = False
                        if st.session_state.get("redirect_to_login", False):
                            st.session_state["redirect_to_login"] = False
                            #st.switch_page("pages/Search.py")
                            #time.sleep(2)
                            #st.rerun()
                    else:
                        st.error("Invalid username or password")

def register_interface():
    col1, col2, col3 = st.columns([1,3,1])
    con=col2.container(border=True)
    with con:
            c1,c2,c3=st.columns(3)
            with c2:
                st.markdown("<h1 style='text-align: center;'>Register</h1>", unsafe_allow_html=True)
        
            col2, col3 = st.columns(2,gap="small", vertical_alignment="center")
            with col2:
                st.markdown("<h3 style='text-align: center;'>First Name</h3>", unsafe_allow_html=True)
                fname = st.text_input("FirstName", label_visibility="collapsed")
            with col3:
                st.markdown("<h3 style='text-align: center;'>Last Name</h3>", unsafe_allow_html=True)
                lname = st.text_input("LastName", label_visibility="collapsed")
        
            col2, col3 = st.columns(2,gap="small", vertical_alignment="center")
            with col2:
                st.markdown("<h3 style='text-align: center;'>Create Username</h3>", unsafe_allow_html=True)
            with col3:
                username1 = st.text_input("Username", label_visibility="collapsed")
            
            col2, col3 = st.columns(2,gap="small", vertical_alignment="center")
            with col2:
                st.markdown("<h3 style='text-align: center;'>Enter Email</h3>", unsafe_allow_html=True)
            with col3:
                email1 = st.text_input("Email", label_visibility="collapsed")
        
            col2, col3 = st.columns(2,gap="small", vertical_alignment="center")
            with col2:
                st.markdown("<h3 style='text-align: center;'>Create Password</h3>", unsafe_allow_html=True)
            with col3:
                password1 = st.text_input("Password1", type="password", label_visibility="collapsed")

            col2, col3 = st.columns(2,gap="small", vertical_alignment="center")
            with col2:
                st.markdown("<h3 style='text-align: center;'>Confirm Password</h3>", unsafe_allow_html=True)
            with col3:
                password2 = st.text_input("Password2", type="password", label_visibility="collapsed")
        
            col2, col3, col4= st.columns([1, 2, 1,],gap="small", vertical_alignment="center")
            if col3.button("Register", use_container_width=True):
                if password1 == password2:
                    st.success("Password checked")
                    if not validate_username_length(username1):
                        st.error("Username must be between 1 and 20 characters long.")
                    elif not validate_password_max(password1):
                        st.error("Password must be less than 20 characters long.")
                    elif not validate_username(username1):
                        st.error("Invalid username. Only a-z, A-Z, 0-9, and !@#$%^&*_+-/? are allowed.")
                    elif not validate_email(email1):
                        st.error("Invalid email. Must contain @ .com .ac .in ")
                    elif not validate_password(password1):
                        st.error("Password must be at least 8 characters long.")
                    else:
                        if add_user(username1, password1, fname, lname, email1):
                            st.success("Registration successful! Please login.")
                            st.session_state.current_interface='login'
                            st.rerun()
                        else:
                            st.error("Username or email already exists.")
                else:
                    st.warning("Passwords do not match. Please try again.")

def login_page():
    if 'current_interface' not in st.session_state:
        st.session_state.current_interface = None

    con=st.container(border=False)
    with con:
        col1,col2=st.columns([4,6])
        with open("logo1.png", "rb") as img_file:
            img_data = img_file.read()
        img_login=img_to_base64(img_data)
        col1.image(f"data:image/png;base64,{img_login}", use_container_width=True)
        with col2:
            st.markdown("<h1 style='text-align: center;'>WELCOME</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Log in to the CHICKPEA OMICS EXPLORER to explore the world of Chickpea Genomics and Proteomics</h3>", unsafe_allow_html=True)
    #st.title("Security")

    if st.session_state.get("logged_in", False) and st.session_state.get("authenticated", False):
        username = st.session_state.get('username')
        details_button = st.expander("⠀", expanded=True)
        col1, col2, col4, col6, col7 = st.columns([1, 2, 1, 2, 1])
        history_button = col2.button("History", key="history_login")
        logout_button = col6.button("Logout", key="logout_login")
        conn2 = connect_to_db()
        cursor2 = conn2.cursor()
        query = "SELECT Username,FirstName, LastName, Email FROM Identity WHERE Username = %s"
        cursor2.execute(query, (username,))
        result = cursor2.fetchone()
        with details_button:
                col1,col2=st.columns(2)
                with col1:
                    st.subheader(f"**Name**: {result[1]} {result[2]}")
                    st.subheader(f"**Username**: {result[0]}")
                with col2:
                    st.subheader(f"**Email**: {result[3]}")
        cursor2.execute("SELECT COUNT(*) FROM History WHERE Username = %s", (username,))
        user_searches = cursor2.fetchone()[0]
        st.subheader(f"**Total Searches** for **{username}**: **{user_searches}**")
        conn2.commit()
        conn2.close()

        if history_button:
            conn2 = connect_to_db()
            cursor2 = conn2.cursor()
            con = st.container(border=True)
            con.write(f"**History** for **{username}** :-")
            cursor2.execute("SELECT * FROM History WHERE Username = %s", (username,))
            rows = cursor2.fetchall()
            column_names = [desc[0] for desc in cursor2.description]
            df = pd.DataFrame(rows, columns=column_names)
            con.dataframe(df, use_container_width=True)
            conn2.close()

        # Handle logout
        if logout_button:
            st.session_state["logged_in"] = False
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            st.success("You have been logged out successfully!")
            time.sleep(2)
            st.rerun()

    else:
        # User is not logged in, show login and register options
        col1, col2, col4, col6, col7 = st.columns([1, 2, 1, 2, 1])
        login_button = col2.button("Login")
        register_button = col6.button("Register")

        if login_button:
            st.session_state.current_interface = 'login'

        if register_button:
            st.session_state.current_interface = 'register'

        # Show the appropriate interface based on the current state
        if st.session_state.current_interface == 'login':
            login_interface()
            if st.session_state.get("authenticated", False):
                col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 2, 1, 1, 1])
                col4.button("Confirm")
        elif st.session_state.current_interface == 'register':
            register_interface()
    return

if __name__ == "__main__":
    initialize_database()
    login_page()