from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_calendar_list(service_account_info):
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=credentials)
    calendar_list = service.calendarList().list().execute()
    return calendar_list.get('items', [])

def create_event(calendar_id, event_data, service_account_info):
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=credentials)
    event = service.events().insert(calendarId=calendar_id, body=event_data).execute()
    return event
