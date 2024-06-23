import json

import streamlit as st
from streamlit_calendar import calendar

with open('calendar_options.json') as f:
    calendar_options = json.load(f)
if not 'last_click' in st.session_state:
    st.session_state['last_click'] = ''

def erase_date():
    del st.session_state['starting_day']
    del st.session_state['starting_day']

calendar_events = [
    {
        "title": "Jhon does vacation",
        "start": "2024-04-01T08:30:00",
        "end": "2024-05-01T10:30:00",
        "resourceId": "a",
    },
]
custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
"""

calendar_widget = calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)
if 'callback' in calendar_widget and calendar_widget['callback'] == ('dateClick'):

    raw_date = calendar_widget['dateClick']['date']
    if raw_date != st.session_state['last_click']:
        st.session_state.date['last_click'] = calendar_widget['dateClick']['date']


    date = calendar_widget['dateClick']['date'].split('T')[0]
    st.write(date)
    st.write(calendar_widget['dateClick']['date'])
    if not 'entry_date' in st.session_state:
        st.session_state['starting_day'] = date
        st.warning(f"starting vacation day selected {date}")
    else:
        st.session_state['ending_day'] = date
        start_day = st.session_state['starting_day']
        cols = st.columns([0.7, 0.3])
        with cols[0]:
            st.warning(f"starting vacation day selected {start_day}")
        with cols[1]:
            st.button('Erase', use_container_width=True, on_click=erase_date)
        cols = st.columns([0.7, 0.3])
        with cols[0]:
            st.warning(f"ending vacation day selected {date}")
        with cols[1]:
            st.button('Add vacation', use_container_width=True)


st.write(calendar_widget)

