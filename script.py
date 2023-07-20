import streamlit as st
import pandas as pd
import numpy as np
import re
import hashlib
import secrets
from datetime import datetime, timedelta
from filelock import FileLock

# Generate a DataFrame for the week
index = pd.date_range(start='2023-07-22', end='2023-07-29', freq='H')
df = pd.DataFrame(np.full((len(index), 4), None), index=index, columns=['Door (Left)', 'Door (Right)', 'Window (Left)', 'Window (Right)'])

# Load the current bookings and audit log from csv files
try:
    df = pd.read_csv('bookings.csv', index_col=0, parse_dates=True)
    audit_log = pd.read_csv('audit_log.csv', index_col=0, parse_dates=['timestamp'])
except FileNotFoundError:
    df.to_csv('bookings.csv')
    audit_log = pd.DataFrame(columns=['timestamp', 'code', 'name', 'station', 'start', 'duration', 'action'])
    audit_log.to_csv('audit_log.csv')

def validate_name(name):
    if len(name) < 3 or len(name) > 20:
        return "Name must be between 3 and 20 characters long."
    if not re.match(r"^[a-zA-Z0-9_.,!'$]*$", name):
        return "Name contains invalid characters. Only numbers, letters and _ . , ! ' $ are allowed."
    return None

def is_slot_available(station, start, duration):
    end = start + pd.DateOffset(hours=duration - 1) # Excluding the end hour
    if df.loc[start:end, station].isna().all():
        return True
    else:
        return False

def validate_booking_time(start, duration):
    now = pd.to_datetime(datetime.now())
    end = start + pd.DateOffset(hours=duration - 1) # Excluding the end hour
    if now > start:
        return "Booking time is in the past. Please select a future time."
    return None

def book_slot():
    st.subheader('Book a Slot')
    station = st.selectbox('Select a station:', df.columns, key='book_station')
    today = datetime.today().date()
    event_start = datetime(2023, 7, 22).date()
    event_end = datetime(2023, 7, 29).date()
    min_date = max(today, event_start)
    col1, col2 = st.columns(2)
    with col2:
        date = st.date_input('Select a date:', value=min_date, min_value=min_date, max_value=event_end, key='book_date')
    with col1:
        hour = st.selectbox('Select a start hour:', [f'{i:02d}:00' for i in range(24)], key='book_hour')
    start = pd.to_datetime(f'{date} {hour}:00')
    duration = st.slider('Select duration (in hours):', 1, 8, key='book_duration')
    name = st.text_input('Enter your name:', key='book_name')
    error_message = validate_name(name)
    time_error_message = validate_booking_time(start, duration)
    if error_message:
        st.error(error_message)
    elif time_error_message:
        st.error(time_error_message)
    elif st.button('Book slot'):
        lock = FileLock("bookings.csv.lock")
        with lock:
            if is_slot_available(station, start, duration):
                end = start + pd.DateOffset(hours=duration - 1) # Excluding the end hour
                df.loc[start:end, station] = name
                df.to_csv('bookings.csv')
                
                # Generate a unique booking code and save it to the audit log
                code = secrets.token_hex(3) # 6-character code
                timestamp = datetime.now()
                audit_log.loc[len(audit_log)] = [timestamp, code, name, station, start, duration, 'Booked']
                audit_log.to_csv('audit_log.csv')
                
                st.success(f'Your slot has successfully been booked! Your booking code is {code}. It can be used to cancel your booking.')
            else:
                st.error('This slot has already been booked. Please select another slot.')

def remove_slot():
    st.subheader('Remove a Slot')
    code = st.text_input('Enter your booking code:', key='remove_code')
    if st.button('Remove slot'):
        lock = FileLock("bookings.csv.lock")
        with lock:
            if code in audit_log['code'].values:
                booking = audit_log[audit_log['code'] == code]
                station = booking['station'].values[0]
                start = pd.to_datetime(booking['start'].values[0])
                duration = int(booking['duration'].values[0])  # Convert to Python int
                end = start + pd.DateOffset(hours=duration - 1) # Excluding the end hour
                df.loc[start:end, station] = np.nan
                df.to_csv('bookings.csv')
                
                # Add the removal to the audit log
                timestamp = datetime.now()
                audit_log.loc[len(audit_log)] = [timestamp, np.nan, booking['name'].values[0], station, start, duration, 'Removed']
                audit_log.to_csv('audit_log.csv')
                
                st.success('The selected slot has been removed.')
            else:
                st.error('Invalid booking code.')

def view_bookings():
    st.subheader('Current Bookings')
    # Only display future slots and replace NaN with empty string
    future_df = df[df.index >= datetime.now()].fillna('')
    st.dataframe(future_df.style.set_properties(**{'text-align': 'center'}).highlight_null('white'))

def view_audit_log():
    st.subheader('View Audit Log')
    password = st.text_input('Enter the admin password:', type='password')
    if st.button('Show Audit Log'):
        if hashlib.sha256(password.encode()).hexdigest() == '22b3e6b61e76c2636c25ce763072207d687910b4cf960127158e7bcc485d8305':
            st.subheader('Audit Log')
            st.dataframe(audit_log.sort_values(by='timestamp'))  # Show audit log in chronological order
        else:
            st.error('Invalid password.')

st.title('ESA Summer 2023 Streaming Stations')
book_slot()
remove_slot()
view_bookings()
view_audit_log()