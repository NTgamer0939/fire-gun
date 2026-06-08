import time
import flask
from flask import jsonify
import threading
from flask_socketio import SocketIO
from flask_cors import CORS
from connectDB import ConnectDB
import os
import base64

app = flask.Flask(__name__)

CORS(app, supports_credentials=True)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    cors_credentials=True,
    transports=['polling'],
    ping_timeout=60,
    ping_interval=25,
    async_mode='threading'
)

app.secret_key = "kjfjf kjgdgfxfg uts drgscvjbh -uoihug"

API_KEY = "010818064018thilamthidang"

stream_last_time = 0
is_stream = False
is_main_running = False
user_watching = []

cursor = None
conn = None

busy = False

def connectDB():
    print("Connecting to database...")
    global cursor, conn
    DB = ConnectDB()
    cursor = DB.cursor
    conn = DB.conn
    print("Connected to database successfully!")

def defaultSetting():
    global is_stream, user_watching
    if len(user_watching) <= 0:
        is_stream = False

def query(command, val = None):
    global busy
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
                connectDB()
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

def send_log_to_client(currentPage=1, clientID=None):
    if clientID is None:
        return
    print("Sending log to client...")
    data = []
    sql = f"SELECT * FROM `log` ORDER BY `id` DESC LIMIT {(int(currentPage) - 1) * 5}, 5"
    logs = query(sql) or []
    data = convert_datetime(logs)
    print(f"Data to send: {data}")
    socketio.emit('new_log', data, to=clientID)
    print("Sent log to client")

def create_content_export_file():
    sql = "SELECT `datetime` FROM log ORDER BY `id` DESC"
    logs = query(sql)
    content = "Hệ thống Fire-gun - Dự án thi Sáng tạo thanh thiếu niên nhi đồng TP.Cần Thơ năm 2025-2026.\n"
    content += "****************************************************************************************** \n\n"
    content += "Dữ liệu được xuất vào lúc: " + time.strftime("%d-%m-%Y %H:%M:%S") + "\n\n"
    content += "Danh sách các lần cảnh báo:\n"
    for log in logs:
        datetime = log[1].strftime("%d-%m-%Y %H:%M:%S")
        content += f"{datetime}\n"
    return content
# def stream():
#     global stream_last_time, is_stream
#     print("Starting stream...")
#     while is_stream:
#         print("Streaming...")
#         if time.time() - stream_last_time >= 0.4:
#             stream_last_time = time.time()
            
#             frame_original = frame_queue.get()
#             frame_encode = encode_base64(frame_original)
            
#             try:
#                 socketio.emit("stream_frame", frame_encode)
#             except Exception as e:
#                 print(f"Error occurred while emitting stream frame: {e}")

# def putFrameToQueue(frame):
#     global frame_queue, is_stream
#     if is_stream:
#         frame_queue.put(frame)
            # try:
            #     frame_queue.put(frame)
            # except queue.Full:
            #     frame_queue.get_nowait()
            #     frame_queue.put(frame)

def convert_datetime(logs):
    data = []
    for log in logs:
        datetime = log[1].strftime("%d-%m-%Y %H:%M:%S")
        image_name = int(log[0])
        try:
            with open(f"images/{image_name}.jpg", "rb") as f:
                image_data = f.read()
                image_data = base64.b64encode(image_data).decode('utf-8')
            log_data = {
                "datetime": datetime,
                "image": image_data
            }
            data.append(log_data)
        except Exception as e:
            print(f"Error occurred while reading image for log {log[0]}: {e}")
    return data



# Connect to database
connectDB()



# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     return response

@app.route("/")
def home():
    return flask.render_template("index.html")

@socketio.on("connect")
def handle_connect():
    print("***********************************************************")
    sid = flask.request.sid
    socketio.emit("getID", sid, to=sid)
    print(f"[ONLINE] Client connected with sid: {sid}")
    threading.Thread(target=send_log_to_client, kwargs={"clientID": sid}).start()
    return True

@socketio.on("disconnect")
def handle_disconnect():
    print("***********************************************************")
    global is_stream, user_watching
    print(f"[OFFLINE] Client {flask.request.sid} disconnected!")
    if flask.request.sid in user_watching:
        user_watching.remove(flask.request.sid)
        if len(user_watching) <= 0:
            is_stream = False
    defaultSetting()

@app.route("/export", methods=["POST"])
def export_data():
    print(f"Logs exported by {flask.request.form.get('clientID')}")
    return create_content_export_file()

@app.route("/start_stream", methods=["POST"])
def start_stream():
    global is_stream, user_watching
    clientID = flask.request.form.get("clientID")
    user_watching.append(clientID)
    if not is_stream:
        is_stream = True
        # stream_thread = threading.Thread(target=stream)
        # stream_thread.start()
        return jsonify({"message": "Stream started"})

@app.route("/stop_stream", methods=["POST"])
def stop_stream():
    global is_stream, user_watching
    clientID = flask.request.form.get("clientID")
    user_watching.remove(clientID)
    if len(user_watching) <= 0:
        is_stream = False
    send_log_to_client(clientID=clientID)
    return jsonify({"message": "Stream stopped"})

@app.route("/change_page", methods=["POST"])
def change_page():
    currentPage = flask.request.form.get("page")
    clientID = flask.request.form.get("clientID")
    print(f"Changing page to {currentPage} for client {clientID}")
    try:
        currentPage = int(currentPage)
    except (TypeError, ValueError):
        currentPage = 1
    send_log_to_client(currentPage, clientID)
    return jsonify({"message": "Page changed", "page": currentPage})

@app.route("/api/<string:A>/detected", methods=["POST"])
def api_endpoint(A):
    if A != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401
    pass

@app.route("/api/<string:A>/getimage", methods=["POST"])
def api_getimage(A):
    if A != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401

    requested_data = flask.request.data

    if requested_data['image'] is None:
        return jsonify({"error": "No image provided"}), 400

    os.makedirs("images", exist_ok=True)
    image_path = os.path.join("images", f"{requested_data['id_row']}.jpg")
    with open(image_path, "wb") as f:
        f.write(requested_data['image'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)