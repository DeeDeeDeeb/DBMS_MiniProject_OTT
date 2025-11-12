# 🎬 OTT Database Management Platform

A mini-project built using **Python** and **MySQL**, designed to manage OTT (Over-The-Top) platform data such as users, subscriptions, shows, and watch history.  
This project demonstrates database connectivity, CRUD operations, and a GUI-based interface for interaction.

---

## 🚀 Features

- 📁 **Database Integration:** Connects to a MySQL database (`ott`) using `mysql.connector`.
- 🧩 **User Management:** Add, view, update, and delete user details.
- 🎥 **Content Management:** Manage OTT shows, movies, and subscriptions.
- 🖥️ **GUI Interface:** Built with Python (`tkinter` or similar) for a smooth front-end experience.
- 🔒 **Secure Connection:** Database credentials are stored safely in a `.env` file.
- ⚙️ Automation: Includes MySQL triggers, functions, and procedures for real-time data operations.

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/dbms-mini-project.git
cd dbms-mini-project
```
### 2️⃣ Install dependencies
```bash
pip install mysql-connector-python python-dotenv
```
### 3️⃣ Set up the .env file
```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=ott
```
### 4️⃣ Run the project
```bash
python ott_gui.py
```

### Folder Structure
```bash
DBMS_Mini_Project/
│
├── db_connect.py      # Handles MySQL database connection
├── ott_gui.py         # GUI logic and CRUD operations
├── .env               # Contains sensitive DB credentials (not uploaded)
├── .gitignore         # Ignore unnecessary files
└── README.md          # Project documentation
```

