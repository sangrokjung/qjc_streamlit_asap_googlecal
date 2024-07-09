from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import streamlit as st
import os
import json

SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = os.getenv('REDIRECT_URI', "http://localhost:8501")  # 기본값은 localhost

def get_credentials():
    if 'credentials' in st.session_state:
        credentials = Credentials.from_authorized_user_info(st.session_state['credentials'], SCOPES)
        return credentials
    return None

def save_credentials_to_session(credentials):
    st.session_state['credentials'] = json.loads(credentials.to_json())

def get_calendar_list(credentials):
    service = build('calendar', 'v3', credentials=credentials)
    calendar_list = service.calendarList().list().execute()
    return calendar_list.get('items', [])

def create_event(calendar_id, event_data, credentials):
    service = build('calendar', 'v3', credentials=credentials)
    event = service.events().insert(calendarId=calendar_id, body=event_data).execute()
    return event

def authorize_google(client_id, client_secret):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    st.session_state['state'] = state
    return authorization_url

def get_credentials_from_code(state, code, client_id, client_secret):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state
    )
    flow.fetch_token(code=code)
    return flow.credentials
