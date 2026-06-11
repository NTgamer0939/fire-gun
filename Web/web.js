const express = require('express');
const mysql = require('mysql');
const { Server } = require('socket.io');
const http = require('http');
const fs = require('fs')
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

app.set('views', './templates');
app.use(express.static('./static'));
app.use(express.static('./images'));
app.use(express.json({ limit: '10mb', parameterLimit: 50000}));
app.use(express.urlencoded({limit: '10mb', parameterLimit: 50000, extended: true }));

let connection;
let camId = '';
let userInStream = new Array;

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
    if (clientId != 'refresh') {
        io.to(clientId).emit('new_log', data);
    } else{
        io.to('logs-room').emit('new_log', data);
    }
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

function saveImage(imgName, image) {
    const fileName = imgName + `.jpg`;
    const buffer = Buffer.from(image, 'base64');

    fs.writeFileSync('./images/' + fileName, buffer);
    console.log("Saved image with name: ", fileName);
}

function streamManager(method=null, socketId) {
    if (method == null) return;

    if (method == 'join'){
        userInStream.push(socketId);
    }
    if (method == 'leave') {
        for (let i = 0; i < userInStream.length; i++) {
            if (userInStream[i] == socketId) {
                userInStream.splice(i, 1);
            }
        }
    }

    if (userInStream.length == 0) {
        if (camId != '') {
            io.to(camId).emit('stop');
        }
    }
    else {
        io.to(camId).emit('start');
    }
    console.log(userInStream);
}

app.get('/', (req, res) => {
    return res.render('index.ejs');
});

io.use((socket, next) => {
    if (socket.handshake.auth.token == "010818064018thilamthidang") {
        camId = socket.id;
        console.log('[CAMERA] Camera is ready!');
        next();
    }
    next();
});

io.on('connection', (socket) => {
    console.log("[CONNECTION] Connected to client: " + socket.id);
    sendToClient(1, socket.id);
    socket.join('logs-room');

    socket.on('join_stream', () => {
        socket.leave('logs-room');
        socket.join('stream-room');
        streamManager('join', socket.id);
        console.log('[STREAM] Client join to stream room: ' + socket.id);
    })
    
    socket.on('leave_stream', () => {
        socket.leave('stream-room');
        socket.join('logs-room');
        streamManager('leave', socket.id);
        console.log('[!STREAM] Client leave to stream room: ' + socket.id);
        sendToClient(1, socket.id);
    })
    
    socket.on('frame_from_camera', (frame) =>{
        if (socket.id != camId) {
            return;
        }
        io.to('stream-room').emit('stream', frame);
    })
    
    socket.on('disconnect', () => {
        if (socket.id == camId) {
            camId = '';
            console.log('[CAMERA] Camera is offline!');
            return;
        }
        streamManager('leave', socket.id);
        console.log("[!CONNECTION] Client disconnected: " + socket.id);
    });
});

io.on('error', (err) => {
    console.error('[ERROR] Socket.IO error:', err);
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

app.post('/change_page', async (req, res) => {
    currentPage = req.body.page;

    const query = `SELECT * FROM \`log\` ORDER BY \`id\` DESC LIMIT ${(parseInt(currentPage) - 1) * 5}, 5`;
    var data = await executeQuery(query);

    data = dataProcesser(data);
    res.json(data);

    console.log(`An user change to page ${currentPage}`);
})

app.post('/upload_image', (req, res) => {
    console.log(req.body)
    const imgName = req.body.fileName;
    const image = req.body.image;

    saveImage(imgName, image);

    sendToClient(1, 'refresh');

    console.log("[DANGER] An warning image saved in storge");
})

function keepDatabaseAlive() {
    setInterval(() => {
        if (connection) {
            connection.query('SELECT 1');
        }
    }, 30000);
}

// Turn on server
server.listen(PORT, () => {
    console.log(`Server đang chạy ở port ${PORT} rồi nha!`);
    connectDatabase();
    keepDatabaseAlive();
});