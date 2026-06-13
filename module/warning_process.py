import base64
import datetime
import cv2
from module import tele_notification
import time
from module.connectDB import ConnectDB
import requests
import os
import threading
import base64

cursor = None
conn = None

link = 'http://localhost:3000'

busy = False

def keepDatabaseAlive():
    while True:
        cursor.execute('SELECT 1')
        time.sleep(10000)

def connectDatabase():
    global cursor, conn
    print("Connecting to database...")
    DB = ConnectDB()
    cursor = DB.cursor
    conn = DB.conn
    print("Connected to database successfully!")
    threading.Thread(target=keepDatabaseAlive).start()

def get_current_time():
    now = datetime.datetime.now()
    dateTime = {
        'day': now.day,
        'month': now.month,
        'year': now.year,
        'hour': now.hour,
        'minute': now.minute,
        'second': now.second
    }
    return dateTime

def query(command, val=None):
    try:
        cursor.fetchall()
        if val is not None:
            cursor.execute(command, val)
            conn.commit()
        time.sleep(0.1)
    except Exception as e:
        print(f"Error occurred while executing query: {e}")
        connectDatabase()
        return False
    print(f"Executed query: {command} with val: {val}")
    return True

# def query(command, val = None):
#     global busy, cursor, conn
#     error = 0
#     success = False
#     while busy:
#         time.sleep(0.1)
#     busy = True
#     try:
#         cursor.fetchall()
#         if val is not None:
#             cursor.execute(command, val)
#             conn.commit()
#             success = True
#         else:
#             cursor.execute(command)
#             conn.commit()
#             success = True
#         time.sleep(0.1)
#     except Exception as e:
#         print(f"Error occurred while executing query ({error}): {e}")
#         connectDatabase()
#         query(command=command, val=val)
#         error += 1
#         success = False
#     finally:
#         if success:
#             busy = False
#             print(f"Executed query: {command} with val: {val}")
#     if cursor.with_rows == False:
#         return cursor.lastrowid
#     elif cursor.with_rows:
#         return cursor.fetchall()
#     print("Failed to execute query after 3 attempts.")
#     return None

# def request_to_host(package, data):
#     API_KEY = "010818064018thilamthidang"
#     url = f"http://logforfiregun.click/api/{API_KEY}/{package}"
#     try:
#         response = requests.post(url, data=data)
#         if response.status_code == 200:
#             print("Request successful")
#         else:
#             print(f"Request failed with status code: {response.status_code}")
#     except Exception as e:
#         print(f"Error occurred while sending request: {e}")

def send_log_to_database(img):
    is_mysql_done = False

    dateTime = get_current_time()

    fileName = int(time.time())
    sql = "INSERT INTO log (datetime, image) VALUES (%s, %s)"
    val = (f"{dateTime['year']}-{dateTime['month']}-{dateTime['day']} {dateTime['hour']}:{dateTime['minute']}:{dateTime['second']}", fileName)

    def send_mysql():
        while not is_mysql_done:
            is_mysql_done = query(sql, val)
            time.sleep(1)

    threading.Thread(target=send_mysql, args=(sql, val))

    # Cache
    os.makedirs("images", exist_ok=True)
    image_path = os.path.join("images", f"{fileName}.jpg")
    cv2.imwrite(image_path, img)

    imageBase64 = encode_base64(img)

    data = {
        "fileName": str(fileName),
        "image": imageBase64
    }

    requests.post(link + '/upload_image', json=data)

    print("Inserted log to database.")

def encode_base64(img):
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64

def process_warning(frame):
    tele_notification.send_message("Đã phát hiện đám cháy!")

    send_log_to_database(frame)

    print("Log sent to database")
    print("Warning sent to your phone")



connectDatabase()