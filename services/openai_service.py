import openai
import base64
import requests

def parse_event_details(text, api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # 또는 gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts event details from text."},
            {"role": "user", "content": f"Extract event details from the following text:\n\n{text}"}
        ]
    )
    parsed_text = response['choices'][0]['message']['content'].strip()
    lines = parsed_text.split('\n')
    
    if len(lines) < 3:
        raise ValueError("파싱된 텍스트가 이벤트 요건을 충족하지 않습니다.")
    
    return {
        'summary': lines[0],
        'start': lines[1],
        'end': lines[2]
    }

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def extract_text_from_image(image_bytes, api_key):
    base64_image = encode_image(image_bytes)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please extract the text from this image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    extracted_text = response.json()['choices'][0]['message']['content'].strip()
    return extracted_text
