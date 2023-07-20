ESA Summer 2023 Streaming Stations Booking App
This repository contains a Streamlit application for managing bookings of streaming stations at the "ESA Summer 2023" event.

Features
The application provides the following features:

Book a Slot: Users can book a slot at one of the stations for a specific date and time, and for a specified duration.

Remove a Slot: Users can remove their booking by entering their unique booking code.

View Current Bookings: Users can view all current and future bookings.

View Audit Log: Administrators can view an audit log of all bookings and removals.

Installation
The application requires Python 3.7 or higher, along with several Python packages.

You can install the required Python packages using pip:

shell
Copy code
pip install streamlit pandas numpy filelock
Running the Application
To run the application, navigate to the directory containing the Streamlit script and run the following command:

shell
Copy code
streamlit run script.py
Replace script.py with the name of your Streamlit script. The application will then be accessible in your web browser at localhost:8501.

Data Storage
The application stores booking data and an audit log in CSV files. If these files do not exist when the application starts, they will be created automatically.

Contributing
Contributions are welcome! Please submit a pull request or create an issue to discuss proposed changes.

