from time import sleep
import json

import streamlit as st
from streamlit_calendar import calendar
from sqlalchemy.sql.functions import user

import pandas as pd

from crud import reads_all_users, creates_users, updates_user, deletes_user, reads_user_by_id

def login():
    users = reads_all_users()
    users = {user.name: user for user in users}
    st.write(users)
    with st.container(border=True):
        st.markdown("welcome to the vacation webapp")
        user_name = st.selectbox("Please select a user", users.keys())
        password = st.text_input("Please type your password", type='password')
        if st.button("Access"):
            user = users[user_name]
            if user.check_password(password):
                st.success("Welcome {}".format(user.name))
                st.session_state['Logged in'] = True
                st.session_state['user'] = user
                sleep(1)
                st.rerun()
            else:
                st.error("Wrong password")

def management_page():
    st.markdown("User management page")
    with st.sidebar:
        user_management_tab()

    user = reads_all_users()

    for user in users:
        with st.container(border=True):
            cols = st.columns(2)
            days_to_require = user.days_to_require()
            with cols[0]:
                if days_to_require > 40:
                    st.error(f"### {user.name}")
                else:
                    st.markdown(f"### {user.name}")
            with cols[1]:
                if days_to_require > 40:
                    st.error(f"### days to require: {days_to_require}")
                else:
                    st.markdown(f"### days to require: {days_to_require}")

def user_management_tab():
    tab_create, tab_read, tab_update, tab_delete = st.tabs(
        ['create', 'read', 'update', 'delete']
    )
    users = reads_all_users()
    with tab_read:
        users_data = [{
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'admin_access': user.admin_access,
            'entry_date': user.entry_date,
        } for user in users]
        st.dataframe(pd.DataFrame(users_data).set_index('id'))

    with tab_create:
        name = st.text_input("User name")
        password = st.text_input("User password")
        email = st.text_input("User email")
        admin_access = st.text_input("Do you have admin access?", value=False)
        entry_date = st.text_input("Enter the entry date on the company (YYYY-MM-DD)")

        if st.button("Create"):
            creates_user(
                name=name,
                email=email,
                password=password,
                admin_access=admin_access,
                entry_date=entry_date
            )
            st.rerun()

    with tab_update:
        users_dict = {user.name: user for user in users}
        user_name = st.selectbox("Please select a user to update", users_dict.keys())
        user = users_dict[user_name]
        name = st.text_input("User name to update", value=user.name)
        password = st.text_input("User password to update", value='0000')
        email = st.text_input("User email to update", value=user.email)
        admin_access = st.text_input("Do you have admin access?", value=user.admin_access)
        entry_date = st.text_input("Enter the entry date on the company (YYYY-MM-DD)", value=user.entry_date)

        if st.button("Update"):
            if password == '0000':
                updates_user(
                    id=user.id,
                    name=name,
                    email=email,
                    admin_access=admin_access,
                    entry_date=entry_date,
                )
            else:
                updates_user(
                    id=user.id,
                    name=name,
                    email=email,
                    password=password,
                    admin_access=admin_access,
                    entry_date=entry_date,
            )
            st.rerun()

        with tab_delete:
            users_dict = {user.name: user for user in users}
            user_name = st.selectbox("Please select a user to delete", users_dict.keys())
            user = users_dict[user_name]
            if st.button("Delete"):
                deletes_user(user.id)
                st.rerun()

def add_vacation(user, start_vacation, end_vacation):
    user.add_vacation(start_vacation, end_vacation)

def check_and_add_vacation(start_vacation, end_vacation):
    user = st.session_state['user']
    total_days = (datetime.strptime(end_vacation, "%Y-%m-%d") - datetime.strptime(start_vacation, "%Y-%m-%d")).days + 1
    if total_days < 5:
        st.error("days to require less than 5")
    elif user.days_to_require() < total_days:
        st.error(f"user required {total_days} days but has only {user.days_to_require} to require ")
    else:
        user.add_vacation(start_vacation, end_vacation)
        erase_date()

def erase_date():
    del st.session_state['start_vacation']
    del st.session_state['end_vacation']


def calendar_page():

    with open('calendar_options.json') as f:
        calendar_options = json.load(f)

    user = reads_all_users()
    calendar_events = []
    for user in users:
        calendar_events.extend(user.vacation_list())

    user = st.session_state['user']

    with st.expander("days to require"):
        user = reads_user_by_id(user.id)
        days_to_require = user.days_to_require()
        st.markdown(f"the user {user.name} has **{days_to_require}** days to require")

    calendar_events = [
        {
            "title": "John does vacation",
            "start": "2024-04-01T08:30:00",
            "end": "2024-05-01T10:30:00",
            "resourceId": "a",
        }
    ]

    custom_css = """
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
            st.session_state['start_vacation'] = date
            st.warning(f"starting vacation day selected {date}")
        else:
            st.session_state['end_vacation'] = date
            start_vacation = st.session_state['start_vacation']
            cols = st.columns([0.7, 0.3])
            with cols[0]:
                st.warning(f"starting vacation day selected {start_vacation}")
            with cols[1]:
                st.button('Erase', use_container_width=True, on_click=erase_date)
            cols = st.columns([0.7, 0.3])
            with cols[0]:
                st.warning(f"ending vacation day selected {date}")
            with cols[1]:
                st.button('Add vacation', use_container_width=True, on_click=check_and_add_vacation, args=start_vacation, date)

    st.write(calendar_widget)

def main_page():
    st.title("Welcome to the vacation webapp")
    st.divider()

    user = st.session_state['user']
    if user.admin_access:
        st.columns(2)
        with cols[0]:
            if st.button("Access user management", use_container_width=True):
                st.session_state["user_management_page"]=True
                st.rerun()
        with cols[1]:
            if st.button("Access calendar",use_container_width=True):
                st.session_state["user_management_page"]=False
                st.rerun()

    if st.session_state["user_management_page"]:
        management_page()

    else:
        calendar_page()
def main():

    if not 'Logged in' in st.session_state:
        st.session_state['Logged in'] = False
    if not 'user_management_page' in st.session_state:
        st.session_state['user_management_page'] = False
    if not 'last_click' in st.session_state:
        st.session_state['last_click'] = ''

    if not st.session_state['Logged in']:
        login()
    else:
        main_page()

if __name__ == '__main__':
    main()
