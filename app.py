import streamlit as st
from services.openai_service import parse_event_details, extract_text_from_image
from services.google_calendar_service import get_calendar_list, create_event
import json

st.title('간편 구글 캘린더 등록 서비스')

# 유저로부터 API 키 입력 받기
openai_api_key = st.text_input('OpenAI API 키를 입력하세요', type='password')
google_service_account_json = st.file_uploader('Google 서비스 계정 JSON 파일을 업로드하세요', type='json')

if openai_api_key and google_service_account_json:
    st.session_state['openai_api_key'] = openai_api_key
    st.session_state['google_service_account_info'] = json.load(google_service_account_json)

    # 구글 캘린더 선택
    calendars = get_calendar_list(st.session_state['google_service_account_info'])
    calendar_options = {calendar['summary']: calendar['id'] for calendar in calendars}
    calendar_name = st.selectbox('캘린더를 선택하세요:', list(calendar_options.keys()))

    # 일정 정보 입력
    event_input_type = st.radio("일정 정보 입력 방식 선택:", ("텍스트", "이미지"))

    if event_input_type == "텍스트":
        event_text = st.text_area('일정 정보를 입력하세요:')

        if st.button('일정 등록'):
            parsed_event = parse_event_details(event_text, st.session_state['openai_api_key'])
            event_data = {
                'summary': parsed_event['summary'],
                'start': {'dateTime': parsed_event['start'], 'timeZone': 'Asia/Seoul'},
                'end': {'dateTime': parsed_event['end'], 'timeZone': 'Asia/Seoul'},
            }

            event = create_event(calendar_options[calendar_name], event_data, st.session_state['google_service_account_info'])
            st.success(f"이벤트가 등록되었습니다: {event.get('htmlLink')}")

    elif event_input_type == "이미지":
        event_image = st.file_uploader('일정 정보가 담긴 이미지를 업로드하세요', type=['jpg', 'jpeg', 'png'])

        if event_image and st.button('일정 등록'):
            image_bytes = event_image.getvalue()
            extracted_text = extract_text_from_image(image_bytes, st.session_state['openai_api_key'])
            parsed_event = parse_event_details(extracted_text, st.session_state['openai_api_key'])
            event_data = {
                'summary': parsed_event['summary'],
                'start': {'dateTime': parsed_event['start'], 'timeZone': 'Asia/Seoul'},
                'end': {'dateTime': parsed_event['end'], 'timeZone': 'Asia/Seoul'},
            }

            event = create_event(calendar_options[calendar_name], event_data, st.session_state['google_service_account_info'])
            st.success(f"이벤트가 등록되었습니다: {event.get('htmlLink')}")
else:
    st.warning('API 키를 입력하고 Google 서비스 계정 파일을 업로드하세요.')
