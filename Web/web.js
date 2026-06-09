const express = require('express');
const mysql = require('mysql');
const { Server } = require('socket.io');
const http = require('http');
const PORT = 3000;

const app = express();
const server = http.createServer(app);
const io = new Server(
    server, 
    {
        cors: {
            origin: "*"
        }
    }
);

app.use(express.static('json'));
app.use(express.urlencoded({ extended: true }));
app.use(express.static('./static'));
app.use(express.static('./images'));
app.set('views', './templates');

let connection;

// const connection = mysql.createConnection({
//     host: "localhost",
//     user: "root",
//     password: "",
//     database: "fire_gun"
// });
const mysqlConfig = {
    host: "103.18.6.92",
    user: "n4y7190ti8ne_connectbysystemfiregun",
    password: "@92iYnHU3mM@ptq",
    database: "n4y7190ti8ne_fire_gun"
};

async function connectDatabase() {
    await new Promise((resolve, reject) => {
        connection = mysql.createConnection(mysqlConfig);
        connection.connect((err) => {
            if (err) {
                console.error('Error connecting to database:', err);
                return;
            }
            console.log('Connected to database!');
            resolve();
        });
    });
    connection.on('error', (err) => {
        console.error('Database error:', err);
        connectDatabase()
    });
};

function dataProcesser(logs) {
    var data = []

    logs.forEach((item) => {
        let date = convertDate(item.datetime);

        let imagePath = String(item.image) + '.jpg';

        data.push({datetime: date, imagePath: imagePath});
    });
    return data;
}

async function sendToClient(currentPage=1, clientId) {
    if (clientId === null || clientId === undefined) {
        return;
    }
    const query = `SELECT * FROM \`log\` ORDER BY \`id\` DESC LIMIT 0, 5`;
    var data = await executeQuery(query);
    data = dataProcesser(data);
    io.to(clientId).emit('new_log', data);
}

async function executeQuery(query) {
    return await new Promise((resolve, reject) => {
        connection.query(query, (err, results) => {
            if (err) {
                reject(err);
            } else {
                resolve(results);
            }
        });
    }).catch((err) => {
        console.error('Error executing query:', err);
    });
}

function convertDate(data) {
    let date = new Date(data);
    let day = String(date.getDate())
    let month = String(date.getMonth() + 1)
    let year = date.getFullYear();
    let hours = String(date.getHours()).padStart(2, '0');
    let minutes = String(date.getMinutes()).padStart(2, '0');
    let seconds = String(date.getSeconds()).padStart(2, '0');
    return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
}

app.get('/', (req, res) => {
    return res.render('index.ejs');
});

io.on('connection', (socket) => {
    console.log("[NEW CONNECTION] Connected to client: " + socket.id);
    sendToClient(1, socket.id);
    return {message: "Connected!"};
});
io.on('disconnect', (socket) => {
    console.log("[DISCONNECTED] Client disconnected: " + socket.id);
});

io.on('error', (err) => {
    console.error('[ERROR] Socket.IO error:', err);
});

app.post("/start_stream", () => {
    console.log("[STREAM] Client requested to start stream");
});

app.post("/stop_stream", () => {
    console.log("[STREAM] Client requested to stop stream");
});

app.post('/export', async (req, res) => {
    var content = "Hệ thống Fire-gun - Dự án thi Sáng tạo thanh thiếu niên nhi đồng TP.Cần Thơ năm 2025-2026.\n"
    content += "****************************************************************************************** \n\n"
    content += "Dữ liệu được xuất vào lúc: " + convertDate(Date()) + "\n\n"
    content += "Danh sách các lần cảnh báo:\n"

    var logs = await executeQuery('SELECT * FROM `log`')
    logs.forEach((item) => {
        let date = convertDate(item.datetime);
        content += date + "\n"
    });

    res.json(content);
})

app.post("/change_page", async (req, res) => {
    currentPage = req.body.page;

    const query = `SELECT * FROM \`log\` ORDER BY \`id\` DESC LIMIT ${(parseInt(currentPage) - 1) * 5}, 5`;
    var data = await executeQuery(query);

    data = dataProcesser(data);
    res.json(data);

    console.log(`An user change to page ${currentPage}`);
})

function keepDatabaseAlive() {
    setInterval(() => {
        if (connection) {
            connection.query('SELECT 1');
        }
    }, 30000);
}

// Bật server
server.listen(PORT, () => {
    console.log(`Server đang chạy ở port ${PORT} rồi nha!`);
    connectDatabase();
    keepDatabaseAlive();
});