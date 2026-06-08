import mysql.connector

class ConnectDB:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="103.18.6.92",
            user="n4y7190ti8ne_connectbysystemfiregun",
            password="@92iYnHU3mM@ptq",
            database="n4y7190ti8ne_fire_gun"
        )
        self.cursor = self.conn.cursor()