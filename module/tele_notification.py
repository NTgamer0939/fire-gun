import requests
import time

def send_message(message):
    _token = "8367989045:AAFP6fVsVBdMBvYfjJh_4QKOJMEM9nyJoGs"

    # baseUrl = "https://api.telegram.org/bot8367989045:AAFP6fVsVBdMBvYfjJh_4QKOJMEM9nyJoGs/getUpdates"

    chatID = "7662495194"
    
    url = f"https://api.telegram.org/bot{_token}/sendMessage?chat_id={chatID}/&text={message}"
    try:
        req = requests.get(url)
    except Exception as e:
        print(e)