# Vacation Management App
The Vacation Management App is a Python-based web application built using Streamlit. It simplifies vacation tracking, user management, and provides an interactive calendar for better organization.

# Features
## User Authentication:
Users can log in using their credentials.
Password validation ensures secure access.
## User Management:
Admin users can create, read, update, and delete user records.
User details include name, email, admin access, and entry date.
## Vacation Tracking:
Users can add vacation periods (start and end dates).
The app checks if the requested vacation days are within the user’s available balance.
Color-coded indicators highlight users with low available vacation days.
## Interactive Calendar:
The calendar displays vacation events.
Users can click on dates to select start and end dates for vacation requests.
# Installation
Clone the Repository:
git clone https://github.com/olivialrp/vacation-management-app.git

## Install Dependencies:
Navigate to the project folder and install the required dependencies:
cd vacation-management-app
pip install -r requirements.txt

# Run the App:
streamlit run vacation_app.py

# Usage
## Log In:
Launch the app and log in using valid credentials.
Admin users can access user management features.
## User Management:
Create, update, or delete user records as needed.
Modify user details (name, email, etc.) or reset passwords.
## Vacation Requests:
Click on the interactive calendar to select start and end dates for vacation requests.
The app validates vacation days against the user’s available balance.
