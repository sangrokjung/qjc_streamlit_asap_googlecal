import streamlit as st
from services.openai_service import parse_event_details, extract_text_from_image
from services.google_calendar_service import get_calendar_list, create_event, authorize_google, get_credentials_from_code, save_credentials_to_session, get_credentials
import os
from dotenv import load_dotenv

load_dotenv()

st.title('간편 구글 캘린더 등록 서비스')

# 환경 변수에서 API 키 가져오기
openai_api_key = os.getenv('OPENAI_API_KEY')
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

if not openai_api_key:
    openai_api_key = st.text_input('OpenAI API 키를 입력하세요', type='password')
if not google_client_id:
    google_client_id = st.text_input('Google Client ID를 입력하세요')
if not google_client_secret:
    google_client_secret = st.text_input('Google Client Secret을 입력하세요', type='password')

if openai_api_key and google_client_id and google_client_secret:
    st.session_state['openai_api_key'] = openai_api_key
    st.session_state['google_client_id'] = google_client_id
    st.session_state['google_client_secret'] = google_client_secret

    # 구글 로그인 및 권한 부여
    credentials = get_credentials()
    if not credentials:
        query_params = st.experimental_get_query_params()
        if 'code' in query_params:
            code = query_params['code'][0]
            try:
                credentials = get_credentials_from_code(
                    st.session_state['state'], code, 
                    st.session_state['google_client_id'], st.session_state['google_client_secret']
                )
                save_credentials_to_session(credentials)
                st.experimental_rerun()
            except Exception as e:
                st.error(f"인증 중 오류가 발생했습니다: {e}")
        else:
            try:
                auth_url = authorize_google(st.session_state['google_client_id'], st.session_state['google_client_secret'])
                st.markdown(f'[구글 로그인하기]({auth_url})')
            except Exception as e:
                st.error(f"구글 로그인 URL 생성 중 오류가 발생했습니다: {e}")
            st.stop()

    # 구글 캘린더 선택
    try:
        calendars = get_calendar_list(credentials)
        calendar_options = {calendar['summary']: calendar['id'] for calendar in calendars}
        calendar_name = st.selectbox('캘린더를 선택하세요:', list(calendar_options.keys()))
    except Exception as e:
        st.error(f"캘린더 목록을 불러오는 중 오류가 발생했습니다: {e}")

    # 일정 정보 입력
    event_input_type = st.radio("일정 정보 입력 방식 선택:", ("텍스트", "이미지"))

    if event_input_type == "텍스트":
        event_text = st.text_area('일정 정보를 입력하세요:')

        if st.button('일정 등록'):
            try:
                parsed_event = parse_event_details(event_text, st.session_state['openai_api_key'])
                event_data = {
                    'summary': parsed_event['summary'],
                    'start': {'dateTime': parsed_event['start'], 'timeZone': 'Asia/Seoul'},
                    'end': {'dateTime': parsed_event['end'], 'timeZone': 'Asia/Seoul'},
                }
                event = create_event(calendar_options[calendar_name], event_data, credentials)
                st.success(f"이벤트가 등록되었습니다: {event.get('htmlLink')}")
            except Exception as e:
                st.error(f"일정 등록 중 오류가 발생했습니다: {e}")

    elif event_input_type == "이미지":
        event_image = st.file_uploader('일정 정보가 담긴 이미지를 업로드하세요', type=['jpg', 'jpeg', 'png'])

        if event_image and st.button('일정 등록'):
            try:
                image_bytes = event_image.getvalue()
                extracted_text = extract_text_from_image(image_bytes, st.session_state['openai_api_key'])
                parsed_event = parse_event_details(extracted_text, st.session_state['openai_api_key'])
                event_data = {
                    'summary': parsed_event['summary'],
                    'start': {'dateTime': parsed_event['start'], 'timeZone': 'Asia/Seoul'},
                    'end': {'dateTime': parsed_event['end'], 'timeZone': 'Asia/Seoul'},
                }
                event = create_event(calendar_options[calendar_name], event_data, credentials)
                st.success(f"이벤트가 등록되었습니다: {event.get('htmlLink')}")
            except Exception as e:
                st.error(f"일정 등록 중 오류가 발생했습니다: {e}")
else:
    st.warning('OpenAI API 키와 Google Client ID, Client Secret을 입력하세요.')
