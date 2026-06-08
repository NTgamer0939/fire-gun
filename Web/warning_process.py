import base64
import datetime
import cv2
# import tele_notification
import time
import connectDB
import requests
import os
import threading

cursor = None
conn = None

busy = False

def connectDatabase():
    global cursor, conn
    print("Connecting to database...")
    DB = connectDB.ConnectDB()
    cursor = DB.cursor
    conn = DB.conn
    print("Connected to database successfully!")

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

def query(command, val = None):
    global busy, cursor, conn
    error = 0
    while error < 3:
        while busy:
            time.sleep(0.1)
        busy = True
        try:
            if val is not None:
                cursor.execute(command, val)
                conn.commit()
            else:
                cursor.execute(command)
                conn.commit()
            time.sleep(0.1)
        except Exception as e:
            print(f"Error occurred while executing query ({error}): {e}")
            if e == "Lost connection to MySQL server during query":
                connectDatabase()
            error += 1
        finally:
            busy = False
            print(f"Executed query: {command} with val: {val}")
            if error >= 3:
                print("Failed to execute query after 3 attempts.")
                return None
            if cursor.with_rows == False:
                return cursor.lastrowid
            elif cursor.with_rows:
                return cursor.fetchall()
            print("while busy: ", busy, cursor.with_rows, cursor.lastrowid)

def request_to_host(package, data):
    API_KEY = "010818064018thilamthidang"
    url = f"http://logforfiregun.click/api/{API_KEY}/{package}"
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Request successful")
        else:
            print(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred while sending request: {e}")

def send_log_to_database(img):

    dateTime = get_current_time()

    sql = "INSERT INTO log (datetime, image) VALUES (%s, %s)"
    val = (f"{dateTime['year']}-{dateTime['month']}-{dateTime['day']} {dateTime['hour']}:{dateTime['minute']}:{dateTime['second']}", int(time.time()))

    id_row = query(sql, val)

    os.makedirs("images", exist_ok=True)
    image_path = os.path.join("images", f"{id_row}.jpg")
    cv2.imwrite(image_path, img)

    with open(image_path, "rb") as f:
        image = f.read()

    data = {
        "id_row": id_row,
        "image": image
    }

    request_to_host("image", data)

    print("Inserted log to database.")

def encode_base64(img):
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64

def process_warning(frame):
    # tele_notification.send_message("Đã phát hiện đám cháy!")

    send_log_to_database(frame)

    print("Log sent to database")
    print("Warning sent to your phone")



connectDatabase()