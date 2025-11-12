import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()  # Loads the .env file

def connect_db():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except mysql.connector.Error as err:
        print("Error:", err)
        return None
